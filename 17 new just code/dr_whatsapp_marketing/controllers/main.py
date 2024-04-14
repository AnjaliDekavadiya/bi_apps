# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import yaml
from heyoo import WhatsApp

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

from werkzeug.exceptions import Forbidden

_logger = logging.getLogger(__name__)

class WhatsappController(http.Controller):
    _return_url = "/whatsapp/callback"

    @http.route(
        _return_url, type='http', auth='public', methods=['GET'], csrf=False,
        save_session=False
    )
    def ping(self, **data):
        verify_token = request.env['ir.config_parameter'].sudo().get_param('whatsapp.verify_token')
        mode = data.get('hub.mode')
        token = data.get('hub.verify_token')
        challenge = data.get('hub.challenge')

        if mode and token and mode == "subscribe" and token == verify_token:
            return challenge
        else:
            raise Forbidden()
    
    @http.route(
        _return_url, type='http', auth='public', methods=['POST'], csrf=False,
        save_session=False
    )
    def listener(self, **data):
        data = request.httprequest.data
        data = yaml.load(data)
        token = request.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')
        phone_number_id = request.env['ir.config_parameter'].sudo().get_param('whatsapp.phone_id')
        whatsapp = WhatsApp(token, phone_number_id=phone_number_id)

        changed_field = whatsapp.changed_field(data)
        isMessageStatusChange = False
        
        logging.info(data)
        
        try:
            if("statuses" in data["entry"][0]["changes"][0]["value"]):
                isMessageStatusChange = True
        except:
            logging.info("No message status change")
        
        if isMessageStatusChange:
            wamid = data["entry"][0]["changes"][0]["value"]["statuses"][0]["id"]
            
            wamid_res = request.env['whatsapp.wamid'].sudo().search([('wamid', '=', wamid)], limit=1)
            if wamid_res:
                status = data["entry"][0]["changes"][0]["value"]["statuses"][0]["status"]
                wamid_res.sudo().write({ "is_" + status: 1 })  
        elif changed_field == "message_template_status_update":
            status = data["entry"][0]["changes"][0]["value"]["event"]
            template_id = data["entry"][0]["changes"][0]["value"]["message_template_id"]
            
            template = request.env['whatsapp.template'].sudo().search([('template_id', '=', template_id)], limit=1)
            
            if(template):
                template.sudo().write({ "status": status })
        elif changed_field == "messages":
            type = whatsapp.get_message_type(data)
            phone = whatsapp.get_mobile(data)
            
            if("context" in data["entry"][0]["changes"][0]["value"]["messages"][0]):
                wamid = data["entry"][0]["changes"][0]["value"]["messages"][0]["context"]["id"]
                wamid_res = request.env['whatsapp.wamid'].sudo().search([('wamid', '=', wamid)], limit=1)
                if wamid_res:
                    user_response_type = data["entry"][0]["changes"][0]["value"]["messages"][0]["type"]
                    user_response = ""
                    if(user_response_type == "button"):
                        user_response = data["entry"][0]["changes"][0]["value"]["messages"][0]["button"]["payload"].lower().replace(" ", "_")
                    elif(user_response_type == "text"):
                        user_response = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"].lower().replace(" ", "_")
                    wamid_res.sudo().write({ "response": user_response, "is_replied": 1 })

            message = None
            if type == "text":
                message = whatsapp.get_message(data)
            elif type == "interactive":
                message_response = whatsapp.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message = message_response[interactive_type]["id"]
                
            if(message):
                name = whatsapp.get_name(data)
                message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
                message_data["name"] = name
                
                action_res = request.env['whatsapp.action'].sudo().search([('payload', '=', str(message).strip().replace(" ", "_").lower())], limit=1)
                if(action_res):
                    self.send_reply(action_res, phone, message_data)
                else:
                    action_res = request.env['whatsapp.action'].sudo().search([('payload', '=', 'default_message')], limit=1)
                    if(action_res):
                        self.send_reply(action_res, phone, message_data)
                    else:
                        whatsapp.send_message("Our team will get back to you shortly.", phone)

        return "ok"
    
    @http.route(
        "/whatsapp/test", type='http', auth='public', methods=['POST'], csrf=False,
        save_session=False
    )
    def test(self, **data):
        data = request.httprequest.data
        data = yaml.load(data)
        
        logging.info(data)
        
        # res = safe_eval(data["code"].strip(), mode='exec')
        res_eval = exec(data["code"].strip())
        
        # logging.info("SAFE EVAL RESULT: " + str(res))
        logging.info("EVAL RESULT: " + str(res_eval))

        return "ok"
    
    def send_reply(self, action, phone, data = None):
        token = request.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')
        phone_number_id = request.env['ir.config_parameter'].sudo().get_param('whatsapp.phone_id')
        whatsapp = WhatsApp(token, phone_number_id=phone_number_id)
        
        if(action["action_type"] == "custom_message"):
            if("buttons" in action and len(action["buttons"]) > 0):
                if(len(action["buttons"]) > 3):
                    buttons = []
                    for button in action["buttons"]:
                        buttons.append({
                            "title": button.text,
                            "id": button.payload.strip().replace(" ", "_").lower(),
                            "description": button.description if button.description else ""
                        })
                    
                    button_obj = { "action": { "button": "Choices", "sections": { "title": "Choices", "rows": buttons } }, "body": action["body"] }
                    
                    if("header" in action and action["header"]):
                        button_obj["header"] = action["header"]
                        
                    if("footer" in action  and action["footer"]):
                        button_obj["footer"] = action["footer"]
                        
                    whatsapp.send_button(
                        recipient_id=phone,
                        button=button_obj
                    )
                else:
                    buttons = []
                    for button in action["buttons"]:
                        buttons.append({
                            "type": "reply",
                            "reply": {
                                "title": button.text,
                                "id": button.payload.strip().replace(" ", "_").lower(),
                            }
                        })
                    
                    button_obj = { "type": "button", "action": { "buttons": buttons }, "body": { "text": action["body"] } }
                    
                    if("header" in action  and action["header"]):
                        button_obj["header"] = { "type": "text", "text": action["header"] }
                        
                    if("footer" in action  and action["footer"]):
                        button_obj["footer"] = { "text": action["footer"] }
                    
                    whatsapp.send_reply_button(
                        recipient_id=phone,
                        button=button_obj,
                    )
            else:
                whatsapp.send_message(action["body"], phone)
        elif(action["action_type"] == "template"):
            if("header" not in action):
                action["header"] = ""
                
            if("body" not in action):
                action["body"] = []
                
            if("buttons" not in action):
                action["buttons"] = []
                
            request.env['whatsapp.message'].send_message([phone], action["template_id"]["id"], action["body"], action["buttons"], action["header"])
        elif(action["action_type"] == "function_call" and data):
            model = request.env[action["model"]].sudo()
            func = getattr(model, action["function"])
            func(data)
        elif(action["action_type"] == "code"):
            # safe_eval(action["code"].strip(), mode='exec')
            exec(action["code"].strip())