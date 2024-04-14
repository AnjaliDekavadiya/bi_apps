# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BFBarcodeTemplate(models.Model):
    _name = 'bf.barcode.template'
    _description = 'BF barcode template'

    name = fields.Char('Name', translate=True)
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Applies to', required=True,
        domain=[('transient', '=', False)], ondelete='cascade',
        help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    one2many = fields.Boolean(string='Field One2many')
    sidebar_action_id = fields.Many2one(
        'ir.actions.act_window', 'Sidebar action', readonly=True, copy=False,
        help="Sidebar action to make this template available on records "
             "of the related document model")
    model_object_field = fields.Many2one(
        'ir.model.fields', string="Field", compute_sudo=True,
        help="Select target field from the related document model.\n"
             "If it is a relationship field you will be able to select "
             "a target field at the destination of the relationship.")
    sub_object = fields.Many2one('ir.model', 'Sub-model', compute='_compute_sub_object',
                                 help="When a relationship field is selected as first field, "
                                      "this field shows the document model the relationship goes to.", store=True)
    sub_object_model = fields.Char(related='sub_object.model')
    filter_id = fields.Many2one('ir.filters', 'Filter', domain="[('model_id', '=', sub_object_model)]")
    sub_model_object_field = fields.Many2one('ir.model.fields', 'Sub-field', compute_sudo=True,
                                             help="When a relationship field is selected as first field, "
                                                  "this field lets you select the target field within the "
                                                  "destination document model (sub-model).")
    sub_model_object_field_integer = fields.Many2one('ir.model.fields', 'Sub-field quantity', compute_sudo=True,
                                             help="When a relationship field is selected as first field, "
                                                  "this field lets you select the target field within the "
                                                  "destination document model (sub-model).")

    report_model = fields.Char(string="Report template model", compute='_compute_report_model', store=True)
    report_template_id = fields.Many2one('ir.actions.report', string="Report template")

    @api.depends('model_id', 'one2many', 'sub_model_object_field')
    def _compute_report_model(self):
        for record in self:
            if not record.one2many:
                record.report_model = record.model
            else:
                if record.sub_model_object_field.name == 'id':
                    record.report_model = record.sub_model_object_field.model_id.model
                else:
                    record.report_model = record.sub_model_object_field.relation
    
    @api.depends('model_object_field')
    def _compute_sub_object(self):
        for record in self:
            if record.model_object_field:
                if record.model_object_field.ttype in ['many2one', 'one2many', 'many2many']:
                    model = record.env['ir.model']._get(record.model_object_field.relation)
                    if model:
                        record.sub_object = model.id
                else:
                    record.sub_object = False
            else:
                record.sub_object = False
    
    def action_create_sidebar_action(self):
        # sms/models/sms_template.py (ActWindow.create)
        ActWindow = self.env['ir.actions.act_window']
        view = self.env.ref('report_extend_bf_barcode.bf_barcode_view_form')

        for template in self:
            button_name = template.name or _('Action barcode templates')
            action = ActWindow.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'bf.barcode',
                'context': "{'default_template_id' : %d, 'default_res_ids': active_ids, 'default_res_id': active_id}" % (template.id),
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'binding_model_id': template.model_id.id,
            })
            template.write({'sidebar_action_id': action.id})
        return True
    
    def action_unlink_sidebar_action(self):
        for template in self:
            if template.sidebar_action_id:
                template.sidebar_action_id.unlink()
        return True
    
    def unlink(self):
        for template in self:
            if template.sidebar_action_id:
                template.sidebar_action_id.unlink()
        return super(BFBarcodeTemplate, self).unlink()
    
    @api.onchange('model_id')
    def _onchange_model_id(self):  
        self.model_object_field = False
        self.filter_id = False
        self.sub_model_object_field = False
        self.sub_model_object_field_integer = False
        self.report_template_id = False

    @api.onchange('model_object_field')
    def _onchange_model_object_field(self):  
        self.filter_id = False
        self.sub_model_object_field = False
        self.sub_model_object_field_integer = False
        self.report_template_id = False
