
from credentials.project_info import PROJECT_INFO, PROCESS_INFO


import logging
import re
import pandas as pd
from enum import Enum
from datetime import datetime, timezone

from google.cloud import storage

class STORAGE(Enum):
	LANDING = f"{PROJECT_INFO.PROJECT_ID.value}-gcs-bucket-landing"
	ERRORS = f"{PROJECT_INFO.PROJECT_ID.value}-gcs-bucket-errores"
	ARCHIVE = f"{PROJECT_INFO.PROJECT_ID.value}-gcs-bucket-archivo"
	
	GCS_FOLDER = f"sftp_{PROCESS_INFO.PROCESS_NAME.value}"
	
	DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

	FILE_PATH_REGEX	 = r"^gs:\/\/(?P<bucket>[^\/]+)\/(?P<file_path>.*)"

NOW = datetime.now(timezone.utc)

def get_storage_client() -> storage.Client:
	"""
	Gets client for Google Cloud Storage.

	Returns
	-------
	storage.Client
	"""
	return storage.Client()

def upload_to_gcs(df: pd.DataFrame, key:str, fileName: str):
	"""
	Uploads dataframe to GCS landing bucket

	Parameters
	----------
	df : pd.Dataframe Dataframe data
	key : str folder name
	fileName : str file name

	Returns
	-------
	str Full gcs file path
	"""
	try:
		file_path = build_file_path(key, fileName)

		df.to_csv(file_path, index=False, encoding='utf-8', sep=",")
		
		return file_path
	except Exception as e:
		logging.error("Error uploading data to GCS", extra={"json_fields": {
			"key": fileName,
			"shape": df.shape,
			"error": e
		}})

		raise e
	
def build_file_path(key: str, fileName: str):
	date_folder = NOW.strftime(STORAGE.DATE_FORMAT.value)
		
	file_prefix = int(NOW.timestamp() * 1000)
	return f"gs://{STORAGE.LANDING.value}/{STORAGE.GCS_FOLDER.value}/{key}/{date_folder}/{file_prefix}__{fileName}.csv"

def add_system_columns(df: pd.DataFrame, gcs_file_path: str) -> pd.DataFrame:
	df["upload_date"] = NOW.strftime(STORAGE.DATE_FORMAT.value)
	df["gcs_path"] = gcs_file_path


def get_latest_uploaded_date(client: storage.Client, folder: str) -> datetime:
	bucket = client.bucket(STORAGE.LANDING.value)

	bucket.list_blobs(prefix=f"{STORAGE.GCS_FOLDER.value}/{folder}/")

def check_file_path(file_path: str):
	"""
    Valida y descompone una ruta de archivo de Google Cloud Storage (GCS).

    Parámetros
    ----------
    file_path : str Ruta completa al archivo en GCS (ejemplo: "gs://my-bucket/folder/file.csv").

    Retorna
    -------
    tuple (str, str)
        - old_bucket : nombre del bucket extraído.
        - path       : ruta relativa al archivo dentro del bucket.

    Excepciones
    -----------
    ValueError
        Se lanza si el `file_path` no cumple con el formato esperado.
    """
	match = re.match(STORAGE.FILE_PATH_REGEX.value, file_path)
	if not match:
		raise ValueError(f"Invalid file path: {file_path}")
	
	old_bucket = match.group("bucket")
	path = match.group("file_path")

	return old_bucket, path


def archive_file(file_path: str):
	"""
    Mueve un archivo de Google Cloud Storage (GCS) al bucket de archivo del proyecto.

    Parámetros
    ----------
    file_path : str Ruta completa al archivo en GCS (ejemplo: "gs://my-bucket/folder/file.csv").

    Retorna
    -------
    str
        Ruta GCS del archivo en el bucket de archivo

    Excepciones
    -----------
    ValueError
        Si el `file_path` no cumple con el formato esperado.
    google.api_core.exceptions.GoogleCloudError
        Si ocurre un error en la operación de copia o eliminación en GCS.
    """
	old_bucket, path = check_file_path(file_path)

	move_file(old_bucket, path, STORAGE.ARCHIVE.value, path)

	return f"gs://{STORAGE.ARCHIVE.value}/{path}"

def move_file_to_error(file_path: str):
	"""
    Mueve un archivo de Google Cloud Storage (GCS) al bucket de errores del proyecto.

    Parámetros
    ----------
    file_path : str Ruta completa al archivo en GCS (ejemplo: "gs://my-bucket/folder/file.csv").

    Retorna
    -------
    str
        Ruta GCS del archivo en el bucket de archivo

    Excepciones
    -----------
    ValueError
        Si el `file_path` no cumple con el formato esperado.
    google.api_core.exceptions.GoogleCloudError
        Si ocurre un error en la operación de copia o eliminación en GCS.
    """
	old_bucket, path = check_file_path(file_path)
	
	move_file(old_bucket, path, STORAGE.ERRORS.value, path)
	
	return f"gs://{STORAGE.ERRORS.value}/{path}"


def move_file(old_bucket: str, old_path: str, new_bucket:str, new_path: str):
	"""
    Mueve un objeto dentro de Google Cloud Storage de una ubicación a otra,
    incluso entre buckets diferentes.

    Parámetros
    ----------
    client : storage.Client Cliente autenticado de Google Cloud Storage.
    old_bucket : str Nombre del bucket de origen.
    old_path : str Ruta (key) del archivo en el bucket de origen.
    new_bucket : str Nombre del bucket de destino.
    new_path : str Ruta (key) en la que se almacenará el archivo en el bucket destino.

    Retorna
    -------
    storage.Blob
        Objeto Blob correspondiente al archivo en la nueva ubicación.

    Excepciones
    -----------
    google.api_core.exceptions.NotFound Si el archivo origen no existe.
    google.api_core.exceptions.Conflict Si ocurre un conflicto al copiar o borrar el blob.
    """
	logging.info("About to move file", extra={"json_fields": {
		"old_bucket": old_bucket,
		"old_path": old_path,
		"new_bucket": new_bucket,
		"new_path": new_path
	}})

	client = get_storage_client()

	original_bucket = client.bucket(old_bucket)
	dest_bucket = client.bucket(new_bucket)

	old_blob = original_bucket.blob(old_path)
	
	new_blob = original_bucket.copy_blob(old_blob, dest_bucket, new_path)

	old_blob.delete()

	return new_blob

