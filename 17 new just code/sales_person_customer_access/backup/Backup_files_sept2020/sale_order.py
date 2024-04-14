# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
        if restricted_customer:
            args = [('salesperson_ids','in',self.env.user.id)] + list(args)
        return super(SaleOrder, self)._search(args, offset, limit, order, count, access_rights_uid)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        if self.partner_id.salesperson_ids:
            self.salesperson_ids=[(6, 0, self.partner_id.salesperson_ids.ids)]
        else:
            self.salesperson_ids=[]

#    @api.multi #odoo13
    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({'salesperson_ids': [(6, 0, self.salesperson_ids.ids)]})
        return result

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

#    @api.multi #odoo13
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        res.update({'salesperson_ids': [(6, 0, sale_orders.salesperson_ids.ids)]})
        return res
