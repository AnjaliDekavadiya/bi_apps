# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models
from datetime import datetime, timedelta, date
import base64

class InheritCalander(models.Model):
    _inherit = "calendar.event"

    project_id = fields.Many2one("project.project",string="Project")
    analytic_account_id = fields.Many2one("account.analytic.account",string="Analytic Account")
    job_order_id = fields.Many2one("job.order",string="Job Order")
    job_cost_sheet_id = fields.Many2one("job.cost.sheet",string="Job Cost Sheet")
    job_cost_sheet_line_id = fields.Many2many("job.cost.line",string="Job Cost Sheet Line")
    timesheet_ids = fields.One2many('one.many', 'many_id', 'Timesheets')

class Attendee(models.Model):
    """ Calendar Attendee Information """

    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        """ Send mail for event invitation to event attendees.
            :param mail_template: a mail.template record
            :param force_send: if set to True, the mail(s) will be sent immediately (instead of the next queue processing)
        """

        if isinstance(mail_template, str):
            raise ValueError('Template should be a template record, not an XML ID anymore.')
        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return False
        if not mail_template:
            _logger.warning("No template passed to %s notification process. Skipped.", self)
            return False
      
        # get ics file for all meetings
        ics_files = self.mapped('event_id')._get_ics_file()

        

        # send email with attachments
        mail_ids = []
        for attendee in self:
            if attendee.email and attendee.partner_id != self.env.user.partner_id:
                event_id = attendee.event_id.id
                ics_file = ics_files.get(event_id)

                email_values = {
                    'model': None,  # We don't want to have the mail in the tchatter while in queue!
                    'res_id': None,
                }

                attachment_ids = mail_template.attachment_ids.ids
                if ics_file:
                    attachment_ids += self.env['ir.attachment'].create({
                        'datas': base64.b64encode(ics_file),
                        'description': 'invitation.ics',
                        'mimetype': 'text/calendar',
                        'name': 'invitation.ics',
                    }).ids

                body = mail_template._render_field(
                    'body_html',
                    attendee.ids,
                    compute_lang=True)[attendee.id]
                subject = mail_template._render_field(
                    'subject',
                    attendee.ids,
                    compute_lang=True)[attendee.id]
                attendee.event_id.with_context(no_document=True).sudo().message_notify(
                    email_from=attendee.event_id.user_id.email_formatted or self.env.user.email_formatted,
                    author_id=attendee.event_id.user_id.partner_id.id or self.env.user.partner_id.id,
                    body=body,
                    subject=subject,
                    partner_ids=attendee.partner_id.ids,
                    email_layout_xmlid='mail.mail_notification_light',
                    attachment_ids=attachment_ids,
                    force_send=force_send)


       
       
class OneMany(models.Model):
    _name="one.many"
    _description = "One Many" 
    
    many_id = fields.Many2one('calendar.event')
    project_id = fields.Many2one("project.project",string="Project")
    description = fields.Char("Description")
    date = fields.Date("Date")
    task = fields.Char("Task")
    quantity = fields.Float("Quantity")
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    job_cost_center_id = fields.Many2one("job.cost.sheet",string="Job Cost Sheet")
    job_cost_line_id = fields.Many2one("job.cost.line",string="Job Cost Line")

class JobCostSheet(models.Model):
    _inherit="job.cost.sheet"

    @api.depends('sequence')
    def name_get(self):
        result = []
        for account in self:
            name = account.sequence
            result.append((account.id, name))
        return result

    job_meeting_count = fields.Integer(compute='_meeting_count',string="JobCostMeeting")
    
    def _meeting_count(self):
        for s_id in self:   
            support_ids = self.env['calendar.event'].search([("job_cost_sheet_id",'=',self.id)])
            s_id.job_meeting_count = len(support_ids)
        return
        
    
    def job_calendar_button(self):
        self.ensure_one()
        return {
            'name': 'Job Cost Meeting',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'calendar.event',
            'domain': [("job_cost_sheet_id",'=',self.id)],
            'context': {
                'default_project_id': self.project_id.id,
                'default_analytic_account_id' : self.analytic_ids.id,
                'default_job_order_id' : self.job_order_id.id,
                'default_job_cost_sheet_id' : self.id,
            }
        }       
class JobLine(models.Model):
    _inherit ="job.cost.line"
    _rec_name="job_type_id"

class InheritProject(models.Model):
    _inherit ="project.project"

    job_meeting_proj_count = fields.Integer(compute='_proj_meeting_count',string="JobCostMeeting")
    
    def _proj_meeting_count(self):
        for s_id in self:   
            support_ids = self.env['calendar.event'].search([("project_id",'=',self.id)])
            s_id.job_meeting_proj_count = len(support_ids)
        return
        

    def job_meeting_button(self):
        self.ensure_one()
        return {
            'name': 'Job Cost Meeting',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'calendar.event',
            'domain': [("project_id",'=',self.id)],
        }

class InheritProject(models.Model):
    _inherit ="job.order"

    job_meeting_job_count = fields.Integer(compute='_job_meeting_count',string="JobCostMeeting")


    
    def _job_meeting_count(self):
        for s_id in self:   
            support_ids = self.env['calendar.event'].search([("job_order_id",'=',self.id)])
            s_id.job_meeting_job_count = len(support_ids)
        return


    def job_order_meeting_button(self):
        self.ensure_one()
        return {
            'name': 'Job Cost Meeting',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'calendar.event',
            'domain': [("job_order_id",'=',self.id)],

        }