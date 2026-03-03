resource "google_storage_bucket" "archive_bucket" {
  name          = "${var.project_id}-archive"
  location      = var.region
  storage_class = "STANDARD"

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
    condition {
      age                   = 30
      matches_storage_class = ["STANDARD"]
    }
  }
}

resource "google_storage_bucket" "errors_bucket" {
  name          = "${var.project_id}-errors"
  location      = var.region
  storage_class = "ARCHIVE"
}
