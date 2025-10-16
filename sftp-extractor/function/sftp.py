import paramiko
from enum import Enum
import tempfile
import io
import logging

from secret_manager import get_sftp_credentials
from credentials.project_info import PROCESS_INFO

class SFTP(Enum):
	HOST = PROCESS_INFO.SFTP_HOST.value
	PORT = PROCESS_INFO.SFTP_PORT.value
class SFTP_FOLDERS(Enum):
	FOLDER = PROCESS_INFO.SFTP_FOLDER.value

SFTP_CLIENT: paramiko.SFTPClient = None
SSH_CLIENT: paramiko.SSHClient = None

def write_temp_file(private_key: str):
	"""
	Escribe la clave privada en un archivo temporal y devuelve la ruta al archivo.
	"""
	with tempfile.NamedTemporaryFile(delete=False, mode='w') as keyfile:
		keyfile.write(private_key)
		return keyfile.name

def get_sftp_connector() -> tuple[paramiko.SSHClient, paramiko.SFTPClient]:
	"""
	Crea y devuelve un cliente SFTP autenticado usando paramiko.

	Returns:
		SFTPClient: Objeto SFTP autenticado.
	"""
	global SSH_CLIENT, SFTP_CLIENT
	
	if SFTP_CLIENT != None and SSH_CLIENT != None:
		return SSH_CLIENT, SFTP_CLIENT

	credentials = get_sftp_credentials()
	sftp_user = credentials["user"]
	sftp_password = credentials["password"]

	keyfile_path = write_temp_file(sftp_password)

	ssh_client = paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 

	logging.info("About to connect to SFTP", extra={"json_fields": {
		"hostname":	SFTP.HOST.value,
		"port": SFTP.PORT.value
	}})

	ssh_client.connect(
		hostname=SFTP.HOST.value,
		port=SFTP.PORT.value,
		username=sftp_user,
		key_filename=keyfile_path
	)

	sftp_client = ssh_client.open_sftp()

	if SFTP_CLIENT == None or SSH_CLIENT == None:
		SFTP_CLIENT = sftp_client
		SSH_CLIENT = ssh_client

	return ssh_client, sftp_client


def get_files(folder: str):
	"""
	Obtiene los archivos de una carpeta SFTP modificados desde una fecha dada.

	Args:
		sftp_client (SFTPClient): Cliente SFTP autenticado.
		folder (str): Nombre de la carpeta configurada en SFTP_FOLDERS.
		date (datetime): Fecha mínima de modificación.

	Returns:
		list: Lista de diccionarios con información y contenido de los archivos encontrados.
	"""
	_, sftp_client = get_sftp_connector()

	csv_files = []

	for file in sftp_client.listdir_attr(f"./{folder}"):
		if file.filename.endswith(".csv"):
			remote_path = f"./{folder}/{file.filename}"
			with sftp_client.open(remote_path, 'r') as f:
				file_content = f.read()
				csv_files.append({
					"file_name": file.filename.lower(),
					"path": remote_path,
					"data": io.StringIO(file_content.decode('utf-8'))
				})

	return csv_files

def empty_folder(folder: str) -> None:
	"""
	Elimina los archivos de una carpeta en el servidor SFTP.

	Args:
		sftp (paramiko.SFTPClient): Cliente SFTP autenticado.
		file_names (List[str]): Lista de nombres de archivos a eliminar.
	"""
	_, sftp_client = get_sftp_connector()

	for file in sftp_client.listdir_attr(f"./{folder}"):
		try:
			if file.filename.endswith(".csv"):
				remote_path = f"./{folder}/{file.filename}"
				sftp_client.remove(remote_path)
		except Exception as e:
			logging.error(f"Error al eliminar archivo desde SFTP", extra={"json_fields": {
				"file_name": file.filename,
				"error": e
			}})

def delete_file(file_name: str):
	"""
	Elimina un archivo en el servidor SFTP.

	Args:
		file_name (str): Nombre del archivo a eliminar.
	"""
	_, sftp_client = get_sftp_connector()

	try:
		remote_path = f"./{file_name}"
		sftp_client.remove(remote_path)
	except Exception as e:
		logging.error(f"Error al eliminar archivo desde SFTP", extra={"json_fields": {
			"file_name": file_name,
			"error": e
		}})


def close_connection():
	"""
	Cierra la conexión SFTP y SSH.
	"""
	global SSH_CLIENT, SFTP_CLIENT
	
	if SFTP_CLIENT != None and SSH_CLIENT != None:
		SFTP_CLIENT.close()
		SSH_CLIENT.close()

		SFTP_CLIENT = None
		SSH_CLIENT = None