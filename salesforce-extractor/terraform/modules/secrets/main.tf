resource "google_secret_manager_secret" "user_secret" {
  secret_id = "gc-sm-${var.process_name}-user"
  replication {
    user_managed {
		replicas {
			location = var.region
		}
	}
  }
}

resource "google_secret_manager_secret" "ssh_key_secret" {
  secret_id = "gc-sm-${var.process_name}-sshkey"
  replication {
    user_managed {
		replicas {
			location = var.region
		}
	}
  }
}

resource "google_secret_manager_secret" "cf_sa_key" {
  secret_id = "gc-sm-${var.process_name}-sa_key"
  replication {
    user_managed {
		replicas {
			location = var.region
		}
	}
  }
}


resource "google_service_account" "function_sa" {
  account_id   = "sa-${var.process_name}"
  display_name = "Service Account para el proceso ${var.process_name}"
}

resource "google_service_account_key" "function_key" {
  service_account_id = google_service_account.function_sa.name
}

resource "google_secret_manager_secret_version" "ssh_key_version" {
  secret      = google_secret_manager_secret.cf_sa_key.id
  secret_data = base64decode(google_service_account_key.function_key.private_key)
}

resource "google_secret_manager_secret_iam_member" "access_secret" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.cf_sa_key.id

  role   = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.function_sa.email}"
}
