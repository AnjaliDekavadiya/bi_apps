
from xml.etree import ElementTree

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

from odoo.addons.sale_amazon import utils as amazon_utils


class AmazonMarketplace(models.Model):
    _inherit = 'amazon.marketplace'

    account_id = fields.Many2one('account.account', string='Account')
    tax_id = fields.Many2one('account.tax', string='Default Sales Tax')
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string="Pricelist (Price not sync)",
        help="Prices are not synced, only use to set Pricelist field on Sale Orders"
    )
    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team")
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account"
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Journal"
    )
    fbm_location_id = fields.Many2one(
        'stock.location',
        string="FBM Stock Location",
        domain=[('usage', '=', 'internal')]
    )
    fba_location_id = fields.Many2one(
        'stock.location',
        string="FBA Stock Location",
        domain=[('usage', '=', 'internal')]
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Default Customer"
    )
    amazon_offer_ids = fields.One2many(
        comodel_name='amazon.offer',
        inverse_name='marketplace_id',
        string='Amazon Products'
    )
    amazon_offer_count = fields.Integer(compute='_compute_amz_offer_count')

    def _compute_amz_offer_count(self):
        offer_env = self.env['amazon.offer']
        for mp in self:
            mp.amazon_offer_count = offer_env.search_count([
                ('marketplace_id', '=', mp.id)
            ])

    def action_view_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Amazon Products'),
            'res_model': 'amazon.offer',
            'view_mode': 'tree',
            'domain': [('marketplace_id', '=', self.id)],
            'context': {'default_marketplace_id': self.id},
        }

