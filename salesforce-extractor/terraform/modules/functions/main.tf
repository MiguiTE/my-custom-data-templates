
resource "google_service_account" "function_sa" {
  account_id   = "sa-${var.process_name}"
  display_name = "Service Account para el proceso ${var.process_name}"
}

resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_cloudfunctions_function" "function" {
  name        = "gc-cf-${var.project_id}-${var.process_name}"
  description = "Función para el proceso ${var.process_name}"
  runtime     = "python311"

  available_memory_mb   = 256
#   source_archive_bucket = var.source_bucket
#   source_archive_object = var.source_object
  trigger_http          = true
  entry_point           = "main"
}


resource "google_cloud_scheduler_job" "invocator" {
  name     = "gc-sc-${var.process_name}-invocator"
  schedule = "0 1 * * *"
  region   = var.region

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.function.https_trigger_url
    oidc_token {
      service_account_email = google_service_account.function_sa.email
    }
  }
}


