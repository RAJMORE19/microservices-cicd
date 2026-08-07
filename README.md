# microservices-cicd
Enterprise-grade microservices CI/CD pipeline using Jenkins, Docker, Kubernetes, and cloud-native DevOps practices — from developer code commit to production deployment.
<img width="2752" height="1536" alt="microservices-cicd" src="https://github.com/user-attachments/assets/b8cfc497-dd93-4028-8c12-de7454df414c" />

# 1. AWS Resources & Cost-Effective Sizing

- **EC2 Instance:** `t2.large` (2 vCPU, 8 GB RAM)
- **Storage:** `30 GB` EBS (gp3)
- **Operating System:** Ubuntu Server 24.04 LTS
- **Security Group:**
  - `22` (SSH)
  - `8080` (Jenkins Web UI)

---

# Jenkins Setup

| Command | Why | Result |
|---------|-----|--------|
| `sudo apt update` | Update package index | Latest package information |
| `sudo apt install fontconfig openjdk-21-jre -y` | Install Java (Jenkins dependency) | Java installed |
| `java -version` | Verify Java installation | Java version displayed |
| `sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key` | Add Jenkins GPG key | Repository trusted |
| `echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \| sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null` | Add Jenkins repository | Repository configured |
| `sudo apt update` | Refresh package list | Jenkins package available |
| `sudo apt install jenkins -y` | Install Jenkins | Jenkins installed |
| `sudo systemctl status jenkins` | Verify Jenkins service | `active (running)` |
| `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` | Get initial unlock password | Initial admin password displayed |

# Install and Configure Docker

| Command | Why | Result |
|---------|-----|--------|
| `sudo apt update && sudo apt install -y docker.io` | Install Docker | Docker installed |
| `sudo usermod -aG docker jenkins` | Allow Jenkins to run Docker commands | Jenkins added to Docker group |
| `sudo systemctl restart docker && sudo systemctl restart jenkins` | Apply changes | Docker and Jenkins services restarted |


