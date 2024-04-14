from odoo import api, fields, models, _

class LunchProduct(models.Model):
    _inherit = 'lunch.product'
    
    @api.model
    def get_lunch_kiosk_mode_action(self):
        next_action = self.env["ir.actions.actions"]._for_xml_id("lunch_kiosk_mode_adv.lunch_action_kiosk_mode")
        next_action['context'] = {}
        return {'action': next_action}