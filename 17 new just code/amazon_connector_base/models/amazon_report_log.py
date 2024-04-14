import base64
import logging
import requests
import time
import zlib

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.sale_amazon import utils as amazon_utils

_logger = logging.getLogger(__name__)


SUPPORTED_PATHS = (
    "[Content_Types].xml",
    "xl/sharedStrings.xml",
    "xl/styles.xml",
    "xl/workbook.xml",
    "_rels/",
    "xl/_rels",
    "xl/charts/",
    "xl/drawings/",
    "xl/externalLinks/",
    "xl/pivotTables/",
    "xl/tables/",
    "xl/theme/",
    "xl/worksheets/"
)


class AmazonReportLog(models.Model):
    _name = 'amazon.report.log'
    _description = "Amazon Report Log"
    _order = 'id desc'
    _rec_name = "report_id"

    account_id = fields.Many2one('amazon.account', string='Account', required=True)
    report_id = fields.Char(string="Report ID", copy=False)
    # report_type = fields.Char(string="Report Type")
    report_type_id = fields.Many2one(
        comodel_name='amazon.report.type',
        string="Report Type",
        required=True,
    )
    report_document_id = fields.Char(string='Report Document ID', copy=False)
    report_file = fields.Binary(string="Report File", copy=False)
    report_filename = fields.Char(string="Report Filename", copy=False)
    amz_marketplace_ids = fields.Many2many(
        comodel_name='amazon.marketplace',
        string="Amazon Marketplaces",
        help="The marketplaces of this Report",
    )
    report_url = fields.Char(string="Report URL", copy=False)
    report_date_from = fields.Datetime(string="Date From")
    report_date_to = fields.Datetime(string="Date To")
    requested_date = fields.Datetime(
        string='Requested Date',
        default=fields.Datetime.now(), copy=False)
    user_id = fields.Many2one("res.users", string="Responsible",
                              default=lambda self: self.env.user)
    state = fields.Selection([
        ('DRAFT', 'DRAFT'),
        ('SUBMITTED', 'SUBMITTED'),
        ('IN_QUEUE', 'IN_QUEUE'),
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('CANCELLED', 'CANCELLED'),
        ('DONE', 'DONE'),
        ('FATAL', 'FATAL'),
        ('PROCESSED', 'PROCESSED'),
    ], string='Report Status', default='DRAFT', copy=False)
    # listing_fields = fields.One2many()


    def request_report(self):
        amazon_utils.refresh_aws_credentials(self.mapped('account_id'))
        amazon_utils.ensure_account_is_set_up(self.mapped('account_id'))
        for report in self:
            report_id = False
            if (not report.account_id or not report.report_type_id):
                continue
            try:
                date_from = self.report_date_from.isoformat(sep='T') \
                    if self.report_date_from else False
                date_to = self.report_date_to.isoformat(sep='T') \
                    if self.report_date_to else False
                report_id = amazon_utils.create_report(
                    report.account_id,
                    report.report_type_id.technical_name,
                    start_date=date_from,
                    end_date=date_to,
                    marketplace_ids=report.amz_marketplace_ids.mapped('api_ref')
                    if report.amz_marketplace_ids else [],
                )
            except amazon_utils.AmazonRateLimitError:
                _logger.info(
                    "Rate limit reached while creating report to Amazon with type: %s",
                    report.report_type_id.technical_name
                )
                time.sleep(2)
            except Exception as e:
                _logger.info(
                    "Error when sending report to Amazon, ID: %s\n%s", report_id, str(e)
                )
                continue
            report.write({
                'report_id': report_id,
                'requested_date': fields.Datetime.now(),
            })
            time.sleep(0.2)

    def check_report_status(self):
        amazon_utils.refresh_aws_credentials(self.mapped('account_id'))
        amazon_utils.ensure_account_is_set_up(self.mapped('account_id'))
        for report in self:
            report_status = False
            if (not report.account_id or not report.report_id or
                    report.state in ["DONE", "CANCELLED"]):
                continue
            try:
                report_status = amazon_utils.get_report(
                    report.account_id,
                    report.report_id,
                )
            except amazon_utils.AmazonRateLimitError:
                _logger.info(
                    "Rate limit reached while checking report to Amazon with type: %s",
                    report.report_id
                )
                time.sleep(2)
            except Exception as e:
                _logger.info(
                    "Error when sending report to Amazon, ID: %s\n%s", report_status, str(e)
                )
                continue
            report.write({
                'report_document_id': report_status.get(
                    'reportDocumentId', str(report_status)),
                'state': report_status['processingStatus'],
            })
            time.sleep(0.2)
            if report.state == "DONE":
                # there is already time interval in the function below
                report.retrieve_report_document()

    def _get_report_file_from_url(self, report_url, compression=False):
        document_response = requests.get(report_url)
        document = document_response.content
        if compression:
            document = zlib.decompress(bytearray(document), 15 + 32)
        return base64.b64encode(document)

    def retrieve_report_document(self):
        amazon_utils.refresh_aws_credentials(self.mapped('account_id'))
        amazon_utils.ensure_account_is_set_up(self.mapped('account_id'))
        for report in self:
            if (not report.account_id or not report.report_document_id):
                continue
            report_filename = "{}-{}".format(
                report.report_type_id.technical_name,
                report.report_id
            )
            if report.report_url:
                report_file = self._get_report_file_from_url(
                    report.report_url)
                report.write({
                    "report_file": report_file,
                    "report_filename": report_filename
                })
            try:
                report_document = amazon_utils.get_report_document(
                    report.account_id,
                    report.report_document_id,
                )
            except amazon_utils.AmazonRateLimitError:
                _logger.info(
                    "Rate limit reached while checking report to Amazon with type: %s",
                    report.report_id
                )
                time.sleep(2)
            except Exception as e:
                _logger.info(
                    "Error when sending report to Amazon, ID: %s\n%s", self.report_id, str(e)
                )
                continue
            vals = {
                'report_url': report_document['url'],
                'report_file': self._get_report_file_from_url(
                    report_document['url'],
                    compression=report_document.get('compressionAlgorithm')
                ),
                'report_filename' : report_filename,
            }

            report.write(vals)
            time.sleep(0.2)

    def process_report(self):
        self.ensure_one()
        if not self.report_type_id.name:
            raise UserError("Please choose a report type")
        if not self.report_file:
            return False
        if hasattr(self, 'process_report_%s' % self.report_type_id.technical_name):
            res = getattr(self, 'process_report_%s' % self.report_type_id.technical_name)()
            if res:
                self.write({"state": "PROCESSED"})
            return res
        return False
