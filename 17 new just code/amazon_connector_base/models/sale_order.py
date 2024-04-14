import json

from odoo import api, fields, models, _
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @property
    def _rec_names_search(self):
        res = super()._rec_names_search
        res.append('amazon_order_ref')
        return res

    amz_account_id = fields.Many2one(
        'amazon.account',
        string='Amazon Account'
    )
    amz_marketplace_id = fields.Many2one(
        string="Amazon Marketplace",
        help="The marketplace of this Order.",
        comodel_name='amazon.marketplace',
    )
    amz_debug_data = fields.Text()
    """
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = [('amazon_order_ref', operator, name)]
            return self._search(expression.OR([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)"""

    @api.model
    def update_amazon_information(self, order_data, amz_account=False):
        marketplace = self.env['amazon.marketplace'].search([
            ('api_ref', '=', order_data['MarketplaceId'])
        ])
        vals = {
            "amz_marketplace_id": marketplace.id,
            "amz_debug_data": json.dumps(order_data),
        }
        if marketplace.pricelist_id:
            vals['pricelist_id'] = marketplace.pricelist_id.id
        if marketplace.team_id:
            vals['team_id'] = marketplace.team_id.id
        if marketplace.analytic_account_id:
            vals['analytic_account_id'] = marketplace.analytic_account_id.id
        if order_data["FulfillmentChannel"]  == 'MFN' and marketplace.fbm_location_id:
            vals['warehouse_id'] = marketplace.fbm_location_id.warehouse_id.id
        elif order_data["FulfillmentChannel"]  == 'AFN' and marketplace.fba_location_id:
            vals['warehouse_id'] = marketplace.fba_location_id.warehouse_id.id
        if amz_account:
            vals['amz_account_id'] = amz_account.id
        if self:
            # Called with Sale Order Record
            self.write(vals)
        return vals
