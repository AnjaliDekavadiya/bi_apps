# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class RmaConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_quote_cancellation = fields.Boolean(
        string="Allow cancellation of order quote.", help="Customer can cancel quotation order.")
    process_do_state = fields.Selection([
        ('all', 'All'),
        ('done', 'Only Done'),
    ], string="Process state")
    rma_term_condition = fields.Html(string="Term And Conditions")
    days_for_rma = fields.Integer(string="Return Policy",
                                  help="Number of days upto which customer can request for RMA after delivery done.")
    rma_day_apply_on = fields.Selection(
        [("so_date", "Order Date"), ("do_date", "Delivery Date")], string="Apply On")
    is_repair_enable = fields.Boolean(
        "Allow repair of product in RMA.", help='Allows to manage all product repairs.\n')
    repair_location_id = fields.Many2one(
        'stock.location', 'Repair Location')
    show_rma_stage = fields.Boolean(string="Show RMA stage to customer.")
    enable_notify_admin_4_rma = fields.Boolean(string="Enable Notification Admin For RMA")
    enable_notify_customer_4_rma = fields.Boolean(string="Enable Notification Customer For RMA")
    notify_admin_for_rma_creation = fields.Many2one(
        "mail.template", string="Mail Template to Notify Admin On RMA Request", domain="[('model_id.model','=','rma.rma')]")
    notify_customer_for_rma_creation = fields.Many2one(
        "mail.template", string="Mail Template to Notify Customer On RMA Request", domain="[('model_id.model','=','rma.rma')]")
    
    def check_repair_install(self):
        irmodule_obj = self.env['ir.module.module']
        vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
            'to install', 'installed', 'to upgrade'])])   
        if not vals:
            raise UserError("You need to install the repair module for Repair Management !!")     
        return

    def set_values(self):
        super(RmaConfigSettings, self).set_values()
        ir_default = self.env['ir.default'].sudo()

        if self.is_repair_enable:
            self.check_repair_install()

        ir_default.set('res.config.settings', 'is_repair_enable', self.is_repair_enable)
        ir_default.set('res.config.settings', 'allow_quote_cancellation', self.allow_quote_cancellation)
        ir_default.set('res.config.settings', 'process_do_state', self.process_do_state)
        ir_default.set('res.config.settings', 'rma_term_condition', self.rma_term_condition)
        ir_default.set('res.config.settings', 'days_for_rma', self.days_for_rma)
        ir_default.set('res.config.settings', 'rma_day_apply_on', self.rma_day_apply_on)
        ir_default.set('res.config.settings', 'repair_location_id', self.repair_location_id.id)
        ir_default.set('res.config.settings', 'show_rma_stage', self.show_rma_stage)
        ir_default.set('res.config.settings', 'enable_notify_admin_4_rma', self.enable_notify_admin_4_rma)
        ir_default.set('res.config.settings', 'enable_notify_customer_4_rma', self.enable_notify_customer_4_rma)
        ir_default.set('res.config.settings', 'notify_admin_for_rma_creation', self.notify_admin_for_rma_creation.id)
        ir_default.set('res.config.settings', 'notify_customer_for_rma_creation', self.notify_customer_for_rma_creation.id)
        return True

    @api.model
    def get_values(self):
        res = super(RmaConfigSettings, self).get_values()
        ir_default = self.env['ir.default'].sudo()
        is_repair_enable = ir_default._get('res.config.settings', 'is_repair_enable')
        allow_quote_cancellation = ir_default._get('res.config.settings', 'allow_quote_cancellation')
        process_do_state = ir_default._get('res.config.settings', 'process_do_state')
        rma_term_condition = ir_default._get(
            'res.config.settings', 'rma_term_condition') or "About Return and Refund Policies Most e-commerce stores should have a Return or Refund Policy, just as it should have a Privacy Policy. Wikipedia defines Returning as: In retail, returning is the process of a customer taking previously purchased merchandise back to the retailer, and in turn, receiving a cash refund, exchange for another item (identical or different), or a store credit. Most countries industry regulations require that stores (even digital) must have this kind of policy. eBay’s help pages mention that stores with return policies published online sell better (however, eBay requires all stores to have this policy): We’ve found that items with clear return policies typically sell better than items that don’t. A Terms and Conditions agreement for your store might be a good idea, but it is not required by law. If you’re looking for a Terms and Conditions agreement, you can generate it with our generator. What to include in your policy Your Return Policy should include at least the following sections: the numbers of days a customer can notify you for wanting to return an item after they received it what kind of refund you will give to the customer after the item is returned: another similar product, a store credit, etc. who will pay for the return shipping"
        days_for_rma = ir_default._get('res.config.settings', 'days_for_rma')
        rma_day_apply_on = ir_default._get('res.config.settings', 'rma_day_apply_on') or "do_date"
        show_rma_stage = ir_default._get('res.config.settings', 'show_rma_stage')
        repair_location_id = ir_default._get('res.config.settings', 'repair_location_id')
        enable_notify_admin_4_rma = ir_default._get('res.config.settings', 'enable_notify_admin_4_rma')
        enable_notify_customer_4_rma = ir_default._get('res.config.settings', 'enable_notify_customer_4_rma')
        notify_admin_for_rma_creation = ir_default._get('res.config.settings', 'notify_admin_for_rma_creation')
        notify_customer_for_rma_creation = ir_default._get('res.config.settings', 'notify_customer_for_rma_creation')
        res.update({
            "is_repair_enable": is_repair_enable,
            'allow_quote_cancellation': allow_quote_cancellation,
            'process_do_state': process_do_state,
            'rma_term_condition': rma_term_condition,
            "days_for_rma": days_for_rma,
            "rma_day_apply_on": rma_day_apply_on,
            "repair_location_id": repair_location_id,
            "show_rma_stage": show_rma_stage,
            "enable_notify_admin_4_rma": enable_notify_admin_4_rma,
            "enable_notify_customer_4_rma": enable_notify_customer_4_rma,
            "notify_admin_for_rma_creation": notify_admin_for_rma_creation,
            "notify_customer_for_rma_creation": notify_customer_for_rma_creation,
        })
        return res
