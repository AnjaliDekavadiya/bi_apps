# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import is_html_empty


class Invite(models.TransientModel):
    """ Wizard to invite partners (or channels) and make them followers. """
    _inherit = 'mail.wizard.invite'

    def add_followers(self):
        if not self.env.user.email:
            raise UserError(_("Unable to post message, please configure the sender's email address."))
        email_from = self.env.user.email_formatted
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_partners = wizard.partner_ids - document.sudo().message_partner_ids
            document.with_context(allow_manual_create=True).message_subscribe(partner_ids=new_partners.ids)

            model_name = self.env['ir.model']._get(wizard.res_model).display_name
            # send a notification if option checked and if a message exists (do not send void notifications)
            if wizard.notify and wizard.message and not is_html_empty(wizard.message):
                message_values = wizard._prepare_message_values(document, model_name, email_from)
                message_values['partner_ids'] = new_partners.ids
                document.message_notify(**message_values)
        return {'type': 'ir.actions.act_window_close'}