# ============================================================================
# LokMat — Terraform Outputs
# ============================================================================

output "cloud_run_url" {
  description = "URL of the deployed Cloud Run API service"
  value       = google_cloud_run_v2_service.api.uri
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.lokmat.connection_name
}

output "cloud_sql_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.lokmat.private_ip_address
}

output "redis_host" {
  description = "Memorystore Redis host"
  value       = google_redis_instance.lokmat.host
}

output "redis_port" {
  description = "Memorystore Redis port"
  value       = google_redis_instance.lokmat.port
}

output "gcs_bucket" {
  description = "GCS bucket name for uploads"
  value       = google_storage_bucket.uploads.name
}

output "artifact_registry_url" {
  description = "Artifact Registry URL for container images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.lokmat.repository_id}"
}

output "service_account_email" {
  description = "Service account email for the API"
  value       = google_service_account.lokmat_api.email
}

output "database_url" {
  description = "Full database URL for the API (sensitive)"
  value       = "postgresql+asyncpg://lokmat_user:${random_password.db_password.result}@${google_sql_database_instance.lokmat.private_ip_address}:5432/lokmat"
  sensitive   = true
}
