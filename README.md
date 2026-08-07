# microservices-cicd
Enterprise-grade microservices CI/CD pipeline using Jenkins, Docker, Kubernetes, and cloud-native DevOps practices — from developer code commit to production deployment.
<img width="2752" height="1536" alt="microservices-cicd" src="https://github.com/user-attachments/assets/b8cfc497-dd93-4028-8c12-de7454df414c" />


1. AWS Resources & Cost-Effective Sizing
To run this complete architecture smoothly while keeping costs minimal (ideal for learning/testing):

Amazon EC2 (for Jenkins & Kubernetes Control Plane/Worker):

Size: t3.medium (2 vCPUs, 4 GB RAM).

Why: t3.micro or t3.small will run out of memory instantly when running Jenkins, Docker builds, and a local Kubernetes cluster (like Minikube or K3s) together. t3.medium is the sweet spot for free-tier-adjacent / low-budget testing.

Amazon EKS (Alternative Managed Kubernetes):

If using managed EKS, use 1 node of t3.medium, but note that EKS control plane charges hourly, so a single EC2 instance running K3s/Minikube is cheaper.

Storage (EBS):

Size: 30 GB gp3 root volume.

Why: Docker images, build caches, and logs take up space quickly. 30 GB is the AWS Free Tier limit for gp3 and prevents "disk full" pipeline crashes.
