
resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:sa-${var.process_name}@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_object" "object" {
  name   = "templates/cf.zip"
  bucket = "gc-tfstate-${var.project_id}"
  source = "../../templates/cf/cf.zip"
}

resource "google_cloudfunctions2_function" "function" {
  name        = "gc-cf-${var.project_id}-${var.process_name}"
  location    = var.region
  description = "Función para el proceso ${var.process_name}"

  build_config {
    runtime     = "python311"
    entry_point = "hello_world" # Set the entry point 
    source {
      storage_source {
        bucket = "gc-tfstate-${var.project_id}"
        object = "templates/cf.zip"
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  lifecycle {
    ignore_changes = [
      build_config[0].source[0].storage_source[0].bucket,
      build_config[0].source[0].storage_source[0].object
    ]
  }
}


resource "google_cloud_scheduler_job" "invocator" {
  name      = "gc-sc-${var.process_name}-invocator"
  schedule  = "0 1 * * *"
  time_zone = "Europe/Madrid"
  region    = "europe-west1"
  http_target {
    http_method = "POST"
    uri         = "${google_cloudfunctions2_function.function.service_config[0].uri}/invoke"
    oidc_token {
      audience              = "${google_cloudfunctions2_function.function.service_config[0].uri}/"
      service_account_email = "sa-${var.process_name}@${var.project_id}.iam.gserviceaccount.com"
    }
  }
}


