# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request

class PosScreenConfig(models.Model):
    _name = 'pos.kitchen.screen.config'
    _description = "Kitchen Screen Config"

    name = fields.Char(string="Name")
    url = fields.Char(string="Kitchen Display Url", compute="compute_url")
    pos_config_ids = fields.Many2many('pos.config', string="Allowed POS")
    pos_category_ids = fields.Many2many(
        'pos.category', string="Allowed POS Categories")
    ip_address = fields.Char(string="IP Address")
    orders_on_grid = fields.Selection(
        [('2', 2), ('3', 3), ('4', 4), ('6', 6)], string="Orders On Grid Screen", default="3")
    queue_order = fields.Selection(
        [('new2old', "Newer To Older"), ('old2new', "Older To Newer")], default="new2old")
    is_changed = fields.Boolean(default=False, string="Is Changed")

    @api.depends('pos_config_ids')
    def compute_url(self):
        for self_obj in self:
            if(self_obj.ip_address):
                 self_obj.url = '{}/pos/kitchen/{}/screen'.format(
                    self_obj.ip_address, self_obj.id)
            else:
                self_obj.url = '{}pos/kitchen/{}/screen'.format(request.httprequest.host_url, self_obj.id)
           
    def redirect_customer_screen(self):
        if self.url:
            url = self.url
        else:
            base_url = request.httprequest.host_url
            url = '{}pos/kitchen/{}/screen'.format(base_url, self.id)
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
            
class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_kitchen_screen = fields.Many2many(
        'pos.kitchen.screen.config', string="Pos Kitchen Screen")
    auto_accept = fields.Boolean('Auto Accept kitchen order', default=False)

    def open_screen_configuration(self):
        view_id_tree = self.env.ref(
            'pos_kitchen_screen.pos_screen_conf_form').id
        pos_screen_data = self.env['pos.kitchen.screen.config'].search(
            [("pos_config_ids", '=ilike', self.id)])
        if pos_screen_data and pos_screen_data.id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'pos.kitchen.screen.config',
                'view_mode': 'form',
                'res_id': pos_screen_data.id,
                'view_id': view_id_tree,
                'target': 'current'
            }
        else:
            raise UserError("No Kitchen Screen Settings available for this POS.")
        
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pos_kitchen_screen = fields.Many2many(
        related='pos_config_id.pos_kitchen_screen', readonly=False)

    pos_auto_accept = fields.Boolean(
        related='pos_config_id.auto_accept', readonly=False)
     
class ProductProduct(models.Model):
    _inherit = "product.product"

    related_order = fields.Many2one('pos.order', string="related order")
    related_kitchen_order = fields.Many2one('pos.kitchen.order', string="Related Kitchen order")