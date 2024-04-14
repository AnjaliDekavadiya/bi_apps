# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    custom_comment = fields.Text(
        string='Customer Comment',
        readonly=True,
        copy=False,
    )
    custom_service_rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Service',
        readonly=True,
        copy=False,
    )
    custom_product_rating = fields.Selection(
        [('unsatisfied', 'Unsatisfied'),
        ('very unsatisfied', 'Very Unsatisfied'),
        ('neutral', 'Neutral'),
        ('satisfied', 'Satisfied'),
        ('very satisfied', 'Very Satisfied')],
        string='Product',
        readonly=True,
        copy=False,
    )
    custom_price_rating = fields.Selection(
        [('unsatisfied', 'Unsatisfied'),
        ('very unsatisfied', 'Very Unsatisfied'),
        ('neutral', 'Neutral'),
        ('satisfied', 'Satisfied'),
        ('very satisfied', 'Very Satisfied')],
        string='Price',
        readonly=True,
        copy=False,
    )
    custom_Waitting_rating = fields.Selection(
        [('unsatisfied', 'Unsatisfied'),
        ('average', 'Average'),
        ('satisfied', 'Satisfied'),
        ('outstanding', 'Outstanding')],
        string='Ordering and Billing',
        readonly=True,
        copy=False,
    )
    custom_shopping_experiences_rating = fields.Selection(
        [('unsatisfied', 'Unsatisfied'),
        ('average', 'Average'),
        ('satisfied', 'Satisfied'),
        ('outstanding', 'Outstanding')],
        string='Shopping Experiences',
        readonly=True,
        copy=False,
    )

    def custom_send_customer_pos_feedback_mail(self):
        '''Sedn a feedback mail to customer'''
        for rec in self:
            if rec.partner_id and rec.partner_id.custom_send_feedback_mail:
                ctx = self.env.context.copy()
                template = self.env.ref('pos_customer_feedback_rating.custom_customer_pos_feedback_email_template')
                feedback_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069') + '/custom_pos_email/feedback/' + str(rec.id) + '-' + str(rec.user_id.id) + '-' + str(rec.partner_id.id)
                unsubscribe_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069') + '/custom_pos_email/unsubscribe/' + str(rec.id)
                ctx.update({
                    'feedback_url': feedback_url,
                    'unsubscribe_url': unsubscribe_url,
                    'lines': rec.lines
                })
                template.with_context(ctx).send_mail(rec.id)
        return True

    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        if vals.get('state') and vals['state'] == 'paid':
            self.custom_send_customer_pos_feedback_mail()
        return res