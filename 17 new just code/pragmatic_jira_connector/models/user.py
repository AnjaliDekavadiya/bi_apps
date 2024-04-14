# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
import sys
import random


class JiraUser(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        if 'disable_mail_mail' in self.env.context:
            return
        super(JiraUser, self).action_reset_password()

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.getall('user/search?query="."&includeInactive=true')
            # print("\n\n\n query=================",response)
            for r in response:
                self.process_response(r)

    def process_response(self, response):
        # print("\n\n response=================",response)
        if 'errorMessages' in response:
            key = response['errorMessages'][0][len('The user with the key \''):-len('\' does not exist')]
            user_dict = dict(
                jira_accountId=key,
                short_name=key,
                login=key,
                name=key,
                jira_active=False,
            )
        else:
            login = ''
            final_user_name = ''
            rand = random.randint(11, 99999)
            first_name = list(response['displayName'].split())
            if first_name[0] and first_name[-1]:
                final_user_name = first_name[0] + "_" + first_name[-1] + "_" + str(rand)
            else:
                final_user_name = first_name[0]
            if 'emailAddress' not in response:
                login = final_user_name
            else:
                login = final_user_name

            user_dict = dict(
                jira_accountId=response['accountId'],
                login=login,
                name=response['displayName'],
                jira_active=response['active'],
                groups_id=[(6, 0, [self.env.ref('base.group_portal').id])]
            )
        user = self.env['res.users'].search([('jira_accountId', '=', user_dict['jira_accountId'])])
        if not user:
            if response and response.get("displayName"):
                user_ids = self.env['res.users'].search([('name', '=', response.get("displayName"))])
                if user_ids and user_ids.jira_active == False:
                    user_ids.write({'jira_accountId': response['accountId']})
                else:
                    user = self.env['res.users'].sudo().create(user_dict)
                    self.env['hr.employee'].sudo().create(dict(user_id=user.id))
        else:
            pass
        return user

    def key_operation(self, account_id):
        user = self.search([('jira_accountId', '=', account_id)])
        # print("\n\n user-------------->>>>>>>>>",user)
        if not user:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                user = self.process_response(company_id.get('user?accountId=' + account_id, check=False).json())
                # print("\n\n=============",user)
        return user

    def jira_short_name(self, name):
        user = self.search([('short_name', '=', name)])
        if not user:
            self.receive_all()
            user = self.search([('short_name', '=', name)])
        return user

    def get_user_by_dict(self, user_dict):
        # print("\n\n get_user_by_dict=============",user_dict,self)
        if 'key' in user_dict:
            return self.key_operation(user_dict['key'])
        else:
            return self.key_operation(user_dict['accountId'])

    jira_accountId = fields.Char()
    short_name = fields.Char()
    name = fields.Char(required=1)
    jira_active = fields.Boolean(default=False)
