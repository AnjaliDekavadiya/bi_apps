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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class AgeVerificationConfigSettings(models.Model):
    _name = "age.verification.config.settings"
    _description = 'Age Verification Configuration Settings'

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    _sql_constraints = [('unique_setting', 'unique(name)','You can only modify this settings')]
    name = fields.Char(string="Name", required=True)
    minimum_age = fields.Integer(string="Minimum Age", default=18, help="""
    Enter minimum age to restrict users to enter on the website.
    """, required=True)
    description = fields.Text(string="Description",  translate=True, help="""
    Description used to show age restriction message on popup.
    Description length should not be more than 90 characters.
    """)
    image = fields.Binary(string="Popup Image",help="""
    Replace default image on pupup.
    """)
    enable_age_verification = fields.Boolean(string="Enable Age Verification", help="""
    Enable/Disable age restriction popup on website.
    """)
    deny_message = fields.Text(string="Deny Message", help="""
    Message for those who are not eligible to enter on website.
    Message should not be greater than 53 characters.
    """,
    default="You are not allowed to enter on this website", required=True,
    translate=True)
    terms_condition = fields.Text(string="Terms & Condition",  translate=True)
    dob = fields.Boolean(string="Enable DOB", help="""
    Enable/Disable date of birth option on the popup.
    """)
    is_active = fields.Boolean(string="Active on website", default=False, copy=False)
    website_id = fields.Many2one('website', string="Website", default=_default_website, required=True)
    check_logged_in = fields.Boolean(string="Hide for Loggin User", default=False, help="""
    Disable age verification popup for logged in user
    """)

    select_pages = fields.Selection([('all', 'All'), ('selected', 'Selected')], string="Select Pages",default="all")
    pages_for_popup = fields.Char("Enter Url of Pages", help="Enter multiple url using comma separation")

    @api.constrains('minimum_age')
    def _min_age(self):
        if self.minimum_age <1:
            raise ValidationError("Age should not be less than 1")

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create({'message': _("Currently another Configuration Setting is active. You can only active one setting at a time for a website")})
        return {
            'name': _("Message"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'website.message.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
        }

    def toggle_is_active(self):
        for record in self:
            active_ids = self.search([('is_active', '=', True), ('id', '!=', record.id), ('website_id', '=', record.website_id.id)])
            if active_ids:
                return self.create_wizard()
            record.is_active = not record.is_active

class Website(models.Model):
    _inherit = 'website'

    def get_age_settings(self, **kwargs):
        domain = [('is_active', '=', True)]
        if request.website:
            domain.append(('website_id', '=', request.website.id))
        age_settings_data = self.env['age.verification.config.settings'].search(domain)

        if age_settings_data:
            return age_settings_data
