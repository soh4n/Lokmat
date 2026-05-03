# LokMat — Infrastructure as Code

## GCP Project: `lokmat-495121`

This directory contains Terraform configurations for provisioning all GCP resources.

## Resources Provisioned

| Resource | Service | Purpose |
|----------|---------|---------|
| `lokmat-api` | Cloud Run | Serverless API hosting |
| `lokmat-db` | Cloud SQL (PostgreSQL 16) | Persistent data storage |
| `lokmat-cache` | Memorystore (Redis 7) | Session cache, rate limiting |
| `lokmat-495121-uploads` | Cloud Storage | File uploads, voter slips |
| `lokmat` | Artifact Registry | Docker image repository |
| `lokmat-vpc` | VPC Network | Private networking |
| `lokmat-connector` | VPC Connector | Cloud Run → private network |
| `lokmat-*` | Secret Manager | API keys, DB password, JWT secret |
| `lokmat-api` | Service Account | IAM for Cloud Run |

## Quick Start

```bash
# 1. Authenticate
gcloud auth application-default login

# 2. Create Terraform state bucket (one-time)
gsutil mb -p lokmat-495121 -l us-central1 gs://lokmat-495121-tfstate

# 3. Initialize Terraform
cd infra
terraform init

# 4. Plan
terraform plan

# 5. Apply
terraform apply
```

## Prerequisites

1. [Terraform >= 1.5](https://www.terraform.io/downloads)
2. [gcloud CLI](https://cloud.google.com/sdk/docs/install)
3. GCP project `lokmat-495121` with billing enabled
4. Owner or Editor role on the project

## Setting the Gemini API Key

After `terraform apply`, set the Gemini API key in Secret Manager:

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets versions add lokmat-gemini-api-key --data-file=-
```

## Cost Notes

- Cloud SQL: `db-f1-micro` tier (~$7.67/month)
- Redis: 1GB BASIC tier (~$35/month)
- Cloud Run: Pay-per-use, min 1 instance
- Total estimated: ~$50-80/month for hackathon period
