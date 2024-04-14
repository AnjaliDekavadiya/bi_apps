'''
Created on Jan 10, 2019

@author: Zuhair Hammadi
'''
from odoo import models, api

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['approval.record', 'sale.order']
    
    @api.model
    def _before_approval_states(self):
        return [('draft', 'Draft Quotation')]
    
    @api.model
    def _after_approval_states(self):
        return [('approved', 'Quotation Approved'), 
                ('sent', 'Quotation Sent'),
                ('sale', 'Sales Order'),
                ('done', 'Locked'),
                ('cancel', 'Cancelled'), 
                ('rejected', 'Rejected')]
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'approved').with_context(tracking_disable=True).write({'state': 'sent'})
        
        return super(SaleOrder, self).message_post(**kwargs)
    