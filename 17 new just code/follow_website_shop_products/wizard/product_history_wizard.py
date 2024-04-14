# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.

from odoo import models, fields

class CustomFollowProductHistoryWizard(models.TransientModel):
    _name = 'custom.follow.product.history.wizard'
    _description = 'Custom Follow Product History Wizard'

    custom_message = fields.Text(
        string="Message",
        required=True
    )
   
    def custom_action_message_sent(self):
        product_history_id = self.env['custom.follow.product.history'].browse(self._context.get('active_ids'))
        for rec in product_history_id:
            ctx = self.env.context.copy()
            template = self.env.ref('follow_website_shop_products.custom_email_template_product_follow_history', False)
            ctx.update({
                'custom_message': self.custom_message
            })
            template.with_context(ctx).send_mail(rec.id)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
