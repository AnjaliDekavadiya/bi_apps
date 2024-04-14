# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _, tools
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import random
from odoo.tools import email_re
import uuid


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    state = fields.Selection([('customer_replied', 'Customer Replied'),
                              ('staff_replied', 'Staff Replied')],
                             string="Replied Status",
                             default='customer_replied',
                             required=True,
                             tracking=True)

    sh_user_ids = fields.Many2many('res.users', string="Assign Multi Users",domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    sh_due_date = fields.Datetime(
        'Reminder Due Date', default=datetime.today())
    category_id = fields.Many2one('sh.helpdesk.category',
                                  string="Category",
                                  tracking=True)
    sub_category_id = fields.Many2one('sh.helpdesk.subcategory',
                                      string="Sub Category")
    person_name = fields.Char(string='Person Name', tracking=True)
    replied_date = fields.Datetime('Replied Date', tracking=True)
    sh_ticket_alarm_ids = fields.Many2many('sh.ticket.alarm',
                                           string='Ticket Reminders')
    close_date = fields.Datetime(string='Close Date', tracking=True)
    close_by = fields.Many2one('res.users', string='Closed By', tracking=True)
    comment = fields.Text(string="Comment", tracking=True, translate=True)
    cancel_date = fields.Datetime(string='Cancelled Date', tracking=True)
    cancel_by = fields.Many2one('res.users',
                                string='Cancelled By',
                                tracking=True)
    product_ids = fields.Many2many('product.product', string='Products')
    cancel_reason = fields.Char("Cancel Reason", tracking=True, translate=True)
    priority_new = fields.Selection([('none', 'No Rating yet'),('ko', 'Dissatisfied'),
        ('ok', 'Okay'),('top', 'Satisfied')],
        string="Customer Rating",tracking=True,compute='_compute_rating')
    customer_comment = fields.Text("Customer Comment", tracking=True,compute='_compute_rating')
    done_stage_boolean = fields.Boolean('Done Stage',
                                        compute='_compute_stage_booleans',
                                        store=True)
    cancel_stage_boolean = fields.Boolean('Cancel Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    reopen_stage_boolean = fields.Boolean('Reopened Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    closed_stage_boolean = fields.Boolean('Closed Stage',
                                          compute='_compute_stage_booleans',
                                          store=True)
    open_boolean = fields.Boolean('Open Ticket',
                                  compute='_compute_stage_booleans',
                                  store=True)

    ticket_from_website = fields.Boolean('Ticket From Website')
    cancel_button_boolean = fields.Boolean(
        "Cancel Button",
        compute='_compute_cancel_button_boolean',
        search='_search_cancel_button_boolean')
    done_button_boolean = fields.Boolean(
        "Done Button",
        compute='_compute_done_button_boolean',
        search='_search_done_button_boolean')
    sh_display_multi_user = fields.Boolean(
        compute="_compute_sh_display_multi_user")

    category_bool = fields.Boolean(string='Category Setting',
                                   related='company_id.category',
                                   store=True)
    sub_category_bool = fields.Boolean(string='Sub Category Setting',
                                       related='company_id.sub_category',
                                       store=True)
    rating_bool = fields.Boolean(string='Rating Setting',
                                 related='company_id.customer_rating', store=True)
    sh_display_product = fields.Boolean(compute='_compute_sh_display_product')
    ticket_allocated = fields.Boolean("Allocated")
    description = fields.Html(string="Description")
    sh_ticket_report_url = fields.Char(compute='_compute_report_url')
    report_token = fields.Char("Access Token")
    portal_ticket_url_wp = fields.Char(compute='_compute_ticket_portal_url_wp')
    form_url = fields.Char('Form Url', compute='_compute_form_url')
    
    task_count = fields.Integer('Tasks', compute='_compute_task_count')
    task_ids = fields.Many2many('project.task', string='Task')
    
    sh_lead_ids = fields.Many2many("crm.lead", string="Leads/Opportunities")
    lead_count = fields.Integer(
        'Lead', compute='_compute_lead_count_helpdesk')
    opportunity_count = fields.Integer(
        'Opportunity', compute='_compute_opportunity_count_helpdesk')

    sh_purchase_order_ids = fields.Many2many("purchase.order", string="Orders")
    purchase_order_count = fields.Integer(
        'Purchase Order', compute='_compute_purchase_order_count_helpdesk')
    
    sh_sale_order_ids = fields.Many2many("sale.order", string="Order")
    sale_order_count = fields.Integer(
        'Order ', compute='_compute_sale_order_count_helpdesk')

    sh_invoice_ids = fields.Many2many("account.move",'sh_account_move_helpdesk_ticket_rel', string="Invoice")
    sh_invoice_count = fields.Integer(
        'Invoice ', compute='sh_compute_invoice_count_helpdesk')
    
    sh_merge_ticket_ids = fields.Many2many('helpdesk.ticket','model_merge_helpdesk_ticket',"helpdesk","ticket", string='Merge Tickets')

    sh_merge_ticket_count = fields.Integer(compute="_compute_count_merge_ticket")
    helpdesk_stage_history_line=fields.One2many("sh.helpdesk.ticket.stage.info",'stage_task_id',string="Stage History Line")
    

    def _compute_form_url(self):
        if self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            url_str = ''
            action = self.env.ref('helpdesk.helpdesk_ticket_action_main_my').id
            if base_url:
                url_str += str(base_url) + '/web#'
            for rec in self:
                url_str += 'id='+str(rec.id)+'&action='+str(action) + \
                    '&model=helpdesk.ticket&view_type=form'
                rec.form_url = url_str

    def _compute_ticket_portal_url_wp(self):
        for rec in self:
            rec.portal_ticket_url_wp = False
            if rec.company_id.sh_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                ticket_url = base_url + rec.get_portal_url()
                self.sudo().write({'portal_ticket_url_wp': ticket_url})

    def _get_token(self):
        """ Get the current record access token """
        if self.report_token:
            return self.report_token
        else:
            report_token = str(uuid.uuid4())
            self.write({'report_token': report_token})
            return report_token

    def get_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/ht/' + '%s?access_token=%s' % (self.id,
                                                            self._get_token())
        return url

    def _compute_report_url(self):
        for rec in self:
            rec.sh_ticket_report_url = False
            if rec.company_id.sh_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                ticket_url = "%0A%0A Click here to download Ticket Document : %0A" + \
                    base_url+rec.get_download_report_url()
                self.sudo().write({
                    'sh_ticket_report_url':
                    base_url + rec.get_download_report_url()
                })

    def _track_template(self, changes):
        res = super(HelpdeskTicket, self)._track_template(changes)
        ticket = self[0]
        if 'stage_id' in changes and ticket.stage_id.template_id:
            template_ids = []
            template_ids.append(self.env.ref(
                'sh_helpdesk_enterprise.sh_ticket_done_template_enterprise').id)
            template_ids.append(self.env.ref(
                'sh_helpdesk_enterprise.sh_ticket_cancelled_template_enterprise').id)
            template_ids.append(self.env.ref(
                'sh_helpdesk_enterprise.sh_ticket_reopened_template_enterprise').id)
            template_ids.append(self.env.ref(
                'sh_helpdesk_enterprise.sh_ticket_user_allocation_template_enterprise').id)
            if ticket.stage_id.template_id.id in template_ids:
                res['stage_id'] = (ticket.stage_id.template_id, {
                    'auto_delete_message': False,
                    'subtype_id': False,
                    'email_layout_xmlid': 'custom_layout'
                }
                )
        return res

    def action_send_whatsapp(self):
        self.ensure_one()
        if not self.partner_id.mobile:
            raise UserError(_("Partner Mobile Number Not Exist !"))
        template = self.env.ref(
            'sh_helpdesk_enterprise.sh_send_whatsapp_email_template')

        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_ids': self.ids,
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_is_wp': True,
        }
        attachment_ids = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'helpdesk.ticket'),
            ('res_id', '=', str(self.id))
        ])
        if attachment_ids:
            ctx.update({'attachment_ids': [(6, 0, attachment_ids.ids)]})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Ticket', self.name)

    def preview_ticket(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def action_mass_update_wizard(self):
        return {
            'name': 'Mass Update Ticket',
            'res_model': 'sh.helpdesk.ticket.mass.update.wizard',
            'view_mode': 'form',
            'context': {
                'default_helpdesks_ticket_ids': [(6, 0, self.env.context.get('active_ids'))],
                'default_check_sh_display_multi_user': self.env.user.company_id.sh_display_multi_user
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('partner_id') and vals.get('partner_email', False):
                emails = email_re.findall(vals.get('partner_email') or '')
                email = emails and emails[0] or ''
                name = str(vals.get('partner_email')).split('"')
                partner_id = self.env['res.partner'].create({
                    'name':
                    name[1] if name and len(name)>1 else name[0],
                    'email':
                    email,
                    'company_type':
                    'person',
                })
                vals.update({
                    'partner_id': partner_id.id,
                    'partner_email': email,
                    'person_name': partner_id.name,
                })
            number = random.randrange(1, 10)
            company_id = self.env.company
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if company_id.new_stage_id:
                vals['stage_id'] = company_id.new_stage_id.id

            vals['color'] = number
        res = super(HelpdeskTicket, self).create(vals_list)
        return res

    @api.depends('company_id')
    def _compute_sh_display_product(self):
        if self:
            for rec in self:
                rec.sh_display_product = False
                if rec.company_id and rec.company_id.sh_configure_activate:
                    rec.sh_display_product = True

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id:
            sub_category_ids = self.env['sh.helpdesk.subcategory'].sudo().search([
                ('parent_category_id', '=', self.category_id.id)
            ]).ids
            return {
                'domain': {
                    'sub_category_id': [('id', 'in', sub_category_ids)]
                }
            }
        else:
            self.sub_category_id = False

    @api.depends('company_id')
    def _compute_sh_display_multi_user(self):
        if self:
            for rec in self:
                rec.sh_display_multi_user = False
                if rec.company_id and rec.company_id.sh_display_multi_user:
                    rec.sh_display_multi_user = True

    @api.depends('stage_id')
    def _compute_cancel_button_boolean(self):
        if self:
            for rec in self:
                rec.cancel_button_boolean = False
                if rec.stage_id.is_cancel_button_visible:
                    rec.cancel_button_boolean = True

    @api.depends('stage_id')
    def _compute_done_button_boolean(self):
        if self:
            for rec in self:
                rec.done_button_boolean = False
                if rec.stage_id.is_done_button_visible:
                    rec.done_button_boolean = True

    @api.depends('stage_id')
    def _compute_stage_booleans(self):
        if self:
            for rec in self:
                rec.cancel_stage_boolean = False
                rec.done_stage_boolean = False
                rec.reopen_stage_boolean = False
                rec.closed_stage_boolean = False
                rec.open_boolean = False
                if rec.stage_id.id == rec.company_id.cancel_stage_id.id:
                    rec.cancel_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.done_stage_id.id:
                    rec.done_stage_boolean = True
                    rec.open_boolean = True
                elif rec.stage_id.id == rec.company_id.reopen_stage_id.id:
                    rec.reopen_stage_boolean = True
                    rec.open_boolean = False
                elif rec.stage_id.id == rec.company_id.close_stage_id.id:
                    rec.closed_stage_boolean = True
                    rec.open_boolean = True

    def action_approve(self):
        self.ensure_one()
        if self.stage_id.sh_next_stage:
            self.stage_id = self.stage_id.sh_next_stage.id

    def action_reply(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self.company_id.reply_mail_template_id.id
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_done(self):
        self.ensure_one()
        if self.company_id.done_stage_id:
            self.env.cr.execute(''' UPDATE helpdesk_ticket set stage_id=%s where id=%s ''',
                [self.company_id.done_stage_id.id,self.id])

    def action_closed(self):
        self.ensure_one()
        stage_id = self.company_id.close_stage_id
        if stage_id:
            self.env.cr.execute(''' UPDATE helpdesk_ticket set stage_id=%s,close_date=%s,close_by=%s,closed_stage_boolean=True where id=%s ''',
                [stage_id.id,fields.Datetime.now(),self.env.user.id,self.id])

    def action_cancel(self):
        self.ensure_one()
        stage_id = self.company_id.cancel_stage_id
        if stage_id:
            self.env.cr.execute(''' UPDATE helpdesk_ticket set stage_id=%s,cancel_date=%s,cancel_by=%s,cancel_stage_boolean=True where id=%s ''',
                [stage_id.id,fields.Datetime.now(),self.env.user.id,self.id])

    def action_open(self):
        self.write({
            'stage_id': self.company_id.reopen_stage_id.id,
            'open_boolean': True,
        })

    def write(self, vals):
        if vals.get('state'):
            if vals.get('state') == 'customer_replied':
                if self.env.user.company_id.sh_customer_replied:
                    for rec in self:
                        if rec.stage_id.id != self.env.user.company_id.new_stage_id.id:
                            vals.update({
                                'stage_id':
                                self.env.user.company_id.
                                sh_customer_replied_stage_id.id
                            })
            elif vals.get('state') == 'staff_replied':
                if self.env.user.company_id.sh_staff_replied:
                    for rec in self:
                        if rec.stage_id.id != self.env.user.company_id.new_stage_id.id:
                            vals.update({
                                'stage_id':
                                self.env.user.company_id.
                                sh_staff_replied_stage_id.id
                            })

        user_groups = self.env.user.groups_id.ids
        if vals.get('stage_id'):
            stage_id = self.env['helpdesk.stage'].sudo().search(
                [('id', '=', vals.get('stage_id'))], limit=1)
            if stage_id and stage_id.sh_group_ids:
                is_group_exist = False
                list_user_groups = user_groups
                list_stage_groups = stage_id.sh_group_ids.ids
                for item in list_stage_groups:
                    if item in list_user_groups:
                        is_group_exist = True
                        break
                if not is_group_exist:
                    raise UserError(
                        _('You have not access to edit this support request.'))
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('stage_id'):
            # for update record=====================
            last_create_id=self.helpdesk_stage_history_line.ids
            if last_create_id:
                previous_id=self.env['sh.helpdesk.ticket.stage.info'].browse(last_create_id[-1])
                sub_time = datetime.now()- previous_id.date_in

                # for days difference
                day_diff=sub_time.days

                # for hours difference
                test = str(sub_time.seconds//3600) +':'+ str(((sub_time.seconds//60)%60))
                vals = test.split(':')
                t, hours = divmod(float(vals[0]), 24)
                t, minutes = divmod(float(vals[1]), 60)
                minutes = minutes / 60.0
                time_to_fl =  hours + minutes

                # for total time count
                if day_diff>0:
                    test = str(sub_time.seconds//3600) +':'+ str(((sub_time.seconds//60)%60))
                    vals = test.split(':')
                    t, hours = divmod(float(vals[0]), 24)
                    t, minutes = divmod(float(vals[1]), 60)
                    minutes = minutes / 60.0
                    hours+=day_diff*24
                    total_time_to_fl =  hours + minutes
                else:
                    total_time_to_fl=time_to_fl

                stage_history={
                        'date_out':  datetime.now(),
                        'date_out_by': self.env.user,
                        'day_diff':day_diff,
                        'time_diff':time_to_fl,
                        'total_time_diff':total_time_to_fl,
                    }

                self.helpdesk_stage_history_line = [(1,last_create_id[-1],stage_history)]
                
          # for new record====================
            stage_history={
                        'stage_task_id': self.id,
                        'stage_name': self.stage_id.name,
                        'date_in': datetime.now(),
                        'date_in_by': self.env.user.id,
                    }
            self.helpdesk_stage_history_line = [(0,0,stage_history)]
        return res

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        defaults = {
            'partner_email': msg_dict.get('from'),
            'partner_id': msg_dict.get('author_id', False),
            'description': msg_dict.get('body'),
            'name': msg_dict.get('subject') or _("No Subject"),
            'state': 'customer_replied',
            'replied_date': msg_dict.get('date')
        }
        if custom_values is None:
            custom_values = {}
        if custom_values.get('team_id'):
            team_id = self.env['helpdesk.team'].sudo().browse(
                custom_values.get('team_id'))
            if team_id:
                defaults.update({
                    'team_id': team_id.id,
                })
        if 'to' in msg_dict and msg_dict.get('to') != '':
            to = {tools.email_normalize(email): tools.formataddr((name, tools.email_normalize(email)))
                  for (name, email) in tools.email_split_tuples(msg_dict.get('to'))}
            for k, v in to.items():
                user_id = self.env['res.users'].sudo().search(
                    [('partner_id.email', '=', k)], limit=1)
        defaults.update(custom_values)
        return super(HelpdeskTicket, self).message_new(msg_dict, custom_values=defaults)

    def _message_post_after_hook(self, message, msg_vals):
        if self.partner_email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(
                lambda partner: partner.email == self.partner_email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                ]).write({'partner_id': new_partner.id})

        return super(HelpdeskTicket,
                     self)._message_post_after_hook(message, msg_vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(HelpdeskTicket, self).copy(default=default)
        res.state = 'customer_replied'
        return res

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/helpdesk/ticket/%s' % (ticket.id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if kwargs.get('subtype') != 'mail.mt_note':
            if self and kwargs and 'author_id' in kwargs and kwargs.get('author_id'):
                author_id = self.env['res.partner'].sudo().search(
                    [('id', '=', kwargs.get('author_id'))], limit=1)
                if author_id:
                    user_id = self.env['res.users'].sudo().search(
                        [('partner_id', '=', author_id.id)], limit=1)
                    if user_id:
                        if 'subtype_id' not in kwargs:
                            if self.team_id:
                                if self.team_id.alias_name and self.team_id.alias_domain:
                                    email = str(self.team_id.alias_name) + \
                                        '@' + str(self.team_id.alias_domain)
                                    mail_server_id = self.env['ir.mail_server'].sudo().search(
                                        [('smtp_user', '=', email)], limit=1)
                                    if mail_server_id:
                                        kwargs.update({
                                            'email_from': email,
                                            'mail_server_id': mail_server_id.id
                                        })
                                    self.replied_date = fields.Datetime.now()
                    else:
                        partner_ids = []
                        if 'to' in kwargs:
                            email_to = kwargs.get('to').split(",")
                            if len(email_to) > 1:
                                del email_to[0]
                                for email in email_to:
                                    email_address = email.strip()
                                    partner_id = self.env['res.partner'].search([
                                        ('email', '=', email_address)
                                    ], limit=1)
                                    if partner_id:
                                        partner_ids.append(partner_id.id)
                                    else:
                                        partner_id = self.env['res.partner'].sudo().create({
                                            'name': email_address,
                                            'email': email_address,
                                        })
                                        partner_ids.append(partner_id.id)
                        if partner_ids:
                            self.message_subscribe(partner_ids=partner_ids)
                        self.state = 'customer_replied'
                        if 'date' not in kwargs:
                            self.replied_date = fields.Datetime.now()
                        else:
                            self.replied_date = kwargs.get('date')

                if self.team_id:
                    if self.team_id.alias_name and self.team_id.alias_domain:
                        email = str(self.team_id.alias_name)+'@' + \
                            str(self.team_id.alias_domain)
                        mail_server_id = self.env['ir.mail_server'].sudo().search(
                            [('smtp_user', '=', email)], limit=1)
                        if mail_server_id:
                            kwargs.update({
                                'email_from': email,
                                'mail_server_id': mail_server_id.id
                            })

                        # if self.stage_id.sequence == 0:
                        #     pass
                        # else:
                        #     self.state = 'staff_replied'
                        self.replied_date = fields.Datetime.now()
        return super(HelpdeskTicket, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def _compute_rating(self):
        if self:
            for rec in self:
                rec.priority_new='none'
                rec.customer_comment=''
                find_rating=self.env['rating.rating'].search([('res_id','=',rec.id),('res_model','=','helpdesk.ticket')],limit=1)
                if find_rating:
                    rec.priority_new=find_rating.rating_text
                    rec.customer_comment=find_rating.feedback
                    
    def _action_open_new_timesheet(self, time_spent):
        res=super(HelpdeskTicket, self)._action_open_new_timesheet(time_spent)
        if self.company_id.sh_default_description:
            res['context']['default_description']=str(self.env.user.name)+'-'+str(self.name)
        return res

    def _compute_task_count(self):
        ''' Display Connected task with helpdesk_ticket   '''
        if self:
            for rec in self:
                rec.task_count = 0
                task_ids = self.env['project.task'].sudo().search(
                    [('sh_ticket_ids', 'in', [rec.id])])
                if task_ids:
                    rec.task_count = len(task_ids.ids)

    def create_task(self):
        ''' Create task from ticket   '''
        return{
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_user_id': self.user_id.id,
                'default_sh_ticket_ids': [(4, self.id)],
                'default_partner_id': self.partner_id.id,
                'default_date_deadline': fields.Date.today(),
                'default_description': self.description
            }
        }

    def view_task(self):
        task_ids = self.env['project.task'].sudo().search(
            [('sh_ticket_ids', 'in', [self.id])])
        return{
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', task_ids.ids)],
            'target': 'current',
        }

    def action_create_lead(self):
        context = {'default_type': 'lead'}
        if self.partner_id:
            context.update({
                'default_partner_id': self.partner_id.id,
            })
        if self.user_id:
            context.update({
                'default_user_id': self.user_id.id,
            })
        if self:
            context.update({
                'default_sh_ticket_ids': [(6, 0, self.ids)],
            })
        return{
            'name': 'Lead',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'context': context,
            'target': 'self'
        }

    def action_create_opportunity(self):
        context = {'default_type': 'opportunity'}
        if self.partner_id:
            context.update({
                'default_partner_id': self.partner_id.id,
            })
        if self.user_id:
            context.update({
                'default_user_id': self.user_id.id,
            })
        if self:
            context.update({
                'default_sh_ticket_ids': [(6, 0, self.ids)],
            })
        return{
            'name': 'Opportunity',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'context': context,
            'target': 'self'
        }

    def _compute_lead_count_helpdesk(self):
        for record in self:
            record.lead_count = 0
            leads = self.env['crm.lead'].search(
                [('id', 'in', record.sh_lead_ids.ids), '|', ('type', '=', 'lead'), ('type', '=', False)], limit=None)
            if leads:
                record.lead_count = len(leads.ids)

    def _compute_opportunity_count_helpdesk(self):
        for record in self:
            record.opportunity_count = 0
            opporunities = self.env['crm.lead'].search(
                [('id', 'in', record.sh_lead_ids.ids), ('type', '=', 'opportunity')], limit=None)
            if opporunities:
                record.opportunity_count = len(opporunities.ids)

    def lead_counts(self):
        self.ensure_one()
        leads = self.env['crm.lead'].sudo().search(
            [('id', 'in', self.sh_lead_ids.ids), '|', ('type', '=', 'lead'), ('type', '=', False)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "crm.crm_lead_all_leads")
        if len(leads) > 1:
            action['domain'] = [('id', 'in', leads.ids), '|',
                                ('type', '=', 'lead'), ('type', '=', False)]
        elif len(leads) == 1:
            form_view = [(self.env.ref('crm.crm_lead_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = leads.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def opportunity_counts(self):
        self.ensure_one()
        opportunities = self.env['crm.lead'].sudo().search(
            [('id', 'in', self.sh_lead_ids.ids), ('type', '=', 'opportunity')])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "crm.crm_lead_action_pipeline")
        if len(opportunities) > 1:
            action['domain'] = [('id', 'in', opportunities.ids),
                                ('type', '=', 'opportunity')]
        elif len(opportunities) == 1:
            form_view = [(self.env.ref('crm.crm_lead_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = opportunities.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_create_purchase_order(self):
        context = {'date_planned':datetime.now()}
        if self.partner_id:
            context.update({
                'default_partner_id': self.partner_id.id,
            })
        if self.user_id:
            context.update({
                'default_user_id': self.user_id.id,
            })
        if self:
            context.update({
                'default_sh_purchase_ticket_ids': [(6, 0, self.ids)],
            })
        if self.product_ids:
            line_list = []
            for product in self.product_ids:
                line_vals = {
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': 1.0,
                    'price_unit': product.standard_price,
                    'product_uom': product.uom_id.id,
                    'date_planned':datetime.now()
                }
                if product.taxes_id:
                    line_vals.update({
                        'taxes_id': [(6, 0, product.supplier_taxes_id.ids)]
                    })
                line_list.append((0, 0, line_vals))
            context.update({
                'default_order_line': line_list
            })
        return{
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'context': context,
            'target': 'self'
        }

    def _compute_purchase_order_count_helpdesk(self):
        for record in self:
            record.purchase_order_count = 0
            tickets = self.env['purchase.order'].search(
                [('id', 'in', record.sh_purchase_order_ids.ids)], limit=None)
            record.purchase_order_count = len(tickets.ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        orders = self.env['purchase.order'].sudo().search(
            [('id', 'in', self.sh_purchase_order_ids.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase.purchase_form_action")
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_sale_create_order(self):
        context = {}
        if self.partner_id:
            context.update({
                'default_partner_id': self.partner_id.id,
            })
        if self.user_id:
            context.update({
                'default_user_id': self.user_id.id,
            })
        if self:
            context.update({
                'default_sh_sale_ticket_ids': [(6, 0, self.ids)],
            })
        order_id = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'sh_sale_ticket_ids': self.ids
        })
        if self.product_ids:
            if order_id:
                line_list = []
                for product in self.product_ids:
                    line_vals = {
                        'product_template_id': product.product_tmpl_id.id,
                        'display_type': False,
                        'product_id': product.id,
                        'name': product.display_name,
                        'product_uom_qty': 1.0,
                        'price_unit': product.list_price,
                        'product_uom': product.uom_id.id,
                    }
                    if product.taxes_id:
                        line_vals.update(
                            {'tax_id': [(6, 0, product.taxes_id.ids)]})
                    line_list.append((0, 0, line_vals))
                order_id.order_line = line_list
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': order_id.id,
            'target': 'self'
        }

    def _compute_sale_order_count_helpdesk(self):
        for record in self:
            record.sale_order_count = 0
            tickets = self.env['sale.order'].search(
                [('id', 'in', record.sh_sale_order_ids.ids)], limit=None)
            record.sale_order_count = len(tickets.ids)

    def action_view_sale_orders(self):
        self.ensure_one()
        orders = self.env['sale.order'].sudo().search(
            [('id', 'in', self.sh_sale_order_ids.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_orders")
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_create_invoice(self):
        invoice_vals = {
            'move_type': 'out_invoice',
        }
        if self.partner_id:
            invoice_vals.update({
                'partner_id': self.partner_id.id,
            })
        if self.user_id:
            invoice_vals.update({
                'user_id': self.user_id.id,
            })
        inv_id = self.env['account.move'].sudo().create(invoice_vals)
        if self.product_ids:
            line_list = []
            for product in self.product_ids:
                journal_id = self.env["account.journal"].search(
                    [("type", "=", "sale"), ('name', '=', 'Customer Invoices'),
                     ('company_id', '=', self.env.company.id)],
                    limit=None)
                account_id = False
                if journal_id.default_account_id:
                    account_id = journal_id.default_account_id
                if account_id:
                    line_vals = {
                        'product_id': product.id,
                        'name': product.display_name,
                        'quantity': 1.0,
                        'price_unit': product.list_price,
                        'product_uom_id': product.uom_id.id,
                        'account_id': account_id.id,
                        'currency_id':self.env.company.currency_id.id
                    }
                    if product.taxes_id:
                        line_vals.update(
                            {'tax_ids': [(6, 0, product.taxes_id.ids)]})
                    line_list.append((0, 0, line_vals))
            inv_id.invoice_line_ids = line_list
        self.env.cr.execute(""" INSERT INTO sh_account_move_helpdesk_ticket_rel (helpdesk_ticket_id, account_move_id) VALUES (%s, %s);""" , [self.id,inv_id.id])
        self.env.cr.commit() 
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': inv_id.id,
            'target': 'self'
        }

    def sh_compute_invoice_count_helpdesk(self):
        for record in self:
            record.sh_invoice_count = 0
            tickets = self.env['account.move'].search(
                [('id', 'in', record.sh_invoice_ids.ids)], limit=None)
            record.sh_invoice_count = len(tickets.ids)

    def invoice_counts(self):
        self.ensure_one()
        orders = self.env['account.move'].sudo().search(
            [('id', 'in', self.sh_invoice_ids.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_helpdesk_ticket_merge(self):
        get_tickets = self.env['helpdesk.ticket'].browse(self.env.context.get('active_ids'))
        no_partner=False
        for ticket in get_tickets:
            if not ticket.partner_id:
                no_partner=True  
        
        if len(get_tickets.ids) < 2:
            raise ValidationError(_('You should select minium two ticket for merge !!'))
        if no_partner:
            raise ValidationError(_('Partner Must be select to merge ticket !!'))  
        result = all(rec == get_tickets.mapped('partner_id').ids[0] for rec in get_tickets.mapped('partner_id').ids)
        if not result:
            raise ValidationError(_('Partner Must be same !!'))

        return {
            'name':'Merge Ticket',
            'res_model':'helpdesk.ticket.merge.ticket.wizard',
            'view_mode':'form',
            'context': {
              'default_sh_helpdesk_ticket_ids' : [(6, 0, self.env.context.get('active_ids'))],
              'default_sh_partner_id' : get_tickets.mapped('partner_id').ids[0],
            },
            'view_id':self.env.ref('sh_helpdesk_enterprise.sh_helpdesk_enterprise_ticket_merge_ticket_wizard_form_view').id,
            'target':'new',
            'type':'ir.actions.act_window'
        }
        
    def _compute_count_merge_ticket(self):
        for record in self:
            record.sh_merge_ticket_count = len(record.sh_merge_ticket_ids) if record.sh_merge_ticket_ids else 0
    
    def get_merge_tickets(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Merged Tickets",
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "domain": [("id", "in", self.sh_merge_ticket_ids.ids)],
        }