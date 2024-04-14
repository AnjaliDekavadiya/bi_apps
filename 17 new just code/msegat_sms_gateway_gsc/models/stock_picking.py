# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.tools import html2plaintext

from odoo.addons.msegat_sms_gateway_gsc.msegat_sms_gateway_gsc_api.msegat_sms_gateway_gsc_api import MsegatSMSAPI


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        """
            @author: Grow Consultancy Services
        """
        res = super(StockPicking, self)._action_done()

        msegat_sms_accounts = self.env['msegat.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')],
                                                                                   limit=1, order="id asc")
        tobe_msegat_sms_accounts = msegat_sms_accounts.filtered(lambda x: x.is_default_sms_account)
        if not tobe_msegat_sms_accounts and self:
            self.message_post(body=_("MSEGAT default account not found Please set default account!!"))
            return res
        msegat_sms_account = False
        if tobe_msegat_sms_accounts:
            msegat_sms_account = tobe_msegat_sms_accounts[0]
        elif msegat_sms_accounts:
            msegat_sms_account = msegat_sms_accounts[0]

        if msegat_sms_account and msegat_sms_account.is_validate_do_to_send_sms and \
                msegat_sms_account.sms_do_validate_template_id:
            MsegatSMSAPIObj = MsegatSMSAPI()
            for picking in self:
                try:
                    message = picking._message_sms_with_template_msegat(
                        template=msegat_sms_account.sms_do_validate_template_id,
                        partner_ids=picking.partner_id.ids
                    )
                    message = html2plaintext(message)  # plaintext2html(html2plaintext(message))
                    datas = {
                        'message': message,
                        'mobile_number': (picking.partner_id.mobile or "").replace(" ", ""),
                        'picking_id': picking.id
                    }
                    CustomStatusCode, ErrorOrSuccessDict = MsegatSMSAPIObj.post_msegat_sms_send_to_recipients_api(
                        msegat_sms_account, datas)
                    msegat_sms_account.create_sent_sms_log(False, datas, CustomStatusCode, ErrorOrSuccessDict)
                except Exception as e:
                    picking.message_post(body=e)
        return res
