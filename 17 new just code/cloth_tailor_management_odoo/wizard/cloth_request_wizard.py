# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ClothRequestWizard(models.TransientModel):
    _name = "cloth.request.wizard"
    _description = 'Cloth Request Wizard'

    @api.model
    def default_get(self, fields):
        res = super(ClothRequestWizard, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'crm.lead':
            record = self.env[model].browse(active_id)
            res.update({
                'partner_id': record.partner_id.id,
                'company_id': record.company_id.id,
                'lead_id': record.id
            })
        return res

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')],
        string="Gender",
        default='male'
    )
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        default=lambda self: self.env.company
    )
    cloth_type_id = fields.Many2one(
        'cloth.measurement.details',
        string="Customer Measurement",
        domain = "[('partner_id', '=', partner_id)]"
    )
    quantity = fields.Float(
        string="Quantity",
        required=True   
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure",
        required=True
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string="Lead"
    )

    def create_cloth_request(self):
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'gender': self.gender,
            'cloth_type_id': self.cloth_type_id.id,
            'quantity': self.quantity,
            'uom_id': self.uom_id.id,
            'lead_id': self.lead_id.id,
        }
        request_id = self.env['cloth.request.details'].create(vals)
        if request_id:
            request_id.action_get_measurment_line()
        #action = self.env.ref("cloth_tailor_management_odoo.action_cloth_request_details").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.action_cloth_request_details')
        action['views'] = [(self.env.ref('cloth_tailor_management_odoo.cloth_request_details_form_view').id, 'form')]
        action['res_id'] = request_id.id
        return action