# ============================================================================
# LokMat — Terraform Variables
# ============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "lokmat-495121"
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"  # Cost-effective for hackathon
}

variable "labels" {
  description = "Labels applied to all resources (per GEMINI.md cost guardrails)"
  type        = map(string)
  default = {
    project = "promptwars"
    app     = "lokmat"
    env     = "prod"
    team    = "lokmat"
  }
}
