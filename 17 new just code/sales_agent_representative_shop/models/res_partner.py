# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    is_web_sales_agent = fields.Boolean(
        string="Is Sales Agent",
        help="If this checkbox is checked this person will be listed as a sales agent on a website."
    )
    add_sales_person_to_so = fields.Boolean(
        string="Website Order Sales Person ",
        help="If this checkbox is checked then customer sales order commission will be applicable to sales person of this customer also."
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
