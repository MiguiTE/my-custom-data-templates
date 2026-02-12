# Para trabajar con Ventas
terraform init -backend-config=backends/ventas.tfbackend -reconfigure

# Para cambiar a RRHH
terraform init -backend-config=backends/rrhh.tfbackend -reconfigure