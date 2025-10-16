import os
from enum import Enum

class PROJECT_INFO(Enum):
	PROD_PROJECT_ID = "gc-p-plataformadeldato-ingesta"

	PROJECT_ID = os.environ.get("PROJECTID", "gc-t-plataformadeldato-ingesta")
	PROJECT_NUMBER = os.environ.get("PROJECTNUMBER", "455912236365")

	IS_DEV = PROD_PROJECT_ID != PROJECT_ID

class PROCESS_INFO(Enum):
	PROCESS_NAME = os.environ.get("PROCESSNAME", "rrhh").lower()
	SFTP_HOST = os.environ.get("SFTPHOST", "host")
	SFTP_PORT = int(os.environ.get("SFTPPORT", "2222"))
	SFTP_FOLDER = os.environ.get("SFTPFOLDER", "")