# -*- coding:utf-8 -*-


from odoo import models, fields, api

class SaleOrderCancelCustomWizard(models.TransientModel):
    _name = "sale.order.cancel.custom.wizard"
    _description = 'Cancel Order '

    sale_cancel_reason = fields.Text(
        string="Reason Details",
        copy=False,
    )
    so_cancel_reason_custom_id = fields.Many2one(
        'so.cancel.reason.custom',
        string='Reason',
        required=True,
    )
    send_email_tocustomer_custom = fields.Boolean(
        string='Send Email to Customer',
        default=True,
    )
    
    def sale_cancel_wizard_method(self):
        context = self._context.copy()
        context.update({'custom_sale_cancel_wizard':True})
        sale_active_id = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_active_id.sale_cancel_custom_reason = self.sale_cancel_reason
        sale_active_id.so_cancel_reason_custom_id = self.so_cancel_reason_custom_id.id
        sale_active_id.so_cancel_by_custom_id = self.env.user.id
        sale_active_id.so_cancel_custom_date = fields.date.today()
        sale_active_id.with_context(context).action_cancel()
        if self.send_email_tocustomer_custom != False:
            template = self.env.ref('odoo_sale_cancel_reason.email_template_so_cancel_custom_tmp', False)
            template.send_mail(sale_active_id.id)
        
            
            

    