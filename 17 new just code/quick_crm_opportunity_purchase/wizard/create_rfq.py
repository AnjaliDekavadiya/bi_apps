 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _

class AddProductLinesWizard(models.TransientModel):
    _name = "create.request.rfq.line.custom.wizard"

    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        domain=[('sale_ok', '=', True)], 
        change_default=True, 
        ondelete='restrict', 
        required=True
    )
    partner_ids = fields.Many2many(
        'res.partner', 
        string='Vendors', 
        required=True
    )
    product_uom_qty = fields.Float(
        string='Request Quantity', 
        digits='Product Unit of Measure', 
        required=True, 
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure', 
        required=True
    )
    custom_rfq_id = fields.Many2one(
        'create.request.rfq.custom.wizard', 
        string='Rfq'
    )

    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.id


class AddProductLinesWizardForm(models.TransientModel):
    _name = "create.request.rfq.custom.wizard"

    custom_request_rfq_line = fields.One2many(
        'create.request.rfq.line.custom.wizard', 
        'custom_rfq_id', 
        'Rfq Request'
    )

    def create_lines(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        crm_id = self.env['crm.lead'].browse(active_id)
        request_rfq_obj = self.env['request.rfq']
        for rec in self:
            for line in rec.custom_request_rfq_line:
                for partner in line.partner_ids:
                    rfq_line_Vals = {
                        'product_id':line.product_id.id,
                        'product_uom_qty':line.product_uom_qty,
                        'partner_id': partner.id,
                        'product_uom':line.product_uom.id,
                        'lead_id': crm_id.id
                    }
                    rfq_line_Vals_new = request_rfq_obj.new(rfq_line_Vals)
                    rfq_line_Vals_new.product_id_change()
                    rfq_line_Vals = rfq_line_Vals_new._convert_to_write({
                        name: rfq_line_Vals_new[name] for name in rfq_line_Vals_new._cache})
                    line = request_rfq_obj.create(rfq_line_Vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: