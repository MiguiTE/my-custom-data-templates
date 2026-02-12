variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
  default     = "europe-west1"
}

variable "process_name" {
  description = "Nombre del proceso para el nombrado de recursos"
  type        = string
}