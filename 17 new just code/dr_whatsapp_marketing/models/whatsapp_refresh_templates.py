from odoo import models, fields
from odoo.exceptions import UserError
from heyoo import WhatsApp
import requests
import logging


class WhatsAppRefreshTemplates(models.TransientModel):
    _name = 'whatsapp.refresh.templates'

    def fetch_templates(self):
        logging.info("REFRESH")

        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')

        business_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp.business_id')

        res = requests.get(
            f'https://graph.facebook.com/v17.0/{business_id}/message_templates?access_token={token}')
        res = res.json()
        logging.info(res)
        if("error" in res):
            error = res["error"]["message"]
            if("error_user_msg" in res["error"]):
                error += f'\n{res["error"]["error_user_msg"]}'
            logging.error(res)
            raise UserError(error)
        if("data" in res):
            data = res["data"]
            for template in data:
                template_data = self.env['whatsapp.template'].search([('template_id', '=', template['id'])], limit=1)
                vals = {}
                vals["template_id"] = template["id"]
                vals["name"] = template["name"]
                vals["status"] = template["status"]
                vals["language"] = template["language"]
                vals["category"] = template["category"]
                for component in template["components"]:
                    if component["type"] == "HEADER" and "text" in component:
                        vals["header"] = component["text"]
                        if("example" in component and "header_text" in component["example"]):
                            vals["header_example"] = component["example"]["header_text"]
                    elif component["type"] == "BODY" and "text" in component:
                        vals["body"] = component["text"]
                        if("example" in component and "body_text" in component["example"]):
                            logging.info(component["example"]["body_text"])
                            vals["body_example"] = ",".join(component["example"]["body_text"][0])
                    elif component["type"] == "FOOTER" and "text" in component:
                        vals["footer"] = component["text"]
                    elif component["type"] == "BUTTONS" and "buttons" in component:
                        logging.info("BUTTONS")
                        logging.info(component["buttons"])
                        buttons = []
                        count = 0
                        for button in component["buttons"]:
                            buttonData = { "text": button["text"], "payload_type": button["type"] }
                            if(button["type"] == "URL" or button["type"] == "PHONE"):
                                buttonData["payload"] = button[button["type"].lower()]
                            if("example" in button):
                                buttonData["example"] = button["example"][0]
                            else:
                                buttonData["example"] = ""
                            buttons.append([0, count, buttonData])
                            count += 1
                        vals["buttons"] = buttons
                            
                if("header" not in vals):
                    vals["header"] = ""
                if("header_example" not in vals):
                    vals["header_example"] = ""
                if("body_example" not in vals):
                    vals["body_example"] = ""
                if("footer" not in vals):
                    vals["footer"] = ""
                if("buttons" not in vals):
                    vals["buttons"] = []
                    
                if(not(template_data)):
                    self.env['whatsapp.template'].sudo().create(vals)
                else:
                    vals["refresh"] = True
                    template_data.sudo().write(vals)
