# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
        if restricted_customer:
            domain = ['|',('salesperson_ids','in',self.env.user.ids),('team_id.member_ids','in',self.env.user.ids)] + list(domain)
        return super(SaleOrder, self.with_context(do_not_include=True))._search(domain, offset, limit, order, access_rights_uid)

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