from odoo import fields, models

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
