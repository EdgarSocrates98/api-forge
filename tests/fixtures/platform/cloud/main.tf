terraform {
  required_version = ">= 1.5.0"
}

variable "project_id" {
  type = string
}

resource "google_cloud_run_v2_service" "api" {
  name     = "orders-api"
  location = "us-central1"
}
