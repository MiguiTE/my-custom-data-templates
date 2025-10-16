import functions_framework
from flask import jsonify
from functions_framework import HTTPFunction
import logging
import traceback
import pandas as pd
import google.cloud.logging

from sftp import SFTP_FOLDERS, get_files, delete_file, close_connection
from storage import upload_to_gcs, archive_file, move_file_to_error, add_system_columns, build_file_path
from bigquery import upload_to_big_query, check_columns

TABLES = [folder.value for folder in SFTP_FOLDERS]

client = google.cloud.logging.Client()
client.setup_logging()

@functions_framework.http
def main(request: HTTPFunction):
	logging.info("Start sftp extraction")
	for key in TABLES:
		try:
			logging.info("About to get sftp files", extra={"json_fields": {
				"key": key
			}})
			
			try:
				files = get_files(key)
			except Exception as e:
				logging.error("Error getting files from sftp", extra={"json_fields": {
					"error": str(e),
					"stacktrace": "".join(traceback.format_exception(type(e), e, e.__traceback__)),
					"key": key
				}})

				return jsonify({
					"error": "Error getting files from SFTP",
					"message": f"No se pudieron obtener los ficheros de la carpeta {key}: {str(e)}"
				}), 502

				
			logging.info("Data gotten from sftp files", extra={"json_fields": {
				"key": key, 
				"files": list(map(lambda x: {"file_name": x["file_name"], "path": x["path"]}, files))
			}})

			if len(files) == 0:
				logging.info("No files to process", extra={"json_fields": {
					"key": key
				}})
			
			for file_info in files:
				path = None
				
				try:
					logging.info("About to process sftp file", extra={"json_fields": {
						"key": key, 
						"file_name": file_info["file_name"], 
						"remote_path": file_info["path"]
					}})

					df = pd.read_csv(file_info["data"], sep=";")

					landing_path = build_file_path(key, file_info["file_name"])

					add_system_columns(df, landing_path)

					df = check_columns(df, file_info["file_name"])
					
					logging.info("About to upload sftp file to GCS", extra={"json_fields": {
						"key": key, 
						"file_name": file_info["file_name"], 
						"remote_path": file_info["path"],
						"shape": df.shape
					}})

					path = upload_to_gcs(df, key, file_info["file_name"])
					
					logging.info("About to upload sftp file to BQ", extra={"json_fields": {
						"key": key, 
						"file_name": file_info["file_name"], 
						"remote_path": file_info["path"],
						"gcs_path": path,
						"shape": df.shape
					}})
					
					upload_to_big_query(path, df, file_info["file_name"])

					logging.info("Dataframe uploaded for sftp table", extra={"json_fields": {
						"key": key, 
						"shape": df.shape, 
						"gcs_path": path,
						"remote_path": path
					}})
					
					logging.info("About to move sftp file to archive bucket", extra={"json_fields": {
						"key": key, 
						"file_name": file_info["file_name"], 
						"remote_path": file_info["path"],
						"gcs_path": path,
						"shape": df.shape
					}})

					archive_path = archive_file(path)

					logging.info("SFTP file moved to archive bucket", extra={"json_fields": {
						"key": key, 
						"file_name": file_info["file_name"], 
						"remote_path": file_info["path"],
						"gcs_path": archive_path,
						"shape": df.shape
					}})
				except Exception as e:
					logging.error("Error uploading file data to BQ", extra={"json_fields": {
						"error": str(e),
						"stacktrace": "".join(traceback.format_exception(type(e), e, e.__traceback__)),
						"key": key
					}})

					if path:
						logging.info("About to move sftp file to error bucket", extra={"json_fields": {
							"key": key, 
							"file_name": file_info["file_name"], 
							"remote_path": file_info["path"],
							"gcs_path": path,
							"shape": df.shape
						}})

						error_path = move_file_to_error(path)

						logging.info("SFTP file moved to error bucket", extra={"json_fields": {
							"key": key, 
							"file_name": file_info["file_name"], 
							"remote_path": file_info["path"],
							"original_gcs_path": path,
							"new_path": error_path,
							"shape": df.shape
						}})

					return jsonify({
						"error": "Error uploading file data to BQ",
						"message": f"No se pudieron subir los datos del fichero a BQ: {str(e)}"
					}), 502

				logging.info("About to delete file from SFTP", extra={"json_fields": {
					"folder": key, 
					"file_name": file_info["file_name"], 
					"remote_path": file_info["path"], 
				}})

				delete_file(file_info["path"])

				logging.info("Remote file removed from SFTP", extra={"json_fields": {
					"folder": key, 
					"file_name": file_info["file_name"], 
					"remote_path": file_info["path"],
				}})

		except Exception as e:
			logging.error("Error on sftp table sync", extra={"json_fields": {
				"error": str(e),
				"stacktrace": "".join(traceback.format_exception(type(e), e, e.__traceback__)),
				"key": key
			}})

	logging.info("About to close connection from SFTP")

	close_connection()

	logging.info("Connection closed from SFTP")

	return "<p>OK</p>"