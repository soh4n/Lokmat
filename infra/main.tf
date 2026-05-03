# ============================================================================
# LokMat — Terraform Infrastructure as Code
# ============================================================================
# Per GEMINI.md: all GCP resources managed via Terraform
# Project: lokmat-495121
# Region:  us-central1
# ============================================================================

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "lokmat-495121-tfstate"
    prefix = "terraform/state"
  }
}

# ============================================================================
# Provider
# ============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ============================================================================
# Enable Required APIs
# ============================================================================

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "storage.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com"
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ============================================================================
# Service Account
# ============================================================================

resource "google_service_account" "lokmat_api" {
  account_id   = "lokmat-api"
  display_name = "LokMat API Service Account"
  description  = "Service account for LokMat Cloud Run API"
}

# IAM bindings for the service account
resource "google_project_iam_member" "api_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/storage.objectAdmin",
    "roles/redis.editor",
    "roles/firebase.sdkAdminServiceAgent",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.lokmat_api.email}"
}

# ============================================================================
# Artifact Registry
# ============================================================================

resource "google_artifact_registry_repository" "lokmat" {
  location      = var.region
  repository_id = "lokmat"
  format        = "DOCKER"
  description   = "LokMat container images"

  labels = var.labels

  depends_on = [google_project_service.apis]
}

# ============================================================================
# Cloud SQL — PostgreSQL
# ============================================================================

resource "google_sql_database_instance" "lokmat" {
  name             = "lokmat-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
    }

    maintenance_window {
      day  = 7  # Sunday
      hour = 4
    }

    user_labels = var.labels
  }

  deletion_protection = false

  depends_on = [
    google_project_service.apis,
    google_service_networking_connection.private_vpc_connection,
  ]
}

resource "google_sql_database" "lokmat" {
  name     = "lokmat"
  instance = google_sql_database_instance.lokmat.name
}

resource "google_sql_user" "lokmat" {
  name     = "lokmat_user"
  instance = google_sql_database_instance.lokmat.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = false
}

# ============================================================================
# VPC Network (required for private Cloud SQL + Redis)
# ============================================================================

resource "google_compute_network" "vpc" {
  name                    = "lokmat-vpc"
  auto_create_subnetworks = true
}

resource "google_compute_global_address" "private_ip_range" {
  name          = "lokmat-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# VPC Connector for Cloud Run → private network access
resource "google_vpc_access_connector" "connector" {
  name          = "lokmat-connector"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  min_instances = 2
  max_instances = 3

  depends_on = [google_project_service.apis]
}

# ============================================================================
# Redis — Memorystore
# ============================================================================

resource "google_redis_instance" "lokmat" {
  name               = "lokmat-cache"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  redis_version      = "REDIS_7_0"
  authorized_network = google_compute_network.vpc.id

  labels = var.labels

  depends_on = [google_project_service.apis]
}

# ============================================================================
# Cloud Storage — GCS
# ============================================================================

resource "google_storage_bucket" "uploads" {
  name          = "${var.project_id}-uploads"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7  # Auto-delete temp objects after 7 days
    }
  }

  labels = var.labels
}

# ============================================================================
# Secret Manager — Store secrets securely
# ============================================================================

resource "google_secret_manager_secret" "db_password" {
  secret_id = "lokmat-db-password"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "lokmat-gemini-api-key"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "lokmat-jwt-secret"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# ============================================================================
# Cloud Run — API Service
# ============================================================================

resource "google_cloud_run_v2_service" "api" {
  name     = "lokmat-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.lokmat_api.email

    scaling {
      min_instance_count = 1
      max_instance_count = 20
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/lokmat/api:latest"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      # Environment variables
      env {
        name  = "APP_NAME"
        value = "LokMat API"
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "FIREBASE_AUTH_ENABLED"
        value = "true"
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql+asyncpg://lokmat_user:${random_password.db_password.result}@${google_sql_database_instance.lokmat.private_ip_address}:5432/lokmat"
      }

      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.lokmat.host}:${google_redis_instance.lokmat.port}/0"
      }

      env {
        name  = "GCS_BUCKET"
        value = google_storage_bucket.uploads.name
      }

      env {
        name  = "CORS_ORIGINS"
        value = "[\"https://lokmat.web.app\",\"https://lokmat-495121.web.app\"]"
      }

      # Secrets from Secret Manager
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds = 30
      }
    }
  }

  labels = var.labels

  depends_on = [
    google_project_service.apis,
    google_artifact_registry_repository.lokmat,
    google_sql_database.lokmat,
    google_redis_instance.lokmat,
    google_secret_manager_secret_version.db_password,
    google_secret_manager_secret_version.jwt_secret,
  ]
}

# Allow unauthenticated access to Cloud Run (public API)
resource "google_cloud_run_v2_service_iam_member" "public" {
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ============================================================================
# Cloud Monitoring — Budget Alert
# ============================================================================

resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "LokMat API High Latency"

  conditions {
    display_name = "Cloud Run request latency > 5s"
    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"lokmat-api\" AND metric.type = \"run.googleapis.com/request_latencies\""
      comparison      = "COMPARISON_GT"
      threshold_value = 5000
      duration        = "60s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_95"
      }
    }
  }

  combiner = "OR"

  notification_channels = []

  user_labels = var.labels
}
