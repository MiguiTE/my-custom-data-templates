output "sa_private_key" {
  value     = google_service_account_key.function_key.private_key
  sensitive = true
}

output "function_sa_email" {
  value = google_service_account.function_sa.email
}