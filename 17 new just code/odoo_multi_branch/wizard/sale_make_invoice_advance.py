# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    #Pass value of client to pay in create invoice.
#    @api.multi odoo13
    def _create_invoice(self, order, so_line, amount):
        print(":::::::::::::::llllllllllllllllll")
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        res.write({'company_branch_id': order.company_branch_id.id})
        for line in res.invoice_line_ids:
            line.write({'company_branch_id': order.company_branch_id.id})
            print(":::::::::::::", line.company_branch_id)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
