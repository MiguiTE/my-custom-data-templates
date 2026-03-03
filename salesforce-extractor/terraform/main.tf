provider "google" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
  }
}

module "secrets" {
  source       = "./modules/secrets"
  project_id   = var.project_id
  process_name = var.process_name
  region       = var.region
}

module "bigquery" {
  source       = "./modules/bigquery"
  project_id   = var.project_id
  process_name = var.process_name
  region       = var.region
}

module "cloud_function" {
  source       = "./modules/functions"
  project_id   = var.project_id
  process_name = var.process_name
  region       = var.region
}


module "storage" {
  source       = "./modules/storage"
  project_id   = var.project_id
  process_name = var.process_name
  region       = var.region
}
