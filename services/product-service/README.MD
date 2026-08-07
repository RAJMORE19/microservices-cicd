Read only then i will give you task



Act as a Principal DevOps Engineer with 20+ years of experience at Amazon, Netflix, and Google.

DO NOT teach theory.

Your goal is to build ONLY ONE Cart Microservice.

Ignore every other microservice.

I want the MINIMUM number of files while still following enterprise production standards.

Do NOT over-engineer the project.

\=================================================

Architecture

GitHub
→ Jenkins
→ Docker
→ Amazon ECR
→ Kubernetes (later)

For now ONLY Docker.

\=================================================

Technology

Backend: Python FastAPI

Database: PostgreSQL

Cache: Redis

Container: Docker

\=================================================

Containers (ONLY)

1. cart-service
2. postgres
3. redis

Nothing else.

\=================================================

Project Structure

cart-service/

├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .dockerignore
└── README.md

DO NOT create extra folders.

DO NOT create src/.

DO NOT create config/.

DO NOT create models/.

DO NOT create controllers/.

DO NOT create services/.

DO NOT create healthcheck.py.

DO NOT create Jenkinsfile.

Keep everything inside app.py until the project grows.

\=================================================

Dockerfile

Create a production-ready Dockerfile using

• python:3.12-slim
• non-root user
• optimized layers
• healthcheck
• small image
• production CMD

\=================================================

docker-compose.yml

Use ONLY ONE compose file.

Include

cart-service

postgres

redis

Use

restart: unless-stopped

depends\_on

healthcheck

named volume

bridge network

environment variables

\=================================================

Application

Generate a complete FastAPI Cart application inside app.py.

Include

GET /health

POST /cart

GET /cart/{user\_id}

PUT /cart/{user\_id}

DELETE /cart/{user\_id}

Store data in PostgreSQL.

Use Redis for caching.

\=================================================

requirements.txt

Generate only required packages.

\=================================================

README

Include

docker compose up -d --build

docker compose logs -f

docker compose down

\=================================================

IMPORTANT

Generate COMPLETE code.

Do NOT skip anything.

Do NOT use placeholders.

Every file must work immediately.

The final result must run successfully with only

docker compose up -d --build

and later be easily deployable to Jenkins, ECR, and Kubernetes without major changes.



I’ll keep the implementation intentionally small: one FastAPI application file, three containers, PostgreSQL persistence, Redis caching, Docker-ready, and no extra application layers.

Project:

```
cart-service/

├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .dockerignore
└── README.md

```

---

## `app.py`

```
import os
import json
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cartuser:cartpassword@postgres:5432/cartdb"
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379"
)


db_pool = None
redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client

    db_pool = await asyncpg.create_pool(DATABASE_URL)

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS carts (
                user_id VARCHAR(100) PRIMARY KEY,
                items JSONB NOT NULL DEFAULT '[]'
            )
            """
        )

    yield

    await db_pool.close()
    await redis_client.close()


app = FastAPI(
    title="Cart Service",
    version="1.0.0",
    lifespan=lifespan
)


class CartRequest(BaseModel):
    items: list


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.post("/cart")
async def create_cart(cart: CartRequest, user_id: str):
    async with db_pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT user_id FROM carts WHERE user_id=$1",
            user_id
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Cart already exists"
            )

        await conn.execute(
            """
            INSERT INTO carts(user_id, items)
            VALUES($1, $2)
            """,
            user_id,
            json.dumps(cart.items)
        )

    await redis_client.delete(f"cart:{user_id}")

    return {
        "message": "cart created",
        "user_id": user_id,
        "items": cart.items
    }


@app.get("/cart/{user_id}")
async def get_cart(user_id: str):

    cached = await redis_client.get(f"cart:{user_id}")

    if cached:
        return {
            "user_id": user_id,
            "items": json.loads(cached),
            "source": "redis"
        }

    async with db_pool.acquire() as conn:
        cart = await conn.fetchrow(
            """
            SELECT items
            FROM carts
            WHERE user_id=$1
            """,
            user_id
        )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    items = json.loads(cart["items"])

    await redis_client.set(
        f"cart:{user_id}",
        json.dumps(items),
        ex=300
    )

    return {
        "user_id": user_id,
        "items": items,
        "source": "postgres"
    }


@app.put("/cart/{user_id}")
async def update_cart(
    user_id: str,
    cart: CartRequest
):

    async with db_pool.acquire() as conn:

        result = await conn.execute(
            """
            UPDATE carts
            SET items=$1
            WHERE user_id=$2
            """,
            json.dumps(cart.items),
            user_id
        )

    if result == "UPDATE 0":
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    await redis_client.delete(f"cart:{user_id}")

    return {
        "message": "cart updated",
        "user_id": user_id,
        "items": cart.items
    }


@app.delete("/cart/{user_id}")
async def delete_cart(user_id: str):

    async with db_pool.acquire() as conn:

        result = await conn.execute(
            """
            DELETE FROM carts
            WHERE user_id=$1
            """,
            user_id
        )

    if result == "DELETE 0":
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    await redis_client.delete(f"cart:{user_id}")

    return {
        "message": "cart deleted",
        "user_id": user_id
    }

```

---

## `requirements.txt`

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
asyncpg==0.30.0
redis==5.2.1
pydantic==2.10.5

```

---

## `Dockerfile`

```
FROM python:3.12-slim

WORKDIR /app

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD [
    "uvicorn",
    "app:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
    "--workers",
    "2"
]

```

---

## `docker-compose.yml`

```
services:

  cart-service:
    build:
      context: .

    container_name: cart-service

    restart: unless-stopped

    ports:
      - "8000:8000"

    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}

    depends_on:

      postgres:
        condition: service_healthy

      redis:
        condition: service_healthy

    networks:
      - cart-network

    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
        ]
      interval: 30s
      timeout: 5s
      retries: 3


  postgres:

    image: postgres:16-alpine

    container_name: postgres

    restart: unless-stopped

    environment:

      POSTGRES_USER: ${POSTGRES_USER}

      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

      POSTGRES_DB: ${POSTGRES_DB}

    volumes:

      - postgres-data:/var/lib/postgresql/data

    networks:

      - cart-network

    healthcheck:

      test:
        [
          "CMD-SHELL",
          "pg_isready -U ${POSTGRES_USER}"
        ]

      interval: 10s

      timeout: 5s

      retries: 5


  redis:

    image: redis:7-alpine

    container_name: redis

    restart: unless-stopped

    networks:

      - cart-network

    healthcheck:

      test:
        [
          "CMD",
          "redis-cli",
          "ping"
        ]

      interval: 10s

      timeout: 5s

      retries: 5


volumes:

  postgres-data:


networks:

  cart-network:

    driver: bridge

```

---

## `.env`

```
POSTGRES_USER=cartuser
POSTGRES_PASSWORD=cartpassword
POSTGRES_DB=cartdb

DATABASE_URL=postgresql://cartuser:cartpassword@postgres:5432/cartdb

REDIS_URL=redis://redis:6379

```

---

## `.dockerignore`

```
__pycache__
*.pyc
*.pyo
*.pyd

.env

.git
.gitignore

Dockerfile
docker-compose.yml

*.log

```

---

## `README.md`

````
# Cart Service

FastAPI Cart Microservice using:

- FastAPI
- PostgreSQL
- Redis
- Docker Compose


## Run

Build and start containers:

```bash
docker compose up -d --build

````

## Logs

View application logs:

```
docker compose logs -f

```

## Stop

Stop and remove containers:

```
docker compose down

```

## API

### Health

GET

```
/health

```

### Create Cart

POST

```
/cart?user_id=123

```

Body:

```
{
  "items": [
    {
      "product_id": "101",
      "quantity": 2
    }
  ]
}

```

### Get Cart

GET

```
/cart/123

```

### Update Cart

PUT

```
/cart/123

```

### Delete Cart

DELETE

```
/cart/123

```

## Containers

- cart-service
- postgres
- redis

## Future Deployment

The same container image can later be pushed to Amazon ECR and deployed to Kubernetes.

````

---

Run:

```bash
docker compose up -d --build

````

This creates only:

```
cart-service
postgres
redis

```

with:

- FastAPI production server
- non-root container user
- persistent PostgreSQL volume
- Redis cache
- health checks
- bridge networking
- environment-based configuration

No additional application structure is required until the service actually grows.
