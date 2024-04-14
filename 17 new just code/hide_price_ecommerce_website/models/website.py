# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Website(models.Model):
    _inherit = "website"

    is_hide_price_on_shop_custom = fields.Boolean(
        string="Hide Price on Shop",
    )
    contact_person_name_custom = fields.Char(
        string = 'Contact Person Name',
    )
    contact_person_email_custom = fields.Char(
        string="Contact Person Email"
    )
    contact_person_phone_custom = fields.Char(
        string = "Contact Person Phone"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
