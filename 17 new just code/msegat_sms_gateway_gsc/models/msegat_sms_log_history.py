# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MsegatSMSLogHistory(models.Model):
    _name = 'msegat.sms.log.history'
    _description = "Msegat SMS Log History"
    _order = 'id DESC'

    name = fields.Char("Log ID", copy=False, help="LOG ID")
    sms_send_rec_id = fields.Many2one("msegat.sms.send", "SMS Send ID", copy=False)
    msegat_account_id = fields.Many2one("msegat.sms.gateway.account", "SMS Account ID", copy=False)
    partner_id = fields.Many2one("res.partner", "Contact", copy=False)
    mobile_number = fields.Char("Mobile No.", copy=False)
    message = fields.Text("Message", copy=False)
    status = fields.Char("Status", copy=False)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    picking_id = fields.Many2one('stock.picking', string="Transfer")
    error_code = fields.Char("Error Code", copy=False)
    error_message = fields.Char("Error Message", copy=False)
    error_status_code = fields.Char("Error Status Code", copy=False)

    @api.model
    def create(self, vals):
        """
            @author: Grow Consultancy Services
        """
        seq_id = self.env['ir.sequence'].next_by_code('odoo.msegat.sms.log.history.seq')
        vals.update({'name': seq_id})
        return super(MsegatSMSLogHistory, self).create(vals)
