# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class WarningMail(models.Model):
    _name = "warning.mail"
    _description = "CC Warning Mail"

    partner_id = fields.Many2one("res.partner", "Partner", help="This partner is recipient of warning mail.")
    partner_ids = fields.Many2many("res.partner", "partner_warning_mail_rel", "warning_mail_id", "partner_id",
                                   "Partner", help="These partners will also receive of warning mail.")
    mail_user = fields.Many2one("res.users", "Mail User",
                                help="Warning mail will be sent to partner from this account.")
    sale_order_id = fields.Many2one("sale.order", "Sale Order",
                                    help="Related Sale Order.")
    mail_subject = fields.Char("Subject", help="Email Subject.")
    mail_body = fields.Html("Body", help="Email Body.")
    is_send_warning_mail = fields.Boolean("Send Warning Mail")
    is_warning_mail_sent = fields.Boolean("Warning Mail Sent")
    mail_sent_datetime = fields.Datetime("Mail Sent at", help="When was this warning mail sent.")
    mail_sent_by_user = fields.Many2one("res.users", "Mail Sent by", help="By whom this warning mail was sent.")

    def get_name(self):
        """
        Creates name for records temporarily, Does not store it anywhere.
        """
        return "%s-%s" % (self.partner_id, self.mail_subject)

    @api.model
    def action_send_warning_mail(self):
        """
        This method will send warning mail for which record this method is called..
        :return: True
        """
        mail_obj = self.env["mail.mail"]
        recipients = self.partner_id
        recipients += self.partner_id.parent_id
        email_values = {
            'mail_user': self.mail_user.email_formatted,
            'email_to': self.partner_id.email_formatted,
            'subject': self.mail_subject,
            'body_html': self.mail_body,
            'auto_delete': False
        }
        if self.partner_ids:
            email_values.update({
                "recipient_ids": [(6, 0, self.partner_ids.ids)]
            })
        new_mail = mail_obj.create(email_values)
        return new_mail.send()

    def send_mail_cron(self):
        """
        This is cron method. Everytime Send Warning Mail cron runs, this method will be called.
        :return:True
        """
        emails_to_send = self.search([("is_send_warning_mail", "=", True),
                                      ("is_warning_mail_sent", "!=", True)])
        for email_to_send in emails_to_send:
            email_to_send.action_send_warning_mail()
            email_to_send.write({"is_warning_mail_sent": True})
        return True
