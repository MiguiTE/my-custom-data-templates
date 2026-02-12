provider "google" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
  }
}

module "secrets" {
  source            = "./modules/security"
  process_name      = var.process_name
  sa_key_to_store   = module.cloud_function.sa_private_key
  function_sa_email = module.cloud_function.function_sa_email
}

module "bigquery" {
  source       = "./modules/bigquery"
  project_id   = var.project_id
  process_name = var.process_name
  region       = var.region
}

module "cloud_function" {
  source                = "./modules/cloud_function"
  project_id            = var.project_id
  process_name          = var.process_name
  region                = var.region
  source_bucket         = "mi-bucket-codigo"
  source_object         = "src/function.zip"
  service_account_email = "sa-deployer@${var.project_id}.iam.gserviceaccount.com"
}
