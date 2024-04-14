from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    pos_access_close_sent_kitchen = fields.Boolean(
        string='Access for Closing POS (with orders sent to kitchen but unpaid)',
        default=True
    )
    pos_access_decrease_quantity_sent_kitchen = fields.Boolean(
        string='Access for Decreasing Quantity (with orders sent to kitchen but unpaid)',
        default=True
    )
    pos_access_delete_order_sent_kitchen = fields.Boolean(
        string='Access for Order Deletion (with orders sent to kitchen but unpaid)',
        default=True
    )
    pos_access_delete_orderline_sent_kitchen = fields.Boolean(
        string='Access for Order Line Deletion (with orders sent to kitchen but unpaid)',
        default=True
    )
