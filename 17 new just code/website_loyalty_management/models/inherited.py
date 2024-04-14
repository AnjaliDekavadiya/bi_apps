# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

State = [
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('cancel', 'Cancel')
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wk_website_loyalty_points = fields.Float(
        string='Website Loyalty Points',
        help='The points are the points with which the user is awarded of being Loyal !',
        digits= 'Loyalty Points',
        default=0,
        compute='_compute_loyalty_points'
    )

    def _compute_loyalty_points(self):
        for record in self:
            domain = [
                ('partner_id', '=', record.id),
            ]
            credit = 0
            debit = 0
            histories = self.env['website.loyalty.history'].sudo().search(
                domain)
            for history in histories:
                if history.loyalty_process == 'addition':
                    credit += history.points_processed
                else:
                    debit += history.points_processed
            points = credit - debit
            record.wk_website_loyalty_points = points


class res_users(models.Model):
    _inherit = 'res.users'

    wk_website_loyalty_points = fields.Float(
        related='partner_id.wk_website_loyalty_points'
    )

    @api.model_create_multi
    def create(self, values):
        for vals in values:
            wk_loyalty_program_id = self.env['website'].sudo().get_current_website().wk_loyalty_program_id
            groups_id = vals.get('groups_id')
            portal_signup = (self.env.ref('base.group_portal').id in groups_id[0][2]) if groups_id else False
            if wk_loyalty_program_id and wk_loyalty_program_id.active and (portal_signup or vals.get('in_group_1')):

                wk_website_loyalty_points = wk_loyalty_program_id._fetch_signup_loyalty_points()
                if wk_website_loyalty_points:
                    vals['wk_website_loyalty_points'] = wk_website_loyalty_points
                    res = super(res_users, self).create(vals)
                    history = self.env['website.loyalty.history'].search_read([], ['cust_email'])
                    cust_email = set()
                    for rec in history:
                        cust_email.add(rec.get('cust_email'))

                    if res.partner_id.email in cust_email:
                        wk_website_loyalty_points = 0

                    res.partner_id.wk_website_loyalty_points = wk_website_loyalty_points
                    history_vals = {
                        'partner_id': res.partner_id.id,
                        'cust_email': res.partner_id.email,
                        'loyalty_id': wk_loyalty_program_id.id,
                        'points_processed': wk_website_loyalty_points,
                        'loyalty_process': 'addition',
                        'process_reference': 'Sign Up',
                    }

                    self.env['website.loyalty.history'].sudo().create(history_vals)
                    return res
        return super(res_users, self).create(values)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total','wk_extra_loyalty_points')
    def _compute_wk_website_loyalty_points(self):
        for order in self:
            if order.wk_loyalty_state not in ['cancel', 'done']:
                amount = order.amount_total
                obj = self.env['website'].get_current_website(
                ).wk_loyalty_program_id
                if obj and obj.active:
                    wk_website_loyalty_points = order.wk_extra_loyalty_points + obj.get_loyalty_points(amount, order_id=order)                    
                    order.update({
                        'wk_website_loyalty_points': wk_website_loyalty_points,
                    })
                else:
                    order.update({
                        'wk_website_loyalty_points': 0.0,
                    })

    @api.model
    def _get_default_wk_loyalty_program_id(self):
        if self.env['website'].get_current_website().wk_loyalty_program_id.active:
            return self.env['website'].get_current_website().wk_loyalty_program_id.id
        else:
            return False

    wk_extra_loyalty_points = fields.Float(
        string='Extra Loyalty Points',
        copy=False,
        default=0
    )
    wk_loyalty_program_id = fields.Many2one(
        string='Loyalty Program',
        comodel_name='website.loyalty.management',
        default=_get_default_wk_loyalty_program_id
    )
    wk_website_loyalty_points = fields.Float(
        string='Loyalty Points',
        store=True,
        readonly=True,
        compute='_compute_wk_website_loyalty_points'
    )
    wk_loyalty_state = fields.Selection(
        selection=State,
        string='Loyalty Stage',
        default='draft',
        copy=False
    )

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.update_partner_loyalty(record, 'confirm')
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.with_context(
                action_cancel=True).cancel_redeem_history(record)
        return res

    def _website_product_id_change(self, order_id, product_id, qty=0, **kwargs):
        order = self.sudo().browse(order_id)
        order_line = order._cart_find_product_line(product_id)
        unit_price = order_line.price_unit
        res = super(SaleOrder, self)._website_product_id_change(
            order_id, product_id, qty, **kwargs)
        if order_line.is_virtual:
            res['price_unit'] = unit_price
        return res

    class SaleOderLine(models.Model):
        _inherit = "sale.order.line"

        def unlink(self):
            if self.virtual_source == "wk_website_loyalty":
                order = self.order_id
                self.order_partner_id.wk_website_loyalty_points += self.redeem_points
                self.env['website.loyalty.management'].sudo(
                ).cancel_redeem_history(order)
            return super().unlink()

    class AccountTax(models.Model):
        _inherit = 'account.tax'

        @api.model
        def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
            """
            Prepare tax totals and include loyalty points data if the base line corresponds to a sale order line.

            :param base_lines: List of base lines.
            :param currency: Currency information.
            :param tax_lines: Tax lines information.
            :return: A dictionary containing tax totals with loyalty points data if applicable.
            """
            res = super()._prepare_tax_totals(base_lines, currency, tax_lines)
            if base_lines and base_lines[0]['record']._name == "sale.order.line":
                order_id = base_lines[0]['record'].order_id
                loyalty_data = {}
                if order_id.wk_extra_loyalty_points:
                    loyalty_data.update({'wk_extra_loyalty_points': order_id.wk_extra_loyalty_points})
                if order_id.wk_website_loyalty_points:
                    loyalty_data.update({'wk_website_loyalty_points': order_id.wk_website_loyalty_points, 'loyalty_state':order_id.wk_loyalty_state})
                if order_id.wk_extra_loyalty_points:
                    res.update({'formatted_amount_total':order_id.wk_website_loyalty_points})    
                return {**res, **loyalty_data}
            return res
