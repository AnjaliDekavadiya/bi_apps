import json

from odoo import api, fields, models


class AmazonSynchronizationLog(models.Model):
    _name = 'amazon.synchronization.log'
    _order = 'id desc'
    _rec_name = "message"

    account_id = fields.Many2one(
        'amazon.account',
        string='Account', required=True)
    message = fields.Text("Message")
    res_model = fields.Char(string="Model")
    res_id = fields.Integer("Record ID")

    log_type = fields.Selection([
        ('not_found', 'NOT FOUND'),
        ('mismatch', 'MISMATCH'),
        ('error', 'Error'),
        ('warning', 'Warning')
    ], 'Log Type')
    action_type = fields.Selection([
        ('create', 'Created New'),
        ('skip_line', 'Line Skipped'),
        ('terminate_process_with_log', 'Terminate Process With Log')
    ], 'Action')
    operation_type = fields.Selection([
        ('import_order', 'Import Order'),
        ('export_status', 'Export Status')
    ], string="Operation", readonly=True)

    user_id = fields.Many2one("res.users", string="Responsible")
    amazon_order_ref = fields.Char("Amazon Order Ref")
    report_log_id = fields.Many2one("amazon.report.log", string="Report Log")
    json_debug = fields.Text()

    @api.model
    def order_sync_failure(self, account, order_data, error_msg=False):
        self.create({
            'account_id': account.id,
            'operation_type': 'import_order',
            'log_type': 'error',
            'message': str(error_msg),
            'user_id': self.env.user.id,
            'amazon_order_ref': order_data['AmazonOrderId'],
            "json_debug": json.dumps(order_data),
        })

