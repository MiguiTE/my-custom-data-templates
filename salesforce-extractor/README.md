# Salesforce accelerator template

## Folder structure

```
├───README.md
│
├───function
│   │   main.py
│   │
│   └───src
│           bigquery.py
│           project_info.py
│           requirements.txt
│           salesforce.py
│           schema_gcs.py
│           secret_manager.py
│           storage.py
│
└───terraform
    │   main.tf
    │   outputs.tf
    │   README.md
    │   terraform.tfvars
    │   variables.tf
    │
    ├───backends
    │       account.tfbackend
    │       opportunity.tfbackend
    │
    ├───bootstrap
    │       backend-creator.sh
    │
    └───modules
        ├───bigquery
        │       main.tf
        │       outputs.tf
        │       variables.tf
        │
        ├───functions
        │       main.tf
        │       outputs.tf
        │       variables.tf
        │
        ├───secrets
        │       main.tf
        │       outputs.tf
        │       variables.tf
        │
        └───storage
                main.tf
                variables.tf
```

## Prerequisites
Configure, if needed, new backend file in `./terraform/backends` with preffix and bucket and initialize terraform

```
terraform init -backend-config=backends/{filename}.tfbackend -reconfigure
```

## Workflow
```
terrafrom plan

terrafrom apply

terraform destroy //opt
```