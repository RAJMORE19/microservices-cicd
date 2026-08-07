import os
import json
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import redis.asyncio as redis


app = FastAPI(title="Cart Service")


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cart_user:cart_password@postgres:5432/cart_db"
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379"
)


db_pool = None
redis_client = None


class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int


class CartRequest(BaseModel):
    user_id: str
    items: List[CartItem]


@app.on_event("startup")
async def startup():

    global db_pool
    global redis_client

    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20
    )

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS carts (
                user_id VARCHAR(100) PRIMARY KEY,
                items JSONB NOT NULL
            )
            """
        )

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )


@app.on_event("shutdown")
async def shutdown():

    if db_pool:
        await db_pool.close()

    if redis_client:
        await redis_client.close()


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.post("/cart")
async def create_cart(cart: CartRequest):

    data = json.dumps(
        [item.model_dump() for item in cart.items]
    )

    async with db_pool.acquire() as conn:

        await conn.execute(
            """
            INSERT INTO carts(user_id, items)
            VALUES($1,$2)
            ON CONFLICT(user_id)
            DO UPDATE SET items=$2
            """,
            cart.user_id,
            data
        )

    await redis_client.set(
        f"cart:{cart.user_id}",
        data,
        ex=300
    )

    return {
        "message": "cart saved",
        "user_id": cart.user_id
    }


@app.get("/cart/{user_id}")
async def get_cart(user_id: str):

    cached = await redis_client.get(
        f"cart:{user_id}"
    )

    if cached:

        return {
            "user_id": user_id,
            "items": json.loads(cached),
            "source": "redis"
        }


    async with db_pool.acquire() as conn:

        result = await conn.fetchrow(
            """
            SELECT items
            FROM carts
            WHERE user_id=$1
            """,
            user_id
        )


    if not result:

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )


    await redis_client.set(
        f"cart:{user_id}",
        result["items"],
        ex=300
    )


    return {
        "user_id": user_id,
        "items": json.loads(result["items"]),
        "source": "postgres"
    }



@app.put("/cart/{user_id}")
async def update_cart(
    user_id: str,
    cart: CartRequest
):

    if user_id != cart.user_id:

        raise HTTPException(
            status_code=400,
            detail="user_id mismatch"
        )


    data = json.dumps(
        [item.model_dump() for item in cart.items]
    )


    async with db_pool.acquire() as conn:

        updated = await conn.execute(
            """
            UPDATE carts
            SET items=$1
            WHERE user_id=$2
            """,
            data,
            user_id
        )


    if updated == "UPDATE 0":

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )


    await redis_client.set(
        f"cart:{user_id}",
        data,
        ex=300
    )


    return {
        "message": "cart updated"
    }



@app.delete("/cart/{user_id}")
async def delete_cart(user_id: str):

    async with db_pool.acquire() as conn:

        deleted = await conn.execute(
            """
            DELETE FROM carts
            WHERE user_id=$1
            """,
            user_id
        )


    if deleted == "DELETE 0":

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )


    await redis_client.delete(
        f"cart:{user_id}"
    )


    return {
        "message": "cart deleted"
    }
