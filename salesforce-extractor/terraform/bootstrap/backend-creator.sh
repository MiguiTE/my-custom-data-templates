#!/bin/bash

#TODO: variables must be equal to variables defined in ./variables.tf
PROJECT_ID="tu-proyecto-id"
PROCESS_NAME="tu-proceso"
REGION="tu-region"
BUCKET_NAME="gc-tfstate-${PROJECT_ID}"

echo "🚀 Iniciando backend para el proceso: ${PROCESS_NAME}..."

if gsutil ls -b "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
    echo "✅ El bucket de estado ${BUCKET_NAME} ya existe."
else
    echo "📦 Creando bucket de estado ${BUCKET_NAME}..."
    
	gsutil mb -l ${REGION} "gs://${BUCKET_NAME}"
    gsutil versioning set on "gs://${BUCKET_NAME}"
    
	echo "✅ Bucket creado y versionado activado."
fi