from odoo import models, api, fields
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import logging

_logger = logging.getLogger(__name__)

class BigQueryExport(models.Model):
    _name = 'bigquery.techfinna.export'
    _description = 'BigQuery Data Export'

    table_to_export = fields.Selection(selection='_get_table_options', string="Choose a Table")

    @api.model
    def _get_table_options(self):
        self.env.cr.execute("SELECT relname AS table FROM pg_stat_user_tables ORDER BY relname")
        tables = self.env.cr.fetchall()
        return [(table[0], table[0].replace('_', '.')) for table in tables]
    
    def action_export_data(self):
        """ Exports data of the selected table to BigQuery. """
        if not self.table_to_export:
            _logger.error("No table selected for export.")
            return

        # Convert the selected table name to the model name (if required)
        model_name = self.table_to_export.replace('_', '.')

        # Obtain the reference to the BigQuery export model
        bigquery_exporter = self.env['bigquery.techfinna.export']

        # Call the export function from the BigQuery export model
        try:
            bigquery_exporter.export_data_to_bigquery(model=model_name)
            _logger.info(f"Data export to BigQuery initiated for table: {model_name}")
        except Exception as e:
            _logger.error(f"Error during export to BigQuery: {str(e)}")
            raise



    def get_bigquery_client(self):
        ICP = self.env['ir.config_parameter'].sudo()
        credentials_json = ICP.get_param('bigquery.credentials_json')
        if not credentials_json:
            _logger.error("BigQuery credentials are not set.")
            raise ValueError("BigQuery credentials are not set in the system parameters.")

        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON format for BigQuery credentials: {e}")
            raise

        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        project_id = ICP.get_param('bigquery.project_id')
        return bigquery.Client(project=project_id, credentials=credentials)

    @api.model
    def export_data_to_bigquery(self, model='sale.order'):
        client = self.get_bigquery_client()
        dataset_id = self.env['ir.config_parameter'].sudo().get_param('bigquery.dataset_id')
        
        if not dataset_id:
            _logger.error("BigQuery dataset ID is not set.")
            raise ValueError("BigQuery dataset ID is not set in the system parameters.")

        # Example: Exporting a simple Odoo model data
        # Replace 'your.odoo.model' and the field names with your actual model and fields
        query = f'''
            SELECT * 
            FROM {model.replace('.', '_')} 
        '''
        self.env.cr.execute(query)
        values = self.env.cr.dictfetchall()
        dataframe = pd.DataFrame(values)

        # table_id = f"{client.project}.{dataset_id}.res_user"  # Replace 'your_table_name' with your actual table name
        table_id = f"{dataset_id}.{model.replace('.','_')}"  # Replace 'your_table_name' with your actual table name


        try:
            job = client.load_table_from_dataframe(dataframe, table_id)
            job.result()  # Wait for the job to complete
            _logger.info(f"Loaded {job.output_rows} rows into {table_id}.")
        except Exception as e:
            _logger.error(f"Error loading data to BigQuery: {e}")
            raise
