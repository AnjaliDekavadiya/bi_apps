from odoo import models, fields, api
import requests
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import test_python_expr
import logging


class WhatsAppAction(models.Model):
    _name = 'whatsapp.action'

    name = fields.Char(string='Name', required=True)
    reply = fields.Char(string='Reply', required=True)
    payload = fields.Char(string='Payload')
    action_type = fields.Selection([
        ('custom_message', 'Custom message'),
        ('template', 'Template'),
        ('function_call', 'Function call'),
        ('code', 'Code')], string='Type', default='custom_message', required=True)
    code = fields.Text(string='Python Code')
    model = fields.Char(string='Model Name')
    function = fields.Char(string='Function Name')
    template_id = fields.Many2one('whatsapp.template', string='Template')
    header = fields.Text(string='Header')
    body = fields.Text(string='Body')
    footer = fields.Text(string='Footer')
    buttons = fields.One2many('whatsapp.button', 'action', string='Buttons')
    
    # @api.constrains('code')
    # def _check_python_code(self):
    #     for action in self.sudo().filtered('code'):
    #         msg = test_python_expr(expr=action.code.strip(), mode="exec")
    #         if msg:
    #             raise ValidationError(msg)
            
    @api.model
    def create(self, vals):
        # if("action_type" in vals and vals["action_type"] == "code"):
        #     if("code" in vals):
        #         msg = test_python_expr(expr=vals["code"].strip(), mode="exec")
        #         if msg:
        #             raise ValidationError(msg)
        if("reply" in vals):
            vals["payload"] = vals["reply"].strip().replace(" ", "_").lower()
        result = super(WhatsAppAction, self).create(vals)

        return result
    
    def write(self, vals):
        # if("action_type" in vals and vals["action_type"] == "code"):
        #     if("code" in vals):
        #         msg = test_python_expr(expr=vals["code"].strip(), mode="exec")
        #         if msg:
        #             raise ValidationError(msg)
        if("reply" in vals):
            vals["payload"] = vals["reply"].strip().replace(" ", "_").lower()
        result = super(WhatsAppAction, self).write(vals)

        return result
    