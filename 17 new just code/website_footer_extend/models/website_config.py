# -*- encoding: utf-8 -*-
from odoo import models, fields

class website(models.Model):
    _inherit = 'website'
    
    privacy_in_footer = fields.Boolean("Privacy in footer?")
    term_of_use_in_footer = fields.Boolean("Term of use in footer?")
    legal_disclosure_in_footer = fields.Boolean("Legal Disclosure in footer?")
    copyright_in_footer = fields.Boolean("Copyright in footer?")
    trademark_in_footer = fields.Boolean("Trademark in footer?")
    
    
class website_config_settings(models.TransientModel):
    #_inherit = 'website.config.settings'
    _inherit = 'res.config.settings'                           # odoo 11

    privacy_in_footer = fields.Boolean(related='website_id.privacy_in_footer',string="Privacy in footer?",readonly=False)
    term_of_use_in_footer = fields.Boolean(related='website_id.term_of_use_in_footer',string="Term of use in footer?",readonly=False)
    legal_disclosure_in_footer = fields.Boolean(related='website_id.legal_disclosure_in_footer',string="Legal Disclosure in footer?",readonly=False)
    copyright_in_footer = fields.Boolean(related='website_id.copyright_in_footer',string="Copyright in footer?",readonly=False)
    trademark_in_footer = fields.Boolean(related='website_id.trademark_in_footer',string="Trademark in footer?",readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
