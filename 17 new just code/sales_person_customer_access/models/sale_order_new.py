# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if not self.env.context.get('do_not_include'):
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                salesperson_domain = [('salesperson_ids', 'in', self.env.user.ids)]
                if not any(arg[0] == 'id' or arg[0] == 'parent_id' for arg in domain):
                    domain += salesperson_domain
        return super(SaleOrder, self)._search(domain, offset, limit, order, access_rights_uid)

    def read(self, fields=None, load='_classic_read'):
        orders = super(SaleOrder, self).read(fields=fields, load=load)
        if len(orders) == 1:
            if self.env.user.has_group("sales_person_customer_access.group_restricted_customer"):
                order_restrict_access_config = self.env['sale.order'].sudo().search([('salesperson_ids', 'in', self.env.user.ids)])
                if order_restrict_access_config:
                    for order in orders:
                        if order.get('id') and order.get('id') not in order_restrict_access_config.ids:
                            raise AccessError(_("You don't have the access!"))
        return orders

    @api.onchange('partner_id')
    def onchange_partner_id_custom(self):
        self._compute_partner_shipping_id()
        if self.partner_id.salesperson_ids:
            self.salesperson_ids=[(6, 0, self.partner_id.salesperson_ids.ids)]
        else:
            self.salesperson_ids=[]

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({'salesperson_ids': [(6, 0, self.salesperson_ids.ids)]})
        return result

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        res.update({'salesperson_ids': [(6, 0, sale_orders.salesperson_ids.ids)]})
        return res
