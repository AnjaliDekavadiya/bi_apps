# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('do_not_include'):
            pass
        else:
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                args = [('salesperson_ids','in',self.env.user.ids)] + list(args)
        return super(SaleOrder, self)._search(args, offset, limit, order, count, access_rights_uid)

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
#    def onchange_partner_id(self):
    def onchange_partner_id_custom(self):
#        super(SaleOrder, self).onchange_partner_id()
#        res = super(SaleOrder, self).onchange_partner_shipping_id()
        self._compute_partner_shipping_id()
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
