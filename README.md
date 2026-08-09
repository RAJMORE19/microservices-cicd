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

# Install and Configure Docker and compose

| Command | Why | Result |
|---------|-----|--------|
| `sudo apt update && sudo apt install -y docker.io` | Install Docker | Docker installed |
| `sudo usermod -aG docker jenkins` | Allow Jenkins to run Docker commands | Jenkins added to Docker group |
| `sudo systemctl restart docker && sudo systemctl restart jenkins` | Apply changes | Docker and Jenkins services restarted |

# Installaction : 
     1️⃣ SonarQube → 2️⃣ OWASP Dependency-Check → 3️⃣ Trivy
     
=========================================================================================================================

### SonarQube Installation Steps (Working Guide)

SonarQube ko Docker Container mein apne server par successfully install karne ke complete aur working steps yeh hain:

### Step 1: Ek Directory Banayein aur Move Karein

Terminal mein yeh commands run karein:

```bash
mkdir sonarqube
cd sonarqube

```

### Step 2: docker-compose.yml File Banayein

Ek nayi file create karein:

```bash
nano docker-compose.yml

```

Aur isme yeh configuration paste kar dein:

```yaml
version: "3.8"
services:
  sonarqube:
    image: sonarqube:community
    container_name: sonarqube
    restart: unless-stopped
    ports:
      - "9000:9000"
    environment:
      - SONAR_JDBC_URL=jdbc:postgresql://db:5432/sonar
      - SONAR_JDBC_USERNAME=sonar
      - SONAR_JDBC_PASSWORD=sonar_password
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_logs:/opt/sonarqube/logs
      - sonarqube_extensions:/opt/sonarqube/extensions
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=sonar
      - POSTGRES_PASSWORD=sonar_password
      - POSTGRES_DB=sonar
    volumes:
      - postgresql_data:/var/lib/postgresql/data

volumes:
  sonarqube_data:
  sonarqube_logs:
  sonarqube_extensions:
  postgresql_data:

```

*(Save karne ke liye `Ctrl + O`, phir `Enter`, aur exit ke liye `Ctrl + X` dabayein).*

### Step 3: Linux System Limits Set Karein (Zaroori hai)

SonarQube ke liye virtual memory limit badhayein taaki container crash na ho:

```bash
sudo sysctl -w vm.max_map_count=524288

```

### Step 4: Start Karein

Containers ko background mein run karne ke liye yeh command chalayein:

```bash
docker compose up -d

```

### Step 5: Access Karein

Apne browser mein jayein: `http://<Aapke_Server_Ki_IP>:9000`

* **Default Username:** `admin`
* **Default Password:** `admin`
*(Pehli baar login karne par naya password set kar lijiye).*
=========================================================================================================================

Haan, ise **wahi setup karna sabse best hai jahan aapka Jenkins server chal raha hai** (ya Jenkins agent par), kyunki yeh CI/CD pipeline ke andar run hota hai jab aapka code build hota hai.

Jenkins par OWASP Dependency-Check ko set karne ke **3 aasan steps**:

---

### Step 1: Jenkins mein Plugin Install Karein

1. Apne **Jenkins Dashboard** par jayein.
2. **Manage Jenkins** -> **Plugins** -> **Available plugins** par click karein.
3. Search box mein type karein: `Dependency-Check`.
4. **Dependency-Check Plugin** ko select karke **Install** kar dein (Restart ki zaroorat pade toh restart kar lein).

### Step 2: Jenkins mein Tool Configure Karein

1. **Manage Jenkins** -> **Tools** (ya *Global Tool Configuration*) par jayein.
2. Neeche scroll karke **Dependency-Check installations** dhoondein.
3. **Add Dependency-Check** par click karein:
* **Name:** `dependency-check` (ya kuch bhi naam dein).
* **Install automatically** checkbox select karein (version latest chun lein).


4. **Save** par click kar dein.

### Step 3: Apni Pipeline (`Jenkinsfile`) mein Stage Add Karein

Ab apne project ki pipeline file mein ye stage add kar dein taaki build ke waqt code ki dependencies scan ho sakein:

```groovy
stage('Security Scan - OWASP') {
    steps {
        // Agar aapne tool ka naam 'dependency-check' rakha hai
        dependencyCheck additionalArguments: '--scan ./', odcInstallation: 'dependency-check'
        dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
    }
}

```

Bas! Ab jab bhi aapka Jenkins job chalega, ye automatically saari libraries/dependencies ko scan karke security report generate kar dega.
=========================================================================================================================

Yes bro. GitHub notes mein **sirf working method** rakho; failed `apt-key` method mat rakho.

## Trivy Installation — Ubuntu 24.10

### 1. Remove old/failed repository

```bash
sudo rm -f /etc/apt/sources.list.d/trivy.list
```

### 2. Create APT keyring directory

```bash
sudo mkdir -p /etc/apt/keyrings
```

### 3. Add Trivy GPG key

```bash
wget -qO- https://aquasecurity.github.io/trivy-repo/deb/public.key \
| sudo gpg --dearmor -o /etc/apt/keyrings/trivy.gpg
```

### 4. Add Trivy repository

```bash
echo "deb [signed-by=/etc/apt/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" \
| sudo tee /etc/apt/sources.list.d/trivy.list
```

### 5. Update APT

```bash
sudo apt update
```

### 6. Install Trivy

```bash
sudo apt install trivy -y
```

### 7. Verify installation

```bash
trivy --version
```

Expected:

```text
Version: 0.71.2
```

### 🧠 Why this method?

```text
GPG Key
   ↓
APT trusts Trivy Repository
   ↓
apt update
   ↓
apt install trivy
   ↓
Trivy ✅
```

**GitHub note:** `apt-key` wala failed method **mat likhna**. Above **keyring-based method is your working installation procedure**.

=========================================================================================================================

