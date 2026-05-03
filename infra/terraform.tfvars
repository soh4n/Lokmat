# ============================================================================
# LokMat — Terraform tfvars for production
# ============================================================================
# Per GEMINI.md: tag all GCP resources with project, env, team labels.
# This file should NOT contain secrets — those go in Secret Manager.

project_id = "lokmat-495121"
region     = "us-central1"
db_tier    = "db-f1-micro"

labels = {
  project = "promptwars"
  app     = "lokmat"
  env     = "prod"
  team    = "lokmat"
}
