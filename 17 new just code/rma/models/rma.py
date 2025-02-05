# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

wk_state = [
    ('new', 'New'),
    ('verification', 'Verification'),
    ('negotiation', 'Negotiation'),
    ('resolved', 'Resolved'),
    ('agreement', 'Agreement'),
    ('close', 'Closed')
]


class RmaStages(models.Model):
    _name = "rma.stages"
    _order = 'sequence'
    _description = "RMA Stages"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', required=True)
    description = fields.Text('Description')
    related_status = fields.Selection(
        wk_state, 'Related Status', required=True, default='new')


class RmaRma(models.Model):
    _name = 'rma.rma'
    _inherit = ['mail.thread']
    _description = "RMA"
    _order = 'create_date desc'
    _mail_post_access = 'read'


    def invoice_create(self):
        if self.picking_id.state !="done":
            raise UserError("Please validate the incoming delivery first.")
        order_id = self.order_id
        invoice = order_id._create_invoices(final=True)
        self.refund_invoice_id = invoice.id
        return invoice
    @api.model
    def _get_default_name(self):
        sequence_val = self.env['ir.sequence'].next_by_code('rma.rma') or '/'
        return sequence_val

    @api.model
    def _get_default_stage(self):
        stage_id = 0
        rma_stage_obj = self.env['rma.stages']
        rma_stages = rma_stage_obj.search([('related_status', '=', 'new')])
        if rma_stages:
            stage_id = rma_stages[0].id
        return stage_id

    @api.model
    def _get_term_condition(self):
        res = self.env['res.config.settings'].get_values()
        rma_term_condition = ""
        if res.get("rma_term_condition", False):
            rma_term_condition = res.get("rma_term_condition", False)
        return rma_term_condition

    def _set_product_received(self):
        """ """
        for obj in self:
            if obj.picking_id:
                obj.product_received = True
            else:
                obj.product_received = False

    def _set_po_created(self):
        """ """
        for obj in self:
            if obj.purchase_order_id:
                obj.po_created = True
            else:
                obj.po_created = False

    def _set_do_created(self):
        """ """
        for obj in self:
            if obj.new_do_picking_id:
                obj.do_created = True
            else:
                obj.do_created = False

    def _set_inv_created(self):
        """ """
        for obj in self:
            if obj.refund_invoice_id:
                obj.inv_created = True
            else:
                obj.inv_created = False

    def _get_attachment_count(self):
        for record in self:
            x = self.env['ir.attachment'].search([('res_model', '=', 'rma.rma'), ('res_id', '=', record.id)])
            count = 0
            for attach_obj in x:
                if attach_obj.name[attach_obj.name.rfind('.'):] not in ['.pdf', '.doc', '.docx', '.odt']:
                    count += 1
            record.attachment_count = count

    @api.depends('orderline_id.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the RMA.
        """
        for rma_obj in self:
            amount_untaxed = amount_tax = 0.0
            for line in rma_obj.orderline_id:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if not rma_obj.order_id.pricelist_id:
                rma_obj.order_id.pricelist_id = self.env['product.pricelist'].sudo().browse([1])


            if rma_obj.orderline_id and rma_obj.orderline_id.product_uom_qty:
                rma_obj.update({
                    'amount_untaxed': rma_obj.order_id.pricelist_id.currency_id.round((amount_untaxed / rma_obj.orderline_id.product_uom_qty) * rma_obj.refund_qty),
                    'amount_tax': rma_obj.order_id.pricelist_id.currency_id.round((amount_tax / rma_obj.orderline_id.product_uom_qty) * rma_obj.refund_qty),
                    'amount_total': ((amount_untaxed / rma_obj.orderline_id.product_uom_qty) * rma_obj.refund_qty) + ((amount_tax / rma_obj.orderline_id.product_uom_qty) * rma_obj.refund_qty),
                })

            else:
                if rma_obj.order_id:
                    rma_obj.update({
                        'amount_untaxed': rma_obj.order_id.pricelist_id.currency_id.round(amount_untaxed),
                        'amount_tax': rma_obj.order_id.pricelist_id.currency_id.round(amount_tax),
                        'amount_total': amount_untaxed + amount_tax,
                    })

    @api.model
    def get_request_type(self):
        irmodule_obj = self.env['ir.module.module']
        ir_default = self.env['ir.default'].sudo()
        is_repair_enable = ir_default._get('res.config.settings', 'is_repair_enable')
        vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
            'to install', 'installed', 'to upgrade'])])
        request_type = [('refund', 'Refund'), ('exchange', 'Exchange')]
        if vals and is_repair_enable:
            request_type.append(("repair", "Repair"))
        return request_type

    def _set_mrp_install(self):
        """ """
        ir_default = self.env['ir.default'].sudo()
        is_repair_enable = ir_default._get('res.config.settings', 'is_repair_enable')
        for obj in self:
            irmodule_obj = self.env['ir.module.module']
            vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
                'to install', 'installed', 'to upgrade'])])
            if vals and is_repair_enable:
                obj.is_repair_install = True
            else:
                obj.is_repair_install = False

    @api.model
    def _mrp_repair_obj(self):
        ir_default = self.env['ir.default'].sudo()
        is_repair_enable = ir_default._get('res.config.settings', 'is_repair_enable')
        irmodule_obj = self.env['ir.module.module']
        vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
            'to install', 'installed', 'to upgrade'])])
        if vals and is_repair_enable:
            return [('repair.order', 'Repair')]
        else:
            []

    name = fields.Char('RMA No', readonly=True, default='New RMA')
    order_id = fields.Many2one('sale.order', 'Order', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer')
    stage_id = fields.Many2one(
        'rma.stages', 'Stage', default=_get_default_stage)
    product_id = fields.Many2one(
        'product.product', related='orderline_id.product_id', string='Product', required=True, index=True, tracking=True, store=True)
    refund_qty = fields.Float(
        'Return Quantity', required=True, tracking=True)
    orderline_id = fields.Many2one('sale.order.line', 'Order Line')
    problem = fields.Text('Problem')
    resolve_date = fields.Datetime('Resolve Date')
    state = fields.Selection(related="stage_id.related_status",
                             string='Status', readonly=True, store=True)
    attachment_count = fields.Integer(
        compute='_get_attachment_count', string="Number of Attachments")


    return_request_type = fields.Selection(
        'get_request_type', string="Return Request Type", default="refund")
    reason_id = fields.Many2one("rma.reasons", string="Reason")
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order")
    picking_id = fields.Many2one("stock.picking", "Return Pickings")
    refund_invoice_id = fields.Many2one(
        "account.move", string="Refund Invoice")
    new_do_picking_id = fields.Many2one("stock.picking", "New Delivery Order")

    product_received = fields.Boolean(
        compute='_set_product_received', string="Product Received", help="Returned product is received or not.")
    po_created = fields.Boolean(compute='_set_po_created', string="Purchase Order Created",
                                help="For this RMA, purchase order is created or not.")
    do_created = fields.Boolean(compute='_set_do_created', string="Delivery Order Created",
                                help="For this RMA, delivery order is created or not.")
    inv_created = fields.Boolean(compute='_set_inv_created', string="Invoice Issued",
                                 help="For this RMA, Refund invoice is created or not.")

    rma_term_condition = fields.Html(
        string="Term And Conditions", default=_get_term_condition)
    i_agree = fields.Boolean(string="I Agree")
    website_message_ids = fields.One2many('mail.message', 'res_id', domain=lambda self: [
                                          '&', ('model', '=', self._name), ('message_type', '=', 'comment')], string='Website RMA Comments')

    currency_id = fields.Many2one(
        "res.currency", related='order_id.currency_id', string="Currency", readonly=True, required=True)
    amount_untaxed = fields.Monetary(
        string='Untaxed Amount', readonly=True, compute='_amount_all', tracking=True, store=True)
    amount_tax = fields.Monetary(
        string='Taxes', readonly=True, compute='_amount_all', tracking=True, store=True)
    amount_total = fields.Monetary(
        string='Total Refund', readonly=True, compute='_amount_all', tracking=True, store=True)
    mrp_repair_id = fields.Char(string="Repair Reference")
    is_repair_install = fields.Boolean(
        compute='_set_mrp_install', string="MRP Repair Installed")

    load_lot_ids = fields.Many2many(
        string='load number',
        comodel_name='stock.lot',
        compute='_compute_load_lot_ids',
    )

    lot_serial_ids = fields.Many2many(
        string='Lot/Serial Number',
        comodel_name='stock.lot',
        domain="[('id', 'in', load_lot_ids)]",
    )
    
    tracking_type = fields.Selection(
        string='Tracking Type',
        related="orderline_id.product_id.tracking",
        store=True,
    )

    @api.depends('orderline_id')
    def _compute_load_lot_ids(self):
        for record in self:
            all_sr_no = []
            for move_id in record.orderline_id.move_ids:
                if move_id.state == 'done':
                    all_sr_no.extend(move_id.lot_ids.ids)
                    
            exist_sr_no = []
            for rma_id in record.orderline_id.rma_ids:
                exist_sr_no.extend(rma_id.lot_serial_ids.ids)

            domain = list(set(all_sr_no).difference(set(exist_sr_no)))
            domain.extend(record.lot_serial_ids.ids)
            record.load_lot_ids = self.env['stock.lot'].sudo().browse(domain)

    @api.onchange('orderline_id')
    def _onchange_orderline_id(self):
        all_sr_no = []
        domain = []
        for move_id in self.orderline_id.move_ids:
            if move_id.state == 'done':
                all_sr_no.extend(move_id.lot_ids.ids)
                
        exist_sr_no = []
        for rma_id in self.orderline_id.rma_ids:
            exist_sr_no.extend(rma_id.lot_serial_ids.ids)

        domain = [('id', 'in', list(set(all_sr_no).difference(set(exist_sr_no))))]       

        return {'domain': {'lot_serial_ids': domain}}                

    def view_repair_job(self):
        self.ensure_one()
        view_id = self.env.ref('repair.view_repair_order_form').id
        context = self._context.copy()
        mrp_repair_id = self.env["repair.order"].browse(int(self.mrp_repair_id))
        if not mrp_repair_id:
            raise UserError(
                ('Associated Repair Management record has been deleted.'))
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'repair.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': mrp_repair_id.id if mrp_repair_id else False,
        }

    def create_repaired_delivery(self):
        if not self.mrp_repair_id:
            raise UserError(('Create a repair job then you can proceed.'))
        repair_obj = self.env["repair.order"].browse(int(self.mrp_repair_id))
        if repair_obj.state == 'done':
            delivery_action = self.env.ref('rma.action_rma_new_delivery_order_wizard_id')
            action = delivery_action.read()[0]
            return action
        else:
            raise UserError(('Repair job still under process. Please complete the repair job then you can deliver the product to customer.'))

    def attachment_tree_view_action(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {
            'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(
            ['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        return action

    @api.onchange('product_id', 'order_id', 'partner_id')
    def quantity_onchange(self):
        if self.product_id:
            rma_refund_qty = 0
            sale_order_line_obj = self.env['sale.order.line'].search([('order_id', '=', self.order_id.id), (
                'order_partner_id', '=', self.partner_id.id), ('product_id', '=', self.product_id.id)])
            line_qty = sale_order_line_obj.qty_delivered
            rma_search_ids = self.search([('partner_id', '=', sale_order_line_obj.order_partner_id.id), (
                'product_id', '=', sale_order_line_obj.product_id.id), ('order_id', '=', sale_order_line_obj.order_id.id)])
            for rma_id in rma_search_ids:
                rma_refund_qty = rma_refund_qty + \
                    self.browse(rma_id.id).refund_qty
            for prod_id in self.order_id.order_line:
                if self.product_id == prod_id.product_id:
                    self.refund_qty = line_qty - rma_refund_qty

    @api.onchange('order_id')
    def customer_name_onchange(self):
        if self.order_id:
            self.orderline_id = False
            result = {}
            prod_ds = []
            ids = [self.order_id.partner_id.id]
            self.partner_id = self.order_id.partner_id.id
            orderline_ids = self.order_id.order_line.ids
            result['domain'] = {'partner_id': [('id', 'in', ids)], 'orderline_id': [
                ('id', 'in', orderline_ids)]}
            return result
        
    def check_return_qty(self, order_line, refund_qty):
        rma_refund_qty = 0
        if refund_qty <= 0:
            raise UserError(_('You can not create RMA with return quantity 0 .'))  
            
        if not order_line:
            order_line = self.orderline_id

        line_qty = order_line.qty_delivered
        rma_search_ids = self.search([('partner_id', '=', order_line.order_partner_id.id), (
            'product_id', '=', order_line.product_id.id), ('order_id', '=', order_line.order_id.id)])

        for rma_id in rma_search_ids:
            rma_refund_qty += self.browse(rma_id.id).refund_qty  
        
        net_refund_qty = refund_qty + rma_refund_qty
        if net_refund_qty > line_qty:
            raise UserError(('You cannot generate an RMA with quantity greater than %s ') % (
                line_qty - rma_refund_qty))


    def write(self, vals):
        if self:
            if vals.get('stage_id', False):
                previous_stage = self.stage_id.name
                next_stage = self.env['rma.stages'].browse(vals.get('stage_id', False)).name
                for rma_id in self._ids:
                    self.message_post(body=_('<b>• Stage</b>: %s → %s') % (
                        previous_stage, next_stage), subject="Stage Changed", subtype_xmlid='mail.mt_comment')
                    realted_status = self.env['rma.stages'].browse(vals.get('stage_id', False)).related_status
                    if realted_status == 'resolved':
                        vals['resolve_date'] = fields.Datetime.now()

            if vals.get('refund_qty') != None:
                sale_order_line_obj = self.env["sale.order.line"].browse(vals["orderline_id"]) if vals.get("orderline_id", False) else False
                self.check_return_qty(sale_order_line_obj, vals.get('refund_qty'))

            if self.orderline_id.product_id.tracking == 'serial':
                if vals.get('refund_qty') and vals.get('lot_serial_ids'):
                    lot_ids = vals.get('lot_serial_ids')[0][2]
                    if vals.get("refund_qty") != len(lot_ids):
                        raise UserError(('Selected Quantities and the selected lot/serial number must be equal!!'))
                elif vals.get('refund_qty'):
                    if vals.get("refund_qty") != len(self.lot_serial_ids.ids):
                        raise UserError(('Selected Quantities and the selected lot/serial number must be equal!!'))
                elif vals.get('lot_serial_ids'):
                    lot_ids = vals.get('lot_serial_ids')[0][2]
                    if self.refund_qty != len(lot_ids):
                        raise UserError(('Selected Quantities and the selected lot/serial number must be equal!!'))    
                                           
        return super(RmaRma, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New RMA') == 'New RMA':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'rma.rma') or 'New RMA'
        if vals.get("refund_qty", 0.0) <= 0:
            raise UserError(_('You can not create RMA with return quantity 0 .'))

        sale_order_line_obj = self.env["sale.order.line"].browse(vals["orderline_id"]) if vals.get("orderline_id", False) else False
        if not sale_order_line_obj:
            sale_order_line_obj = self.env['sale.order.line'].search([('order_id', '=', vals.get('order_id', False)), ('order_partner_id', '=', vals.get('partner_id', False)), ('product_id', '=', vals.get('product_id', False))], limit=1)
        line_qty = sale_order_line_obj.qty_delivered
        vals.update({"product_id": sale_order_line_obj.product_id.id})

        rma_refund_qty = 0
        net_refund_qty = 0
        rma_search_ids = self.search([('partner_id', '=', sale_order_line_obj.order_partner_id.id), (
            'product_id', '=', sale_order_line_obj.product_id.id), ('order_id', '=', sale_order_line_obj.order_id.id)])

        for rma_id in rma_search_ids:
            rma_refund_qty = rma_refund_qty + self.browse(rma_id.id).refund_qty
        net_refund_qty = rma_refund_qty + vals.get('refund_qty', 0.0)
        if rma_refund_qty == line_qty:
            raise UserError(
                ('RMA has already been Generated for this Order!!'))

        if net_refund_qty > line_qty:
            raise UserError(('You cannot generate an RMA with quantity greater than %s ') % (
                line_qty - rma_refund_qty))
        
        if sale_order_line_obj.product_id.tracking == 'serial':
            lot_ids = vals.get('lot_serial_ids')[0][2]
            if vals.get("refund_qty") != len(lot_ids):
                raise UserError(('Selected Quantities and the selected lot/serial number must be equal!!'))

        rma_obj = super(RmaRma, self).create(vals)

        enable_admin_template = self.env['ir.default']._get('res.config.settings','enable_notify_admin_4_rma')
        if enable_admin_template:
            admin_template = self.env['ir.default']._get('res.config.settings','notify_admin_for_rma_creation')
            if admin_template:
                template_id = self.env['mail.template'].browse(admin_template)
                if template_id:
                    template_id.send_mail(rma_obj.id, force_send=True)
            
        enable_customer_template = self.env['ir.default']._get('res.config.settings','enable_notify_customer_4_rma')
        if enable_customer_template:
            customer_template = self.env['ir.default']._get('res.config.settings','notify_customer_for_rma_creation')
            if customer_template:
                template_id = self.env['mail.template'].browse(customer_template)
                if template_id:
                    template_id.send_mail(rma_obj.id, force_send=True)

        return rma_obj

    def create_purchase_order(self):
        self.ensure_one()
        action = self.env.ref('rma.action_rma_purchase_order_wizard_id')
        form_view_id = self.env['ir.model.data']._xmlid_to_res_id(
            'rma.rma_purchase_order_wizard_id')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form']],
            # 'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
        }

    def customer_refund_inv(self):
        raise UserError("Create Customer Refund Invoice")

    def new_delivery_order(self):
        raise UserError("Create New Delivery Order")

    def return_product(self):
        raise UserError("Return Product by Customer")

    def view_purchase_order(self):
        self.ensure_one()
        view_id = self.env.ref('purchase.purchase_order_form').id
        context = self._context.copy()
        return {
            'name': 'PO Already Created',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'purchase.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.purchase_order_id.id,
        }

    def view_refund_invoice(self):
        self.ensure_one()
        view_id = self.env.ref('account.view_move_form').id
        return {
            'name': 'Refund Invoice',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'account.move',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.refund_invoice_id.id,
        }

    def view_new_delivery_order(self):
        self.ensure_one()
        view_id = self.env.ref('stock.view_picking_form').id
        context = self._context.copy()
        return {
            'name': 'New Delivery Order',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'stock.picking',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.new_do_picking_id.id,
        }

    def view_return_delivery_order(self):
        self.ensure_one()
        view_id = self.env.ref('stock.view_picking_form').id
        context = self._context.copy()
        return {
            'name': 'New Delivery Order',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'stock.picking',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.picking_id.id,
        }

    def open_refund_invoice_wizrad(self):
        self.ensure_one()
        if not self.order_id.invoice_ids:
            raise UserError(
                ('There is no invoice to refund for order "%s".') % (self.order_id.name))
        context = self._context.copy()
        if context.get("params"):
            context["params"]["model"] = "account.move"
            context["params"]["id"] = self.id
        else:
            context["model"] = "account.move"
            context["id"] = self.id
        context["active_id"] = self.order_id.invoice_ids[0].id
        context["active_ids"] = [self.order_id.invoice_ids[0].id]

        action = self.env.ref('account.action_view_account_move_reversal').read()[0]
        action['name'] = _('Credit Note')
        action['context'] = context
        return action

    def get_show_rma_stage_value(self):
        res = self.env['res.config.settings'].get_values()
        if res.get("show_rma_stage", False) and res["show_rma_stage"]:
            return True
        else:
            return False


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        
        res = super(AccountMove, self)._reverse_moves(default_values_list, cancel)
        
        if res._context.get("rma_id"):
            for rec in res:
                rma_id = rec.env["rma.rma"].browse(rec._context.get("rma_id"))
                temp_invoice_lines = []

                for invoice_line_id in rec.invoice_line_ids:
                    if rma_id.orderline_id in invoice_line_id.sale_line_ids:
                        temp_invoice_lines.append(invoice_line_id.id)
                rec.invoice_line_ids = [(6,0,temp_invoice_lines)]
                rma_id.write({"refund_invoice_id": rec.id})
        return res

class RmaReasons(models.Model):
    _name = "rma.reasons"
    _description = "Reasons For Creating RMA Record"

    name = fields.Char("Reason", required=True)
    is_enable_on_web = fields.Boolean("Display on website", default=False)
