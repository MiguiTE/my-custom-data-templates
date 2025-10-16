
import logging

from typing import TypedDict
from enum import Enum

from google.cloud import secretmanager

from credentials.project_info import PROJECT_INFO, PROCESS_INFO

class SECRETS(Enum):
	USER = f"sftp-{PROCESS_INFO.PROCESS_NAME.value}-user"
	PASSWORD = f"sftp-{PROCESS_INFO.PROCESS_NAME.value}-sshkey"
class Credentials(TypedDict):
    user: str
    password: str

def get_sftp_credentials() -> Credentials:
	"""
	Obtiene las credenciales de conexión al servidor SFTP desde Secret Manager.

	Returns:
		Credentials: Un diccionario con las credenciales necesarias para conectarse al SFTP, con las claves:
			- "user": nombre de usuario SFTP.
			- "password": clave privada asociada al usuario.

	Raises:
		KeyError: Si las claves "user" o "password" no están presentes en el JSON recuperado.
		json.JSONDecodeError: Si el contenido del secreto no es un JSON válido.
		Exception: Cualquier excepción derivada de `get_secret_value`.
	"""
	user = get_secret_value(SECRETS.USER.value)
	password = get_secret_value(SECRETS.PASSWORD.value)

	return {
		"user": user,
		"password": password
	}

def get_secret_value(secret_id: str) -> str:
	"""
    Recupera el valor de un secreto almacenado en Google Secret Manager.

    Accede a la última versión del secreto especificado y devuelve su valor decodificado en UTF-8.

    Args:
        secret_id (str): Nombre o identificador del secreto en Secret Manager.

    Returns:
        str: Valor del secreto como cadena de texto.

    Raises:
        google.api_core.exceptions.GoogleAPICallError: Si ocurre un error al acceder al Secret Manager.
        ValueError: Si el secreto no tiene contenido válido.
    """
	try:
		client = secretmanager.SecretManagerServiceClient()

		request = {
			"name": f"projects/{PROJECT_INFO.PROJECT_NUMBER.value}/secrets/{secret_id}/versions/latest"
		}

		response = client.access_secret_version(request)

		secret_value = response.payload.data.decode("UTF-8")

		return secret_value
	except Exception as e:
		logging.error("Error getting secret value", extra={"json_fields": {
			"secret_id": secret_id,
			"error": e
		}})

		raise e