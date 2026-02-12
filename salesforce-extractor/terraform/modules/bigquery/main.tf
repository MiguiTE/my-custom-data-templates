resource "google_bigquery_dataset" "dataset" {
  dataset_id = "bq_ing_${var.process_name}"
  location   = var.region
}