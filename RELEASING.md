# Release Management Guide (RELEASING.md)

**Student Name:** Ven KemLeap  
**Class:** Master - Cloud Computing & DevOps  
**Repository:** [kemleapven/cicd-homework-03](https://github.com/kemleapven/cicd-homework-03)  
**Target Registry:** Amazon ECR (`154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app`)  
**Deployment Target:** AWS EC2 Docker Swarm Cluster (Manager: `52.90.56.1`)  

---

## 1. Semantic Versioning Strategy

This repository enforces **Semantic Versioning (SemVer 2.0.0)** for all production releases. Version tags must follow the format:

```text
v<MAJOR>.<MINOR>.<PATCH>
```

### Format Definition:
- **`MAJOR` (e.g., `v2.0.0`):** Incompatible API changes, major architectural redesigns, or breaking framework migrations.
- **`MINOR` (e.g., `v1.1.0`):** New backward-compatible functionality, feature enhancements, and new telemetry endpoints.
- **`PATCH` (e.g., `v1.1.1`):** Backward-compatible bug fixes, performance optimizations, and security patches.

---

## 2. Release Lifecycle & Tag-Only CI/CD Trigger

Unlike continuous deployment where every commit triggers a production release, **Homework 3 enforces Release Discipline**:
1. Ordinary commits to branches (`main`, `feature/*`) run local tests and linting without triggering production deployment.
2. A production release is cut **strictly by pushing an annotated Git tag** (e.g., `git push origin v1.0.0`).
3. GitHub sends a `create` / `push` tag webhook to the Jenkins automation server.
4. Jenkins parses the Git tag, builds an immutable Docker image tagged with the exact release string, pushes it to **Amazon ECR**, and executes a zero-downtime rolling update on the Docker Swarm cluster.

---

## 3. How to Cut a New Release

To release a new version to production, follow these steps:

### Step 1: Ensure Main is Clean & Tested
```bash
git checkout main
git pull origin main
pytest test_app.py
```

### Step 2: Create an Annotated Git Tag
Always use **annotated tags** (`-a`) with a descriptive release message:

```bash
# Example for Release v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release on AWS EC2 Docker Swarm"

# Example for Release v1.1.0
git tag -a v1.1.0 -m "Release v1.1.0: Added automated health monitoring and telemetry"

# Example for Release v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0: Experimental UI theme and high-concurrency caching"
```

### Step 3: Push the Tag to GitHub
```bash
git push origin <TAG_NAME>
# e.g.:
git push origin v1.0.0
```

Once pushed, GitHub's webhook triggers the Jenkins pipeline job automatically.

---

## 4. Rollback Procedure (Emergency Rollback)

If a release (e.g., `v1.2.0`) introduces an unexpected bug or regression in production, an operator can immediately roll back to a previously verified release (e.g., `v1.1.0`) **without rebuilding code or pushing new commits**.

### Rollback via Jenkins Parameterized Job:
1. Open Jenkins Dashboard -> Job **`cicd-homework-03`**.
2. Click **Build with Parameters** in the left menu.
3. Select parameters:
   - **`ACTION`**: `rollback`
   - **`VERSION`**: Target stable tag (e.g., `v1.1.0`)
4. Click **Build**.

### What Happens During Rollback:
1. Jenkins verifies that the image `154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app:v1.1.0` already exists in Amazon ECR.
2. Jenkins issues a rolling update command to Docker Swarm:
   ```bash
   docker service update \
     --image 154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app:v1.1.0 \
     --with-registry-auth \
     cicd-homework_web
   ```
3. Docker Swarm updates one container replica at a time with `order: start-first`.
4. The service stays **100% online with zero downtime**, and the prior stable version is restored in seconds!

---

## 5. Release History & Audit Log

| Release Tag | Release Date | Highlights & Notes | Status |
|:-----------:|:------------:|--------------------|:------:|
| **`v1.0.0`** | 2026-10-24 | Initial production release on AWS EC2 Docker Swarm cluster | Deployed |
| **`v1.1.0`** | 2026-10-24 | Enhanced telemetry, health-probe metrics & Swarm rolling config | Deployed (Stable Target) |
| **`v1.2.0`** | 2026-10-24 | Experimental UI theme and high-concurrency worker threading | Rolled Back |
