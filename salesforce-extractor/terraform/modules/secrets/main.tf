resource "google_secret_manager_secret" "user_secret" {
  secret_id = "gc-sm-${var.process_name}-user"
  replication {
    # automatic = true
  }
}

resource "google_secret_manager_secret" "ssh_key_secret" {
  secret_id = "gc-sm-${var.process_name}-sshkey"
  replication {
    # automatic = true
  }
}

resource "google_secret_manager_secret" "cf_sa_key" {
  secret_id = "gc-sm-${var.process_name}-sa_key"
  replication {
    # automatic = true
  }
}

resource "google_secret_manager_secret_version" "ssh_key_version" {
  secret      = google_secret_manager_secret.cf_sa_key.id
  secret_data = base64decode(var.sa_key_to_store)
}

resource "google_secret_manager_secret_iam_member" "access_secret" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.cf_sa_key.id
  
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.function_sa_email}"
}