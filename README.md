# Flask Application CI/CD for AWS EKS

This repository contains the **Python Flask application source code and GitLab CI/CD pipeline** used in my end-to-end AWS EKS GitOps project.

The pipeline tests the application, builds a Docker image, pushes it to **Amazon ECR**, and updates the Kubernetes image tag in the GitOps repository. **Argo CD** then deploys the new version to Amazon EKS.

## CI/CD Flow

```text
Developer Push
      |
      v
 GitLab CI/CD
      |
      +--> Pylint
      |
      +--> Pytest
      |
      v
 Docker Build
      |
      v
 Amazon ECR
      |
      v
Update ks8 GitOps Repository
      |
      v
    Argo CD
      |
      v
  Amazon EKS
```

## Pipeline

The GitLab pipeline contains three main stages:

- **Test** — runs Pylint and Pytest
- **Build** — builds the Docker image and pushes it to Amazon ECR
- **Deploy** — updates the image tag in the GitOps repository

AWS authentication is handled through **GitLab OIDC**, allowing the pipeline to assume an AWS IAM role without storing long-lived AWS access keys.

Development deployment is automated, while production deployment requires manual confirmation.

## Project Structure

```text
code_source_eks/
├── app/                 # Flask application
├── tests/               # Unit tests
├── Docker/              # Dockerfile
├── .gitlab-ci.yml       # CI/CD pipeline
├── .pylintrc            # Pylint configuration
├── requirements.txt     # Python dependencies
└── run.py               # Application entry point
```

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Docker
- GitLab CI/CD
- Pytest
- Pylint
- AWS IAM / OIDC
- Amazon ECR
- Kubernetes
- Argo CD

## Related Repositories

- [ks8](https://github.com/Odjeissi/ks8) — Kubernetes, GitOps, monitoring, and observability configuration
- [iac-eks](https://github.com/Odjeissi/iac-eks) — AWS infrastructure provisioned with Terraform

## What This Repository Demonstrates

This repository demonstrates an application delivery workflow where source code changes are automatically tested, containerized, pushed to a registry, and promoted through a GitOps-based deployment process to Amazon EKS.
