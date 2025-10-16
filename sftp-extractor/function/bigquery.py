from enum import Enum
import logging
import traceback
import re

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from credentials.project_info import PROCESS_INFO

class BQ_INFO(Enum):
	DATASET_ID = f"bq_ing_sftp_{PROCESS_INFO.PROCESS_NAME.value}"
	TABLE_ID_PREFIX = "bq_ing_manual_"
	SAFE_COLUMN_NAME_REGEX = "[^a-zA-Z0-9_]"
	SAFE_TABLE_NAME_REGEX = "[^a-zA-Z0-9_]"

def get_bigquery_client() -> bigquery.Client:
	"""
    Gets an authenticated client for Google Cloud BigQuery.

    Returns
    -------
    bigquery.Client BigQuery client
    """
	return bigquery.Client()


def upload_to_big_query(file_path: str, data: pd.DataFrame, file_name: str):
	try:
		bq_client = get_bigquery_client()

		table_name = scape_table_name(file_name)

		job_config = bigquery.LoadJobConfig(
			source_format=bigquery.SourceFormat.CSV,
			write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
			create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
			skip_leading_rows=1,
			time_partitioning=bigquery.TimePartitioning(field="upload_date", type_=bigquery.TimePartitioningType.DAY),
			schema = [bigquery.SchemaField(column, bigquery.enums.SqlTypeNames.STRING) for column in data.columns]
		)


		job = bq_client.load_table_from_uri(file_path, f'{BQ_INFO.DATASET_ID.value}.{BQ_INFO.TABLE_ID_PREFIX.value}{table_name}', job_config=job_config)
		
		job.result()
	except Exception as e:
		logging.error("Error uploading data to BigQuery", extra={"json_fields": {
			"file": file_name,
			"shape": data.shape
		}})

		raise e

def scape_table_name(file_name: str) -> str:
	"""
    Parses file name to safe BigQuery table name

    Parameters
    ----------
    file_name : str File name

	Returns
	----------
	str Safe table name
    """
	return re.sub(BQ_INFO.SAFE_TABLE_NAME_REGEX.value, "", file_name.split(".")[0].replace(" ", "_"), 0, re.MULTILINE)

def scape_column_name(column: str) -> str:
	"""
    Parses column to safe BigQuery column name

    Parameters
    ----------
    column : str Real column name

	Returns
	----------
	str Safe column name
    """
	return	re.sub(BQ_INFO.SAFE_COLUMN_NAME_REGEX.value, "", column.replace(" ", "_"), 0, re.MULTILINE).lower()

def check_columns(data: pd.DataFrame, file_name: str):
	"""
	Validates dataframe columns names from bigquery table

	Parameters
	----------
	data : pd.Dataframe Dataframe data
	file_name : str File name

	Returns:
	----------
	pd.Dataframe Dataframe data with correct columns names
	"""
	columns = [scape_column_name(column) for column in data.columns]

	try:
		schema = get_table_schema(scape_table_name(file_name))
	except NotFound:
		schema = columns
	except Exception as e:
		raise e
	
	data.columns = columns

	for column in schema:
		if column not in columns:
			logging.error("File format not valid", extra={"json_fields":{
				"error": "Missing column name",
				"schema": schema,
				"columns": columns,
				"column": column,
				"file_name": file_name,
			}})

			raise ValueError("File format not valid")
		
	return data[columns]
		
		
	
def get_table_schema(table_name: str):
	"""
	Gets table schema and checks if table exists

	Parameters
	----------
	table_name : str Table name

	Returns:
	----------
	list Table schema
	"""
	bq_client = get_bigquery_client()

	try:
		table = bq_client.get_table(f'{BQ_INFO.DATASET_ID.value}.{BQ_INFO.TABLE_ID_PREFIX.value}{table_name}')
	except NotFound as e:
		raise e
	except Exception as e:
		logging.error("Error getting table", extra={"json_fields": {
			"table": table_name,
			"error": str(e),
			"stack": "".join(traceback.format_exception(type(e), e, e.__traceback__))
		}})

		raise e
	
	return [column.name for column in table.schema]