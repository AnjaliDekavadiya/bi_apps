# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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

from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class WhatsappSettings(models.Model):
    _name="whatsapp.settings"
    _description = "Whatsapp Settings"

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    _sql_constraints = [('unique_setting', 'unique(name)','You can only modify this settings')]

    name = fields.Char(string="Name",required=True)
    is_active = fields.Boolean(string="Activate this settings", help="Enabling this will enable whatsapp widget in your website.", copy=False)
    website_id = fields.Many2one(comodel_name="website",string="Website", default=_default_website, required=True)
    heading_title = fields.Char(string="Heading Title", translate=True, default="Whatsapp chatbot Support")
    description = fields.Text(string="Description", translate=True, default="If any query please ask to support team")
    button_color = fields.Char(string='Button Color',
        help="Provide the color for whatsapp button.",
        default="#4FCE5D")
    popup_background_color = fields.Char(string='Popup Background Color',
        help="Provide the color for popup background.",
        default="#DCF8C6")
    heading_color = fields.Char(string='Heading Color',
        help="Provide the heading color for whatsapp chat box.",
        default="#075E54")
    heading_title_color = fields.Char(string='Heading Title Color',
        help="Provide the heading Title color for whatsapp chat box.",
        default="#ffffff")
    text_color = fields.Char(string='Text Color',
        help="Provide the text color for whatsapp chat box.",
        default="#0d0c0c")
    description_color = fields.Char(string='Description Color',
        help="Provide the description color for whatsapp chat box.",
        default="#0d0c0c")
    time = fields.Boolean(string="Time", help="Enable/Disable time field in chatbox")
    member_type = fields.Boolean(string="Member Type", help="Enable/Disable member type field in chatbox")
    chatbot_position = fields.Selection([('chatbot_left','Left'),('chatbot_right','Right')],string="Position",default="chatbot_left")
    
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            prev_rec = self.search_count([('website_id','=',vals['website_id'])])
            if not prev_rec:
                vals['is_active'] = True
            res = super(WhatsappSettings,self).create(vals)
            return res

    def unlink(self):
        for rec in self:
            if rec.is_active:
                raise UserError('You cannot delete active settings, make another settings active to delete this settings.')
        return super(WhatsappSettings, self).unlink()

    def activate_settings(self):
        for rec in self:
            rec.is_active = True
            record = self.sudo().search([('website_id','=',rec.website_id.id),('id','!=',rec.id),('is_active','=',True)])
            if record.is_active:
                record.is_active = False

    def deactivate_settings(self):
        for rec in self:
            rec.is_active = False

class WhatsappMemberType(models.Model):
    _name="whatsapp.member.type"
    _description = "Whatsapp Member Type"

    _sql_constraints = [('unique_member_type', 'unique(name)', 'Member type already exist')]
    name = fields.Char('Name',required="True")
    sequence = fields.Integer('Sequence',required="True")

class Website(models.Model):
    _inherit = 'website'

    def get_whatsapp_settings(self, **kwargs):
        domain = [('is_active', '=', True)]
        if request.website:
            domain.append(('website_id', '=', request.website.id))

        whatsapp_settings_data = self.env['whatsapp.settings'].search(domain)
        if whatsapp_settings_data:
            return whatsapp_settings_data

        return False

    def get_active_whatsapp_members(self):
        partner_ids = request.env['res.partner'].sudo().search([
            ('whatsapp_support_member','=',True),
            ('status', '=', 'active'),
        ])
        if not partner_ids:
            return False
        partner_ids = partner_ids.sudo().filtered(lambda partner: partner.website_id.id == request.website.id or not partner.website_id)
        return partner_ids
