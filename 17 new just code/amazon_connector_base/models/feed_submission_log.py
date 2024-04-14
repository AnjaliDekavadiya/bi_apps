import base64
import logging
import requests
import time

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.sale_amazon import utils as amazon_utils


_logger = logging.getLogger(__name__)


class FeedSubmissionLog(models.Model):
    _name = "feed.submission.log"
    _order = 'feed_id desc'
    _rec_name = "feed_id"

    account_id = fields.Many2one('amazon.account', string='Account', required=True)
    feed_type = fields.Char('Feed Type', required=True)
    feed_id = fields.Char(string='Feed Amazon ID', copy=False)
    feed_message = fields.Text('Feed Message', required=True)
    feed_options = fields.Char('Feed Options')
    feed_submit_date = fields.Datetime(
        'Feed Submit Date',
        default=fields.Datetime.now(), copy=False)
    feed_result = fields.Text('Feed Result', copy=False)
    feed_document_result = fields.Text('Feed Document Result', copy=False)
    feed_result_date = fields.Datetime('Feed Result Date', copy=False)
    user_id = fields.Many2one('res.users', string="Requested User", copy=False)
    amz_marketplace_ids = fields.Many2many(
        comodel_name='amazon.marketplace',
        string="Amazon Marketplaces",
        help="The marketplaces of this Feed",
    )

    @api.model_create_multi
    def create(self, vals_list):
        feeds = super().create(vals_list)
        if self._context.get("no_submit", False):
            # Just create and submit manually
            return feeds
        feeds.submit_feed_to_amz()
        pdf_feeds = feeds.filtered(lambda f: f.feed_type == 'UPLOAD_VAT_INVOICE')
        # Remove PDF content to save db storage
        for feed in pdf_feeds:
            feed.write({"feed_message": feed.feed_options})
        return feeds

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        return super(FeedSubmissionLog,self.with_context(no_submit=True)
                     ).copy(default=default)

    def submit_feed_to_amz(self):
        amazon_utils.refresh_aws_credentials(self.mapped('account_id'))
        amazon_utils.ensure_account_is_set_up(self.mapped('account_id'))
        for feed in self:
            feed_id = False
            if (not feed.account_id or not feed.feed_message
                or not feed.feed_type or feed.feed_id):
                continue
            try:
                feed_id = amazon_utils.submit_feed(
                    feed.account_id,
                    base64.b64decode(feed.feed_message) if feed.feed_options else feed.feed_message,
                    feed.feed_type,
                    feed.amz_marketplace_ids.mapped('api_ref')
                    if feed.amz_marketplace_ids else [],
                    feed.feed_options,
                )
            except amazon_utils.AmazonRateLimitError:
                _logger.info(
                    "Rate limit reached while sending feed to Amazon with type: %s",
                    feed.feed_type
                )
                time.sleep(2)
            except Exception as e:
                _logger.info(
                    "Error when sending feed to Amazon, ID: %s\n%s", feed_id, str(e)
                )
                continue
            feed.write({
                'feed_id': feed_id,
                'feed_submit_date': fields.Datetime.now(),
            })
            time.sleep(0.2)

    @api.model
    def submit_missing_feeds(self):
        unsubmitted_feeds = self.search([('feed_id', '=', False)], limit=30)
        if unsubmitted_feeds:
            unsubmitted_feeds.submit_feed_to_amz()

    def get_feed_submission_result(self):
        # Maybe the Feed Submission result is not ready yet, retrying 2 times
        # with 10 seconds interval between (total is 20 seconds only)
        self.ensure_one()
        result = amazon_utils.make_sp_api_request(
            self.account_id,
            operation='getFeedResult',
            path_parameter=self.feed_id,
        )
        print(result)
        processing_report = False
        if result.get('resultFeedDocumentId'):
            document_result = amazon_utils.make_sp_api_request(
                self.account_id,
                operation='getFeedDocumentResult',
                path_parameter=result['resultFeedDocumentId']
            )
            processing_report = requests.get(document_result['url'])
        vals = {
            'feed_result': str(result),
            'feed_result_date': fields.Datetime.now()
        }
        if processing_report and processing_report.ok:
            vals['feed_document_result'] = processing_report.content.decode("utf-8")

        self.write(vals)
        return result
