# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
#from openerp.exceptions import UserError odoo13
from odoo.exceptions import UserError

class ReturnOrder(models.Model):
    _inherit = 'return.order'

    return_product_line_ids = fields.One2many(
        'return.product.line',
        'return_order_id',
        string='Return Product Line',
    )
    reason_id = fields.Many2one(
        'return.reason',
        string='Return Reason',
    )
    address = fields.Text(
        string='Return Address',
    )
    return_identify = fields.Selection([
        ('single', 'Single Return'),
        ('multiple', 'Multiple Return')],
        string='Repair Type',
        default='multiple',
        readonly = True
    )
    product_id = fields.Many2one(
        'product.product',
        required=False,
    )
    quantity = fields.Float(
        required=False,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        required =False,
    )
    shipping_reference = fields.Char(
        string='Shipping Reference',
    )
    state = fields.Selection(selection_add=[
        ('rma_issue', 'RMA Issue'),
        ('material_return', 'Material Return'),
        ('return_processed', 'Return Processed')
    ])
    return_invoice_count = fields.Integer(
        compute="_return_invoice_count",
    )
    invoice_count = fields.Integer(
        compute="_invoice_count",
    )
    sale_order_count = fields.Integer(
        compute="_sale_order_count"
    )
    return_request_count = fields.Integer(
        compute="_return_request_count"
    )
    stock_scrap_count = fields.Integer(
        compute="_stock_scrap_count"
    )
    replacement_order_count = fields.Integer(
        compute="_replacement_order_count"
    )

#  Replacement Order
#    @api.multi odoo13
    @api.depends()
    def _replacement_order_count(self):
        for rec in self:
            rec.replacement_order_count = self.env['sale.order'].search_count([
                ('rma_order_id','=', rec.id)
            ])

#    @api.multi odoo13
    def show_replacement_order(self):
        for rec in self:
            res = self.env.ref('sale.action_orders')
            res = res.sudo().read()[0]
            res['domain'] = ([
                ('rma_order_id','=', rec.id)
            ])
        return res

#  Stock Scrap
#    @api.multi odoo13
    @api.depends()
    def _stock_scrap_count(self):
        for rec in self:
            rec.stock_scrap_count = self.env['stock.scrap'].search_count([
                ('rma_order_id','=', rec.id)
            ])

#    @api.multi odoo13
    def show_stock_scrap(self):
        for rec in self:
            res = self.env.ref('stock.action_stock_scrap')
            res = res.sudo().read()[0]
            res['domain'] = str([
                ('rma_order_id','=', rec.id)
            ])
        return res

#  Repair request
#    @api.multi odoo13
    @api.depends()
    def _return_request_count(self):
        for rec in self:
            rec.return_request_count = self.env['machine.repair.support'].search_count([
                ('rma_order_id','=', rec.id)
            ])

#    @api.multi odoo13
    def show_product_return_request(self):
        for rec in self:
            res = self.env.ref('website_request_return_rma_odoo.action_return_machine_repair_support')
            res = res.sudo().read()[0]
            res['domain'] = str([
                ('rma_order_id','=', rec.id)
            ])
        return res

#  Sale Order
#    @api.multi odoo13
    @api.depends()
    def _sale_order_count(self):
        for rec in self:
            rec.sale_order_count = self.env['sale.order'].search_count([
                ('id','=', rec.saleorder_id.id)
            ])

#    @api.multi odoo13
    def show_saleorder(self):
        for rec in self:
            res = self.env.ref('sale.action_orders')
            res = res.sudo().read()[0]
            res['domain'] = str([('id','=', rec.saleorder_id.id)])
        return res

#  Invoice 
#    @api.multi odoo13
    @api.depends()
    def _invoice_count(self):
        for rec in self:
#            rec.invoice_count = self.env['account.invoice'].search_count([
#                ('id','in', rec.saleorder_id.invoice_ids.ids),
#                ('type', '=', 'out_invoice')
#            ])odoo13
            rec.invoice_count = self.env['account.move'].search_count([
                ('id','in', rec.saleorder_id.invoice_ids.ids),
                ('type', '=', 'out_invoice')
            ])

#    @api.multi odoo13
    def show_invoice(self):
        for rec in self:
#            res = self.env.ref('account.action_invoice_tree1') odoo13
            res = self.env.ref('account.action_move_out_invoice_type')
            res = res.sudo().read()[0]
            res['domain'] = str([
                ('id','in', rec.saleorder_id.invoice_ids.ids),
                ('type', '=', 'out_invoice')
            ])
        return res

#  Return Invoice
#    @api.multi odoo13
    @api.depends()
    def _return_invoice_count(self):
        for rec in self:
#            rec.return_invoice_count = self.env['account.invoice'].search_count([ odoo13
            rec.return_invoice_count = self.env['account.move'].search_count([
#                ('rma_order_id', '=', rec.id),
                ('id', 'in', rec.saleorder_id.invoice_ids.ids),
                ('type', '=', 'out_refund')
            ])

#    @api.multi odoo13
    def show_return_invoice(self):
        for rec in self:
#            res = self.env.ref('account.action_invoice_out_refund') odoo13
            res = self.env.ref('account.action_move_out_refund_type')
            res = res.sudo().read()[0]
            res['domain'] = str([
#                ('rma_order_id','=', rec.id),
                ('id', 'in', rec.saleorder_id.invoice_ids.ids),
                ('type', '=', 'out_refund')
            ])
        return res

#    @api.multi odoo13
    def return_issue(self):
        for rec in self:
            rec.state = 'rma_issue'

#    @api.multi odoo13
    def material_return(self):
        for rec in self:
            rec.state = 'material_return'
 
#    @api.multi 13
    def return_processed(self):
        for rec in self:
            rec.state = 'return_processed'

#    @api.multi odoo13
    def return_confirm(self):
        for rec in self:
            if rec.return_identify == 'multiple':
                for line in rec.return_product_line_ids:
                    if not line.repair_scrape:
                        raise UserError(_('Place select repair method on RMA order line.'))
                    else:
                        super(ReturnOrder, self).return_confirm()
            else:
                super(ReturnOrder, self).return_confirm()

#    @api.multi odoo13
    def send_rma(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            # template_id = ir_model_data.get_object_reference('website_request_return_rma_odoo', 'email_template_rma_sendto_customer')[1]
            template_id = ir_model_data._xmlid_to_res_id('website_request_return_rma_odoo.email_template_rma_sendto_customer',raise_if_not_found=False)
        except ValueError:
            template_id = False
        try:
            # compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            compose_form_id = ir_model_data._xmlid_to_res_id('mail.email_compose_message_wizard_form',raise_if_not_found=False)
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'return.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            #'custom_layout': "sale.mail_template_data_notification_email_sale_order",
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

#    @api.multi odoo13
    def create_repair_request(self):
        """This method crate a repair request."""
        for rec in self:
            for line in rec.return_product_line_ids:
                if line.repair_scrape == 'repair':
#                    print("dcfvghj\n\n\n",) odoo13
                    vals = {
                        'subject': rec.number,
                        'partner_id': rec.partner_id.id,
                        'phone': rec.partner_id.phone,
                        'email': rec.partner_id.email,
                        'product_id': line.product_id.id,
                        'quantity': line.return_quantity,
                        'uom_id': line.uom_id.id,
                        'problem': rec.reason,
                        'rma_order_id': rec.id,
                        'reason_id': rec.reason_id.id,
                    }

                    request_id = self.env['machine.repair.support'].sudo().create(vals)
#                    print("dcfvghj\n\n\n",request_id) odoo13
                    
#    @api.multi odoo13
    def create_stock_scrap(self):
        """This method crate a stock scrap."""
        for rec in self:
            for line in rec.return_product_line_ids:
                if line.repair_scrape == 'scrape':
                    vals = {
                        'product_id': line.product_id.id,
                        'scrap_qty': line.return_quantity,
                        'product_uom_id': line.uom_id.id,
                        'rma_order_id': rec.id,
                    }
                    scrap_id = self.env['stock.scrap'].sudo().create(vals)
#                    print("dcfvghj\n\n\n",scrap_id) odoo13

#    @api.multi odoo13
    def create_replacement_order(self):
        """This method crate a sale order."""
        for rec in self:
            if any(line.repair_scrape  == 'ex_change' for line in rec.return_product_line_ids):
                vals = {
                    'partner_id': rec.partner_id.id,
                    'rma_order_id': rec.id,
                }
                order_id = self.env['sale.order'].sudo().create(vals)
#                print("dfgh------------------",order_id) odoo13
                for line in rec.return_product_line_ids:
                    if line.repair_scrape == 'ex_change':
                        line_vals = {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.return_quantity,
                            'product_uom': line.uom_id.id,
                            'price_unit': 0.0,
                            'order_id': order_id.id,
                        }
                        order_line = self.env['sale.order.line'].sudo().create(line_vals)
#                        print("dfgh====================",order_line) odoo13


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
