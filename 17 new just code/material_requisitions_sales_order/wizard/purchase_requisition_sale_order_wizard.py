# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RequisitionWizard(models.TransientModel):
    _name = 'requisition.so.wizard'

    customer_from = fields.Selection(
        selection=[
            ('employee', 'Employee'),
            ('customer', 'Customer')],
        string='Customer From',
        required=True,
    )
    custom_partner_id = fields.Many2one(
        'res.partner',
        string='Sale Customer',
        required=True,
    )

    so_product_price = fields.Selection(
        selection=[
            ('noprice', 'No Price'),
            ('costprice', 'Cost Price'),
            ('saleprice', 'Sale Price')],
        string='Sale Product Price',
        default='noprice',
        required=True,
    )

    @api.onchange('customer_from')
    def onchange_customer_from(self):
        '''
        This method is used to the wizard selection.
        In a wizard customer from employee the partner value automaticly set.
        '''
        if self.customer_from == 'employee':
            requisition = self.env['material.purchase.requisition'].browse(int(self.env.context.get('active_id')))
            # self.custom_partner_id = requisition.employee_id.sudo().address_home_id.id
            self.custom_partner_id = requisition.employee_id.sudo().address_id.id

    # @api.multi #odoo13
    def create_sale_order_requisition(self):
        '''
        This method is used o the create a sale order and sale order line.
        Wizard partner value is set in a sale order customer filed.
        Wizard have one selection so product price in selection there are a three option.
        'No price','Cost Price','Sale Price'.
        user can select the 'No Price' price value pass 0.0.
        user can select the 'Cost Price' Product cost price will be set in unit price.
        user can select the 'Sale Price' Product sale price will be set in unit price.
        '''
        vals_list = []
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']
        requisition_id = self.env['material.purchase.requisition'].browse(int(self.env.context.get('active_id')))
        sale_vals = {
            'partner_id': self.custom_partner_id.id,
        }
        virtual_sale_order_id = sale_order.new(sale_vals)
        # virtual_sale_order_id.onchange_partner_id()
        sale_vals = virtual_sale_order_id._convert_to_write({
            name: virtual_sale_order_id[name] for name in virtual_sale_order_id._cache})
        requisition_line_ids = requisition_id.requisition_line_ids.filtered(lambda line: line.requisition_type == 'saleorder' and line.is_sale_create_line != True)
        if not requisition_line_ids:
            raise ValidationError('Sale Order is already created for the Requisitions')
        price_unit = 0.0
        for req in requisition_line_ids:
            req_vals = {
                'product_id': req.product_id.id,
                'product_uom_qty': req.qty,
                'product_uom': req.uom.id,
                'order_id': virtual_sale_order_id.id,
                'custom_purchase_requisition_line': req.id,
            }
            if self.so_product_price == 'noprice':
                price_unit = 0.0

            if self.so_product_price == 'costprice':
                price_unit = req.product_id.standard_price

            if self.so_product_price == 'saleprice':
                price_unit = req.product_id.lst_price

            sale_order_line_vals = sale_order_line.new(req_vals)
            # sale_order_line_vals.product_id_change()
            req_vals = sale_order_line_vals._convert_to_write({
               name: sale_order_line_vals[name] for name in sale_order_line_vals._cache})

            if self.so_product_price != 'saleprice':
               req_vals['price_unit'] = price_unit
            vals_list.append((0, 0, req_vals))

        sale_vals.update({
            'order_line': vals_list,
            'custom_purchase_requisition': requisition_id.id
        })
        sale_order_id = sale_order.create(sale_vals)

        requisition_id.write({
            'custom_sale_order': sale_order_id.id,
            'state': 'stock',
            'is_sale_create': True,
        })
        
        for line in sale_order_id.order_line:
            requisition_id.requisition_line_ids.filtered(lambda rline: rline.id == line.custom_purchase_requisition_line.id).write({
                'custom_sale_order_line': line.id,
                'is_sale_create_line': True
            })

        action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0]
        action['domain'] = [('id', 'in', sale_order_id.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
