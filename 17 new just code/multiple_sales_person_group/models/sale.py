# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )
    
#    @api.multi #odoo13
    @api.onchange('partner_id')
    # def onchange_partner_id(self):
    def _onchange_partner_id_warning(self):
        self.sale_user_group_id = self.partner_id.sale_user_group_id.id
        res = super(SaleOrder, self)._onchange_partner_id_warning()
        return res
        
#    @api.multi #odoo13
    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        #self.ensure_one()
        sale_user_group_id = self.sale_user_group_id.id
        result.update({'sale_user_group_id':sale_user_group_id})
        return result

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
#    @api.multi #odoo13
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        # sale_user_group_id = self.sale_user_group_id #odoo13
        res.update({'sale_user_group_id': order.sale_user_group_id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
