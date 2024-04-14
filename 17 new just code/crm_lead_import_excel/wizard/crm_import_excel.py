# -*- coding: utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImportFile(models.TransientModel):
    _name = 'lead.import'
    _description = 'Lead Import'

    files = fields.Binary(
        string='Import Excel File',
    )
    filename = fields.Char(
        'File Name'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    import_xls = fields.Selection(selection=[
        ('lead', 'Do you want to import Lead?'),
        ('opportunity', 'Do you want to import Pipeline?')],
        string='Record Type',
        default='lead',
    )

#     @api.multi          #odoo13
    def import_lead(self):
        """this method will import lead and pipeline(opportunity)."""
        crm_obj = self.env['crm.lead']
        team_obj = self.env['crm.team']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        customer_obj = self.env['res.partner']
        sales_person_obj = self.env['res.users']
        crm_lead_tag_obj = self.env['crm.tag']
        campaign_obj = self.env['utm.campaign']
        medium_obj = self.env['utm.medium']
        source_obj = self.env['utm.source']

        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError(_("Please select .xls/xlsx file..."))

        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])

        sheet_number = sheet.row_values(0)
        name = sheet_number.index('Name')
        customer_id = sheet_number.index('Customer')
        company = sheet_number.index('Company Name')
        city_name = sheet_number.index('City')
        country_id = sheet_number.index('Country')
        state_value = sheet_number.index('State')
        website_name = sheet_number.index('Website')
        user_value = sheet_number.index('Salesperson')
        team_value = sheet_number.index('Sales Team')
        contact = sheet_number.index('Contact Name')
        email_value = sheet_number.index('Email')
        job_position_name = sheet_number.index('Job Position')
        phone_value = sheet_number.index('Phone')
        mobile_value = sheet_number.index('Mobile')
        tag_values = sheet_number.index('Tags')
        internal_note = sheet_number.index('Internal Notes')
        campaign_value = sheet_number.index('Campaign')
        medium_value = sheet_number.index('Medium')
        source_value = sheet_number.index('Source')
        referred_value = sheet_number.index('Referred By')
        probability_value = sheet_number.index('Probability')

        alist = []
        row = 1
        number_of_rows = sheet.nrows
        while(row < number_of_rows):
            crm_name = sheet.cell(row, name).value
            if not crm_name:
                raise ValidationError('%s Name should not be empty\
                at row number %s ' % int(row+1))

            crm_customer_id = customer_obj.search(
                [('name', '=', sheet.cell(row, customer_id).value)])
            if not crm_customer_id:
                raise ValidationError('%s Customer is invalid at\
                row number %s ' % (sheet.cell(row, 1).value, row+1))

            company_name = sheet.cell(row, company).value

            city = sheet.cell(row, city_name).value

            crm_country_id = country_obj.search(
                [('name', '=', sheet.cell(row, country_id).value)])
            if not crm_country_id:
                crm_country_id = False
            else:
                crm_country_id = crm_country_id.id

            state_id = state_obj.search(
                [('name', '=', sheet.cell(row, state_value).value)])
            if not state_id:
                state_id = False
            else:
                state_id = state_id.id

            website = sheet.cell(row, website_name).value

            user_id = sales_person_obj.search(
                [('name', '=', sheet.cell(row, user_value).value)])

            team_id = team_obj.search(
                [('name', '=', sheet.cell(row, team_value).value)])

            contact_name = sheet.cell(row, contact).value

            email = sheet.cell(row, email_value).value

            job_position = sheet.cell(row, job_position_name).value

            phone = sheet.cell(row, phone_value).value

            mobile = sheet.cell(row, mobile_value).value

            tag_ids = crm_lead_tag_obj.search(
                [('name', 'in', sheet.cell(row, tag_values).value.split(','))])

            internal_notes = sheet.cell(row, internal_note).value

            campaign_id = campaign_obj.search(
                [('name', '=', sheet.cell(row, campaign_value).value)])

            medium_id = medium_obj.search(
                [('name', '=', sheet.cell(row, medium_value).value)])

            source_id = source_obj.search(
                [('name', '=', sheet.cell(row, source_value).value)])

            referred = sheet.cell(row, referred_value).value

            probability = sheet.cell(row, probability_value).value

            row = row+1
            vals = {
                'name': crm_name,
                'partner_id': crm_customer_id.id,
                'partner_name': company_name,
                'website': website,
                'contact_name': contact_name,
                'email_from': email,
                'phone': int(phone),
                'mobile': int(mobile),
                'tag_ids': [(6, 0, tag_ids.ids)],
                'description': internal_notes,
                'campaign_id': campaign_id.id,
                'medium_id': medium_id.id,
                'source_id': source_id.id,
                'referred': referred,
                'probability': probability,
                'city': city,
                'country_id': crm_country_id,
                'state_id': state_id,
                'function': job_position,
                'user_id': user_id.id,
                'team_id': team_id.id,
                'type': 'lead' if self.import_xls == 'lead' else 'opportunity',
                'company_id': self.company_id.id,
            }
            crm_id = crm_obj.sudo().create(vals).id
            alist.insert(row-1, crm_id)

            if self.import_xls == 'lead':
                #result = self.env.ref('crm.crm_lead_all_leads')
                result = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_all_leads')
                # action_ref = result or False
                # action = action_ref.sudo().read()[0]
                action = result
                action['domain'] = [('type', '=', 'lead')]

            if self.import_xls == 'opportunity':
#                 result = self.env.ref('crm.crm_lead_opportunities_tree_view')
               # result = self.env.ref('crm.crm_case_tree_view_oppor')           #odoo13
                result = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_action_pipeline')
                # action_ref = result or False
                # action = action_ref.sudo().read()[0]
                action = result
                action['domain'] = [('type', '=', 'opportunity')]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'res_model': 'crm.lead',
            'res_id': crm_id,
            'domain': "[('id','in',[" + ','.join(map(str, alist)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': crm_id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
