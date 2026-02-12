import os
from enum import Enum

class PROJECT_INFO(Enum):
	PROD_PROJECT_ID = "PROD-PROJECT-ID"

	PROJECT_ID = os.environ.get("PROJECTID", "TEST-PRROJECT-ID")
	PROJECT_NUMBER = os.environ.get("PROJECTNUMBER", "TEST-PROJECT-NUMBER")

	IS_DEV = PROD_PROJECT_ID != PROJECT_ID

class PROCESS_INFO(Enum):
	PROCESS_NAME = os.environ.get("PROCESSNAME", "PROCESS_NAME").lower()
	SFTP_HOST = os.environ.get("SFTPHOST", "host")
	SFTP_PORT = int(os.environ.get("SFTPPORT", "2222"))
	SFTP_FOLDER = os.environ.get("SFTPFOLDER", "")