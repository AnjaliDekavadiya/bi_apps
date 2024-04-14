from odoo import models, fields,api
import logging
import json
import html

_logger = logging.getLogger(__name__)

class Feed(models.Model):
    _inherit = "channel.feed"
    
    activity_data = fields.Text('Activity Data',inverse='_set_feed_name')
    
    @api.model
    def evaluate_contact(self,data):
        
        mapp = super(Feed,self).evaluate_contact(data)
        
        data_activity = self.activity_data
        data_dict = data_activity and json.loads(data_activity)
        partner_id = self.env['res.partner.mapping'].search([("remote_id","=", self.remote_id)])
        if(data_dict):
            for act_data in data_dict:
                activity_mapping = self.env["hubspot.activity.mapping"].search([("hubspot_id","=",act_data.get("object_id"))])
                if(not activity_mapping):
                    activity_type = self.env['mail.activity.type'].search([("name","=", act_data.get("type"))])
                    key={
                        'activity_type_id':activity_type.id,
                        'summary': act_data.get('summary'),
                        'note': act_data.get('note'),
                        'user_id': self.env.user.id,
                        'date_deadline' : act_data.get('data_deadline'),
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'res_id': partner_id.local_id.id
                        }
                    res = self.env['mail.activity'].create(key)
                    if(res):
                        data = {
                            "odoo_id": res.id,
                            "activity_type": res.activity_type_id.id,
                            "hubspot_id": act_data.get("object_id"),
                            "activity_object_type": "partner",
                            "crm_partner_id": partner_id.id
                        }
                        resp = self.env['hubspot.activity.mapping'].create(data)
        return mapp
    
    @api.model
    def evaluate_company(self,data):

        mapp = super(Feed,self).evaluate_company(data)

        data_activity = self.activity_data
        data_dict = data_activity and json.loads(data_activity)
        company_id = self.env['res.partner.mapping'].search([("remote_id","=", self.remote_id)])
        if(data_dict):
            for act_data in data_dict:
                activity_mapping = self.env["hubspot.activity.mapping"].search([("hubspot_id","=",act_data.get("object_id"))])
                if(not activity_mapping):
                    activity_type = self.env['mail.activity.type'].search([("name","=", act_data.get("type"))])
                    key={
                        'activity_type_id':activity_type.id,
                        'summary': act_data.get('summary'),
                        'note': act_data.get('note'),
                        'user_id': self.env.user.id,
                        'date_deadline' : act_data.get('data_deadline'),
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'res_id': company_id.local_id.id
                        }
                    res = self.env['mail.activity'].create(key)

                    if(res):
                        data = {
                            "odoo_id": res.id,
                            "activity_type": res.activity_type_id.id,
                            "hubspot_id": act_data.get("object_id"),
                            "activity_object_type": "company",
                            "crm_partner_id": company_id.id
                        }
                        resp = self.env['hubspot.activity.mapping'].create(data)
        return mapp
        
    @api.model
    def evaluate_deal(self,data):

        mapp = super(Feed,self).evaluate_deal(data)

        data_activity = self.activity_data
        data_dict = data_activity and json.loads(data_activity)
        deal_id = self.env['crm.lead.mapping'].search([("remote_id","=", self.remote_id)])
        if(data_dict):
            for act_data in data_dict:
                activity_mapping = self.env["hubspot.activity.mapping"].search([("hubspot_id","=",act_data.get("object_id"))])
                if(not activity_mapping):
                    activity_type = self.env['mail.activity.type'].search([("name","=", act_data.get("type"))])
                    key={
                        'activity_type_id':activity_type.id,
                        'summary': act_data.get('summary'),
                        'note': act_data.get('note'),
                        'user_id': self.env.user.id,
                        'date_deadline' : act_data.get('data_deadline'),
                        'res_model_id': self.env['ir.model']._get('res.partner').id,
                        'res_id': deal_id.local_id.id
                        }
                    res = self.env['mail.activity'].create(key)

                    if(res):
                        data = {
                            "odoo_id": res.id,
                            "activity_type": res.activity_type_id.id,
                            "hubspot_id": act_data.get("object_id"),
                            "activity_object_type": "deal",
                            "crm_lead_id": deal_id.id
                        }
                        resp = self.env['hubspot.activity.mapping'].create(data)
        return mapp
