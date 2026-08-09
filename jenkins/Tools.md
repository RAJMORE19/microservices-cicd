**SonarQube kya karta hai?**

Simple language mein:

> **SonarQube developer ke code ki quality aur security check karta hai.**

Jenkins pipeline mein generally:

**Developer → GitHub → Jenkins → SonarQube → Docker Build → Trivy → ECR → Deploy**

SonarQube mainly ye cheezein check karta hai:

* 🐛 **Bugs** — code mein potential errors
* 🔐 **Security vulnerabilities** — insecure coding
* 🧹 **Code Smells** — bad/unclean code
* 📊 **Code Quality** — maintainability
* 🧪 **Test Coverage** — kitna code tests se covered hai
* 📋 **Quality Gate** — code deployment ke liye acceptable hai ya nahi

### Real example

Developer ne code push kiya:

```python
password = "admin123"
```

SonarQube bol sakta hai:

> ❌ Security issue detected

Ya code unnecessarily complicated hai:

> ⚠️ Code Smell detected

Jenkins mein **Quality Gate fail** ho sakta hai, aur pipeline aage deploy nahi karegi.

### Interview mein 10 sec answer

> **"SonarQube is a static code analysis tool used in CI/CD to detect bugs, vulnerabilities, code smells, and measure code quality and test coverage. We use its Quality Gate to prevent poor-quality code from moving further in the pipeline."**
