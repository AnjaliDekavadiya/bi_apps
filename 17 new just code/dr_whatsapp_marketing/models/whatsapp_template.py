from odoo import models, fields, api
import requests
from odoo.exceptions import UserError, ValidationError
import logging


class WhatsAppTemplate(models.Model):
    _name = 'whatsapp.template'

    name = fields.Char(string='Name', required=True)
    header = fields.Text(string='Template Header', default='')
    header_example = fields.Text(string='Template Header Example', default='')
    body = fields.Text(string='Template Body', required=True)
    body_example = fields.Text(string='Template Body Example', default='')
    footer = fields.Text(string='Template Footer', default='')
    template_id = fields.Char(string='Template ID')
    status = fields.Char(string='Status', default='PENDING')
    buttons = fields.One2many('whatsapp.button', 'template', string='Buttons')
    refresh = fields.Boolean(string='Refresh', default=False)
    category = fields.Selection([
        ('AUTHENTICATION', 'Authentication'),
        ('MARKETING', 'Marketing'),
        ('UTILITY', 'Utility')], string='Category')
    language = fields.Selection([
        ('af', 'Afrikaans'),
        ('sq', 'Albanian'),
        ('ar', 'Arabic'),
        ('az', 'Azerbaijani'),
        ('bn', 'Bengali'),
        ('bg', 'Bulgarian'),
        ('ca', 'Catalan'),
        ('zh_CN', 'Chinese (CHN)'),
        ('zh_HK', 'Chinese (HKG)'),
        ('zh_TW', 'Chinese (TAI)'),
        ('hr', 'Croatian'),
        ('cs', 'Czech'),
        ('da', 'Danish'),
        ('nl', 'Dutch'),
        ('en', 'English'),
        ('en_GB', 'English (UK)'),
        ('en_US', 'English (US)'),
        ('et', 'Estonian'),
        ('fil', 'Filipino'),
        ('fi', 'Finnish'),
        ('fr', 'French'),
        ('ka', 'Georgian'),
        ('de', 'German'),
        ('el', 'Greek'),
        ('gu', 'Gujarati'),
        ('ha', 'Hausa'),
        ('hi', 'Hindi'),
        ('hu', 'Hungarian'),
        ('id', 'Indonesian'),
        ('ga', 'Irish'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('kn', 'Kannada'),
        ('kk', 'Kazakh'),
        ('rw_RW', 'Kinyarwanda'),
        ('ko', 'Korean'),
        ('ky_KG', 'Kyrgyz (Kyrgyzstan)'),
        ('lo', 'Lao'),
        ('lv', 'Latvian'),
        ('lt', 'Lithuanian'),
        ('mk', 'Macedonian'),
        ('ms', 'Malay'),
        ('ml', 'Malayalam'),
        ('mr', 'Marathi'),
        ('nb', 'Norwegian'),
        ('fa', 'Persian'),
        ('pl', 'Polish'),
        ('pt_BR', 'Portuguese (BR)'),
        ('pt_PT', 'Portuguese (POR)'),
        ('pa', 'Punjabi'),
        ('ro', 'Romanian'),
        ('ru', 'Russian'),
        ('sr', 'Serbian'),
        ('sk', 'Slovak'),
        ('sl', 'Slovenian'),
        ('es', 'Spanish'),
        ('es_AR', 'Spanish (ARG)'),
        ('es_ES', 'Spanish (SPA)'),
        ('es_MX', 'Spanish (MEX)'),
        ('sw', 'Swahili'),
        ('sv', 'Swedish'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('th', 'Thai'),
        ('tr', 'Turkish'),
        ('uk', 'Ukrainian'),
        ('ur', 'Urdu'),
        ('uz', 'Uzbek'),
        ('vi', 'Vietnamese'),
        ('zu', 'Zulu')], string='Language', required=True, default='en_US')

    @api.model
    def create(self, vals):
        logging.info(vals["buttons"])
        # if(vals["buttons"] and len(vals["buttons"][0]) > 3):
        #     raise ValidationError('Only a maximum of 3 buttons are allowed.')
        
        if("refresh" not in vals):
            vals["refresh"] = False
        
        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')
        business_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp.business_id')

        components = []

        if(vals["header"]):
            header = {
                "type": "HEADER",
                "format": "TEXT",
                "text": vals["header"]
            }
            
            if(vals["header_example"]):
               header["example"] = {
                    "header_text": [vals["header_example"]]
               }
            
            components.append(header)

        body = {
            "type": "BODY",
                    "text": vals["body"]
        }
        
        if(vals["body_example"]):
               body["example"] = {
                    "body_text": [vals["body_example"].split(",")]
               }

        components.append(body)

        if(vals["footer"]):
            components.append({
                "type": "FOOTER",
                "text": vals["footer"],
            })
            
        if(vals["buttons"]):
            buttonsData = vals["buttons"]
            buttons = []
            for button in buttonsData:
                logging.info("NEW BUTTON")
                logging.info(button)
                buttonObj = {}
                buttonObj["type"] = button[2]["payload_type"]
                if(button[2]["payload_type"] == "PHONE"):
                    buttonObj["phone"] = button[2]["payload"]
                elif(button[2]["payload_type"] == "URL"):
                    buttonObj["url"] = button[2]["payload"]
                buttonObj["text"] = button[2]["text"]
                # buttonObj["payload"] = "TEST PAYLOAD"
                if(button[2]["example"]):
                    buttonObj["example"] = [button[2]["example"]]
                buttons.append(buttonObj)
                
            components.append({
                "type": "BUTTONS",
                "buttons": buttons
            })

        data = {
            "name": vals["name"],
            # "category": vals["category"],
            "category": "MARKETING",
            "allow_category_change": True,
            "language": vals["language"],
            "components": components
        }

        if("template_id" not in vals):
         res = requests.post(f'https://graph.facebook.com/v17.0/{business_id}/message_templates?access_token={token}', json=data)
         res = res.json()

         if("error" in res):
               error = ""
               if("message" in res["error"]):
                  error += f'{res["error"]["message"]}\n'
               if("error_user_msg" in res["error"]):
                  error += f'{res["error"]["error_user_msg"]}'
               logging.error(res)
               raise UserError(error)

         vals["status"] = res["status"]
         vals["template_id"] = res["id"]

        result = super(WhatsAppTemplate, self).create(vals)

        return result

    def write(self, vals):
        logging.info("WRITE")
        logging.info(vals)
        
        if("refresh" not in vals):
            vals["refresh"] = False

        if(self.status == "PENDING" and not(vals["refresh"])):
            raise UserError("Cannot update a pending template")
        
        # if(vals["buttons"] and len(vals["buttons"][0]) > 3):
        #     raise ValidationError('Only a maximum of 3 buttons are allowed.')

        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')

        components = []

        if(vals["header"]):
            header = {
                "type": "HEADER",
                "format": "TEXT",
                "text": vals["header"]
            }
            
            if(vals["header_example"]):
               header["example"] = {
                    "header_text": [vals["header_example"]]
               }
            
            components.append(header)

        body = {
            "type": "BODY",
                    "text": vals["body"]
        }
        
        if(vals["body_example"]):
               body["example"] = {
                    "body_text": [vals["body_example"].split(",")]
               }

        components.append(body)

        if(vals["footer"]):
            components.append({
                "type": "FOOTER",
                "text": vals["footer"],
            })

        if(vals["buttons"]):
            buttonsData = vals["buttons"]
            buttons = []
            for button in buttonsData:
                logging.info("NEW BUTTON")
                logging.info(button)
                buttonObj = {}
                buttonObj["type"] = button[2]["payload_type"]
                if(button[2]["payload_type"] == "PHONE"):
                    buttonObj["phone"] = button[2]["payload"]
                elif(button[2]["payload_type"] == "URL"):
                    buttonObj["url"] = button[2]["payload"]
                buttonObj["text"] = button[2]["text"]
                if(button[2]["example"]):
                    buttonObj["example"] = [button[2]["example"]]
                buttons.append(buttonObj)
                
            components.append({
                "type": "BUTTONS",
                "buttons": buttons
            })

        data = {
            "category": vals["category"],
            "components": components
        }
        
        if(not(vals["refresh"])):
            res = requests.post(f'https://graph.facebook.com/v17.0/{self.template_id}?access_token={token}', json=data)
            res = res.json()

            if("error" in res):
                error = res["error"]["message"]
                if("error_user_msg" in res["error"]):
                    error += f'\n{res["error"]["error_user_msg"]}'
                logging.error(res)
                raise UserError(error)
         

        result = super(WhatsAppTemplate, self).write(vals)

        return result

    def unlink(self):
        logging.info("DELETE")
        logging.info(self.template_id)

        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')
        business_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp.business_id')

        res = requests.delete(f'https://graph.facebook.com/v17.0/{business_id}/message_templates?access_token={token}&hsm_id={self.template_id}&name={self.name}')
        res = res.json()

        if("error" in res):
            error = res["error"]["message"]
            if("error_user_msg" in res["error"]):
                error += f'\n{res["error"]["error_user_msg"]}'
            logging.error(res)
            raise UserError(error)

        result = super(WhatsAppTemplate, self).unlink()

        return result

    def fetch_templates(self):
        logging.info("REFRESH")

        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')

        business_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp.business_id')

        res = requests.get(f'https://graph.facebook.com/v17.0/{business_id}/message_templates?access_token={token}')
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
                if(not(template_data)):
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
                                logging.info("EXAMPLE")
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
                    super(WhatsAppTemplate, self).create(vals)