# Homework 3: Release Management — GitHub Tags, Jenkins CI/CD & Docker Swarm Rollback

**Student Name:** Ven KemLeap  
**Class:** Master - Cloud Computing & DevOps  
**Repository:** [kemleapven/cicd-homework-03](https://github.com/kemleapven/cicd-homework-03)  
**Docker Hub:** [kemleapx20/cicd-web-app](https://hub.docker.com/r/kemleapx20/cicd-web-app)  
**Amazon ECR:** `154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app`  
**Production Live URL:** [http://52.90.56.1:5000](http://52.90.56.1:5000)  

---

## 1. Project Overview & Architecture

While Homework 2 deployed every commit automatically, **Homework 3 implements production Release Discipline**:
- **Tag-Triggered CI/CD:** Ordinary branch pushes do not deploy. Production releases trigger **strictly on Git tags** following Semantic Versioning (`vMAJOR.MINOR.PATCH`).
- **Immutable Container Versioning:** Images pushed to **Amazon ECR** and **Docker Hub** are tagged with the exact Git tag (e.g., `cicd-web-app:v1.0.0`, `:v1.1.0`, `:v1.2.0`) and never overwritten.
- **Parameterized Jenkins Pipeline:** Supports on-demand actions via build parameters:
  - `ACTION`: `build_and_deploy` | `rollback` | `build_and_push` | `deploy_only`
  - `VERSION`: Target semantic release version (e.g. `v1.0.0`, `v1.1.0`, `v1.2.0`)
- **Zero-Downtime Swarm Rollback:** Instant one-click rollback that redeploys an existing image from registry directly to the Docker Swarm cluster on AWS EC2 **without rebuilding**, maintaining 100% uptime through rolling updates.

```text
 ┌──────────────────┐    Push Git Tag (v1.0.0)    ┌─────────────────────┐
 │   Developer PC   │ ──────────────────────────► │  GitHub Repository  │
 └──────────────────┘                             └──────────┬──────────┘
                                                             │ Tag Webhook (ref: refs/tags/v*)
                                                             ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │                           Jenkins CI/CD                              │
 │  Parameters: ACTION (build_and_deploy | rollback), VERSION           │
 │  1. Resolve Version & Action (Auto-detects Git Tag)                  │
 │  2. Lint & Unit Test (pytest test_app.py)   [Skipped on Rollback]    │
 │  3. Docker Build (Tagged with Git Tag)       [Skipped on Rollback]    │
 │  4. Push Immutable Tag to Amazon ECR         [Skipped on Rollback]    │
 │  5. Rolling Update on AWS EC2 Docker Swarm Cluster                   │
 └───────────────────┬──────────────────────────────────┬───────────────┘
                     │ Push Immutable Image             │ Rolling Update
                     ▼                                  ▼
          ┌─────────────────────┐             ┌───────────────────┐
          │     Amazon ECR      │ ── Pull ──> │   AWS EC2 Swarm   │
          │  :v1.0.0, :v1.1.0   │             │ 1 Manager + 1 Wkr │
          │  :v1.2.0 (Retained) │             │  3 Replicas (LB)  │
          └─────────────────────┘             └───────────────────┘
```

---

## 2. Repository Structure

```text
Homework_Kemleap_03/
├── .dockerignore                 # Excludes caches and local files from image
├── .gitignore                    # Git exclusions
├── Dockerfile                    # Production multi-worker Gunicorn container
├── Jenkinsfile                   # Parameterized Declarative Pipeline with Rollback
├── README.md                     # Comprehensive documentation & verification
├── RELEASING.md                  # Release management & versioning guide
├── app.py                        # Python Flask microservice with dynamic versioning
├── docker-compose.yml            # Local development Compose file
├── docker-stack.yml              # Swarm stack specification with rolling update
├── requirements.txt              # Application dependencies
└── test_app.py                   # Automated unit test suite
```

---

## 3. Release Lifecycle & Semantic Versioning

All releases adhere strictly to **SemVer 2.0.0** (`vMAJOR.MINOR.PATCH`). Full details are documented in [`RELEASING.md`](RELEASING.md).

```bash
# 1. Ensure tests pass
pytest -v test_app.py

# 2. Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release on AWS EC2 Docker Swarm"

# 3. Push tag to GitHub
git push origin v1.0.0
```

---

## 4. Rollback Engineering & Verification

If a regression is identified in `v1.2.0`, an operator rolls back to `v1.1.0`:
1. Run Jenkins with `ACTION = rollback` and `VERSION = v1.1.0`.
2. Jenkins executes a rolling update against the Docker Swarm service on EC2:
   ```bash
   sudo docker service update \
     --image 154560315950.dkr.ecr.us-east-1.amazonaws.com/cicd-web-app:v1.1.0 \
     --env-add APP_VERSION=v1.1.0 \
     --update-order start-first \
     --update-parallelism 1 \
     cicd-homework_web
   ```
3. Swarm spawns the `v1.1.0` container replica and verifies its health before terminating `v1.2.0`, resulting in **zero downtime**.


---

## 5. Verification & Submission Deliverables

| # | Deliverable Title | Screenshot File | Description |
|---|---|---|---|
| 1 | **GitHub Releases & Tags** | [screenshots/01 - GitHub Releases and Tags.jpg](screenshots/01%20-%20GitHub%20Releases%20and%20Tags.jpg) | Releases 1.0.0, 1.1.0, 1.2.0 published with release notes |
| 2 | **Amazon ECR Repository** | [screenshots/02 - Amazon ECR Repository.jpg](screenshots/02%20-%20Amazon%20ECR%20Repository.jpg) | Immutable images retained across all 3 versions |
| 3 | **Jenkins Pipeline Execution** | [screenshots/03 - Jenkins Pipeline View.jpg](screenshots/03%20-%20Jenkins%20Pipeline%20View.jpg) | Stage view for Builds #3, #4, #5 (Releases) and #6 (Rollback) |
| 4 | **Parameterized Rollback Action** | [screenshots/04 - Jenkins Rollback Action.jpg](screenshots/04%20-%20Jenkins%20Rollback%20Action.jpg) | Jenkins parameters ACTION=rollback & VERSION=v1.1.0 |
| 5 | **Live Health Telemetry** | [screenshots/05 - Live Application Health v1.1.0.jpg](screenshots/05%20-%20Live%20Application%20Health%20v1.1.0.jpg) | JSON /health telemetry confirming active rollback to 1.1.0 |
| 6 | **Live Web Application Dashboard** | [screenshots/06 - Live Web Dashboard v1.1.0.jpg](screenshots/06%20-%20Live%20Web%20Dashboard%20v1.1.0.jpg) | Production UI at http://52.90.56.1:5000 for Ven KemLeap |
| 7 | **Docker Swarm Cluster Status** | [screenshots/07 - EC2 Swarm Nodes and Replicas.jpg](screenshots/07%20-%20EC2%20Swarm%20Nodes%20and%20Replicas.jpg) | Active cluster nodes and 3 tasks running 1.1.0 |
| 8 | **Release Documentation** | [screenshots/08 - RELEASING md Documentation.jpg](screenshots/08%20-%20RELEASING%20md%20Documentation.jpg) | Complete release discipline documented in RELEASING.md |

Official Word Report: [Homework_3_Report_Ven_KemLeap.docx](Homework_3_Report_Ven_KemLeap.docx)
