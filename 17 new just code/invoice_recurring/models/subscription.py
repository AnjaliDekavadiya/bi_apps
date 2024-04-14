# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from lxml import etree
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

def _get_document_types(self):
    return [(doc.model.model, doc.name) for doc in self.env['subscription.document'].search([], order='name')]


class SubscriptionDocument(models.Model):
    _name = "subscription.document"
    _description = "Subscription Document"

    name = fields.Char(required=True)
    active = fields.Boolean(help="If the active field is set to False, it will allow you to hide the subscription document without removing it.", default=True)
    model = fields.Many2one('ir.model', string="Object", required=True, ondelete="cascade")
    field_ids = fields.One2many('subscription.document.fields', 'document_id', string='Fields', copy=True)


class SubscriptionDocumentFields(models.Model):
    _name = "subscription.document.fields"
    _description = "Subscription Document Fields"
    _rec_name = 'field'

    field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', parent.model)]")
    value = fields.Selection([('false', 'False'), ('date', 'Current Date')], string='Default Value', help="Default value is considered for field when new document is generated.")
    document_id = fields.Many2one('subscription.document', string='Subscription Document', ondelete='cascade')


class Subscription(models.Model):
    _name = "subscription.subscription"
    _description = "Subscription"
    _order = "id desc"

    model = fields.Char(string="Model")
    name = fields.Char(required=True)
    active = fields.Boolean(help="If the active field is set to False, "
                                 "it will allow you to hide the subscription without removing it.",
                            default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    notes = fields.Text(string='Internal Notes')
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    interval_number = fields.Integer(string='Recurring Interval', required=True, default=1)
    interval_type = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], string='Recurring Unit', required=True, default='months')
    exec_init = fields.Integer(string='Recurring Number', required=True, default=1)
    date_init = fields.Datetime(string='First Date', required=True, default=fields.Datetime.now)
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('done', 'Done'), ('cancel', 'Cancelled')], string='Status', copy=False, default='draft')
    doc_source = fields.Reference(selection=_get_document_types, string='Source Document', required=True, help="User can choose the source document on which he wants to create documents")
    doc_lines = fields.One2many('subscription.subscription.history', 'subscription_id', string='Documents created', readonly=True)
    cron_id = fields.Many2one('ir.cron', string='Cron Job', help="Scheduler which runs on subscription")
    note = fields.Text(string='Notes', help="Description or Summary of Subscription")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    # Add Invoice Recurring
    invoice_id = fields.Many2one('account.move', string="Invoice", help="Invoice for recurring")
    invoice_schedule_ids = fields.One2many('schedule.schedule', 'invoice_subscription_id', copy=False)

    @api.constrains('interval_number', 'exec_init')
    def _check_configure_duration(self):
        for res in self:
            if res.interval_number <= 0 or res.exec_init <= 0:
                raise ValidationError(_('Recurring Interval or Recurring number should not be negative.'))

    @api.model
    def default_get(self, fields):
        """
            Override method for fetch default values (invoice recurring)
        """
        res = super(Subscription, self).default_get(fields)
        context = dict(self.env.context)
        if context.get('active_id') and context.get('default_model') == 'account.move':
            invoice = self.env['account.move'].browse(context['active_id'])
            if invoice.state == 'cancel' or invoice.payment_state == 'paid':
                raise UserError(_('You can not create recurring invoice which are in paid or in cancelled state!'))
            if invoice:
                res.update({
                    'doc_source': '%s,%s' % (invoice._name, str(invoice.id)),
                    'name': invoice.name,
                    'partner_id': invoice.partner_id.id,
                    'company_id': invoice.company_id.id,
                    'invoice_id': invoice.id
                })
        return res

    @api.model
    def get_views(self, views, options=None):
        """
            Override method for hide create button (invoice recurring)
        """
        res = super(Subscription, self).get_views(
                views=views, options=options)
        if 'active_model' in self.env.context and self.env.context['active_model'] == 'account.move' and 'form' in res['views']:
            root = etree.fromstring(res['views']['form']['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        return res

    def _recurring_schedule(self):
        for rec in self:
            schedules = []
            recent_date = rec.date_init
            if rec.invoice_id:
                for count in range(rec.exec_init):
                    vals = {
                        'date': recent_date,
                        'status': 'not_created',
                        'invoice_id': rec.invoice_id.id,
                        'invoice_subscription_id': rec.id,
                    }
                    schedules += rec.invoice_schedule_ids.create(vals)
                    if rec.interval_number and rec.interval_type == 'days':
                        recent_date = recent_date + relativedelta(days=rec.interval_number)
                    elif rec.interval_number and rec.interval_type == 'weeks':
                        recent_date = recent_date + relativedelta(weeks=rec.interval_number)
                    elif rec.interval_number and rec.interval_type == 'months':
                        recent_date = recent_date + relativedelta(months=rec.interval_number)

    def set_process(self):
        for subscription in self:
            # Add Invoice Recurring
            subscription._recurring_schedule()
            # End
            cron_data = {
                'name': subscription.name,
                'interval_number': subscription.interval_number,
                'interval_type': subscription.interval_type,
                'numbercall': subscription.exec_init,
                'nextcall': subscription.date_init,
                'model_id': self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1).id,
                'state': 'code',
                'code': 'model.sudo()._cron_model_copy(ids=' + str(subscription.id) + ')',
                'priority': 6,
                'user_id': subscription.user_id.id
            }
            cron = self.env['ir.cron'].sudo().create(cron_data)
            subscription.write({'cron_id': cron.id, 'state': 'running'})

    def save_action(self):
        return {
            'name': ('Make Recurring'),
            'type': 'ir.actions.act_window',
            'res_model': 'subscription.subscription',
            'res_id': self.id,
            'target': 'new',
            'view_mode': 'form',
        }

    @api.model
    def _check_recurring_invoice(self):
        subscription_ids = self.search([('state', '=', 'running')])
        for subscription in subscription_ids:
            for schedule in subscription.invoice_schedule_ids:
                reminder_date = schedule.date.date() - relativedelta(days=2)
                template_id = self.env.ref('invoice_recurring.invoice_reminder_email_template')
                if reminder_date == fields.Date.today() and template_id and subscription.doc_source:
                    template_id.sudo().with_context(reminder_date=schedule.date.date()).send_mail(
                        subscription.doc_source.id, force_send=True, raise_exception=False)

    @api.model
    def _cron_model_copy(self, ids=None):
        self.browse(ids).model_copy()

    def model_copy(self):
        for subscription in self.filtered(lambda sub: sub.cron_id):
            if not subscription.doc_source.exists():
                raise UserError(_('Please provide another source document.\nThis one does not exist!'))

            default = {'state': 'draft'}
            documents = self.env['subscription.document'].search([('model.model', '=', subscription.doc_source._name)], limit=1)
            fieldnames = dict((f.field.name, f.value == 'date' and fields.Date.today() or False)
                               for f in documents.field_ids)
            default.update(fieldnames)

            # if there was only one remaining document to generate
            # the subscription is over and we mark it as being done
            if subscription.cron_id.numbercall == 1:
                subscription.set_done()
            else:
                subscription.write({'state': 'running'})
            copied_doc = subscription.doc_source.copy(default)
            self.env['subscription.subscription.history'].create({
                'subscription_id': subscription.id,
                'date': fields.Datetime.now(),
                'document_id': '%s,%s' % (subscription.doc_source._name, copied_doc.id)})
            if subscription.doc_lines and len(subscription.doc_lines) >= subscription.exec_init:
                # subscription.set_done()
                pass
            if subscription.invoice_id:
                for doc in subscription.doc_lines:
                    for schedule in subscription.invoice_schedule_ids:
                        if schedule.date.strftime(DF) == doc.date.strftime(DF):
                            schedule.update({
                                'invoice_id': doc.document_id.id,
                                'status': 'created',
                            })

    def unlink(self):
        if any(self.filtered(lambda s: s.state == "running")):
            raise UserError(_('You cannot delete an active subscription!'))
        return super(Subscription, self).unlink()

    def set_done(self):
        # self.mapped('cron_id').sudo().write({'active': False})
        self.sudo().write({'state': 'done'})

    def set_cancel(self):
        self.write({'state': 'cancel'})

    def set_draft(self):
        self.write({'state': 'draft'})


class SubscriptionHistory(models.Model):
    _name = "subscription.subscription.history"
    _description = "Subscription history"
    _rec_name = 'date'

    date = fields.Datetime(string="Schedule Date")
    subscription_id = fields.Many2one('subscription.subscription', string='Subscription', ondelete='cascade')
    document_id = fields.Reference(selection=_get_document_types, string='Source Document', required=True)


class Schedule(models.Model):
    _name = "schedule.schedule"
    _description = "Schedule"
    _rec_name = 'status'

    date = fields.Datetime('Schedule Date')
    status = fields.Selection([('not_created', 'Scheduled'), ('created', 'Created')], string='Status', default='not_created')
    # Add Invoice Recurring
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_subscription_id = fields.Many2one('subscription.subscription', string="Subscription")
