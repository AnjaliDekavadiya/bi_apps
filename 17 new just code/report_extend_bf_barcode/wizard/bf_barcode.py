# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class BFBarcode(models.TransientModel):
    _name = 'bf.barcode'
    _description = 'BF Barcode'

    @api.model
    def default_get(self, fields):
        result = super(BFBarcode, self).default_get(fields)
        active_ids = self._context.get('active_ids', [])
        if 'template_id' in result:
            lines = []
            template = self.env['bf.barcode.template'].sudo().browse(result.get('template_id'))
            result['report_template_id'] = template.report_template_id.id
            if template.one2many:
                if template.sub_model_object_field.name == 'id':
                    model = template.sub_model_object_field.model_id.model
                else:
                    model = template.sub_model_object_field.relation
                result['model'] = model
                for record in self.env[template.model].sudo().browse(active_ids):
                    ids = record[template.model_object_field.name].ids
                    domain = [["id", "in", ids]]
                    if template.filter_id:
                        domain = [["id", "in", ids]] + safe_eval(template.filter_id.domain)
                    for line in self.env[template.sub_object.model].sudo().search(domain):
                        if template.sub_model_object_field_integer.name:
                            order_qty = int(abs(line[template.sub_model_object_field_integer.name])) or 1.0
                        else:
                            order_qty = 1.0
                        if template.sub_model_object_field.name == 'id':
                            lines += [(0, 0, {
                                'model': model,
                                'resource_ref': '%s,%s' % (model, line[template.sub_model_object_field.name] or 0),
                                'res_id': line[template.sub_model_object_field.name],
                                'qty': order_qty})]
                        else:
                            lines += [(0, 0, {
                                'model': model,
                                'resource_ref': '%s,%s' % (model, line[template.sub_model_object_field.name].id or 0),
                                'res_id': line[template.sub_model_object_field.name].id,
                                'qty': order_qty})]
            else:
                result['model'] = template.model
                for record in self.env[template.model].sudo().browse(active_ids):
                    order_qty = 1.0
                    lines += [(0, 0, {
                        'model': template.model,
                        'resource_ref': '%s,%s' % (template.model, record.id or 0),
                        'res_id': record.id,
                        'qty': order_qty})]
            result['barcode_lines'] = lines
            return result
        else:
            return result

    model = fields.Char('Document Model Name')
    barcode_lines = fields.One2many('bf.barcode.line', 'bf_barcode_id', string='Products')
    template_id = fields.Many2one('bf.barcode.template', string="Use template barcode")
    report_template_id = fields.Many2one('ir.actions.report', string="Report template")
    group_resource_ref = fields.Boolean(
        string="Group record reference", help='Group item record reference in report')
    
    def print_barcode_label(self):
        records = []
        if self.group_resource_ref:
            model_res = {(line.model, line.res_id): {'model': line.model, 'res_id': line.res_id, 'qty': 0.0} for line in self.barcode_lines}
            for line in self.barcode_lines:
                model_res.get((line.model, line.res_id)).update({'qty': model_res.get((line.model, line.res_id)).get('qty') + line.qty})
            records = list(model_res.values())
        else:
            for line in self.barcode_lines:
                records.append({'model': line.model, 'res_id': line.res_id, 'qty': line.qty})
        return self.report_template_id.report_action([], data={'barcode_records': records})


class BFBarcodeLine(models.TransientModel):
    _name = 'bf.barcode.line'
    _description = 'BF Barcode Line'

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].sudo().search([])
        return [(model.model, model.name) for model in models]

    @api.model
    def _selection_languages(self):
        return self.env['res.lang'].sudo().get_installed()
    
    @api.model
    def default_get(self, fields):
        result = super(BFBarcodeLine, self).default_get(fields)
        result['res_id'] = self.env['sale.order'].sudo().search([], limit=1)
        return result

    qty = fields.Integer('Qty', default=1, required=True)
    bf_barcode_id = fields.Many2one('bf.barcode', string='Barcode')
    # lot_id = fields.Many2one('stock.production.lot', string='Production Lot')

    lang = fields.Selection(_selection_languages, string='Template Preview Language')
    model = fields.Char('Document Model Name')
    res_id = fields.Integer(string='Record ID')
    resource_ref = fields.Reference(string='Record reference', selection='_selection_target_model', compute='_compute_resource_ref', inverse='_inverse_resource_ref')

    @api.depends('model', 'res_id')
    def _compute_resource_ref(self):
        for preview in self:
            if preview.model:
                preview.resource_ref = '%s,%s' % (preview.model, preview.res_id or 0)
            else:
                preview.resource_ref = False

    def _inverse_resource_ref(self):
        for preview in self:
            if preview.resource_ref:
                preview.res_id = preview.resource_ref.id

    @api.onchange('lang', 'resource_ref')
    def on_change_resource_ref(self):
        # Update res_id and body depending of the resource_ref
        if self.resource_ref:
            self.res_id = self.resource_ref.id

