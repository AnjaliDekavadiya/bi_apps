# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _, api


class Slot(models.Model):

    _name = 'sh.parking.slot'
    _description = 'Parking Slot'

    name = fields.Char(string='Slot no.', required=True,
                       readonly=True, default=lambda self: _('New'),copy=False)
    sh_slot_name = fields.Char(string='Slot Name', required=True,copy=False)

    sh_subslot_qty = fields.Integer(string='Subslot Quantity', required=True,copy=False)
    sh_location_id = fields.Many2one(
        comodel_name="sh.parking.location", string="Location", required=True,copy=False)

    sh_vehicle_id = fields.Many2one(
        comodel_name="sh.parking.vehicle", string="Vehicle", required=True,copy=False)

    sh_charges = fields.Float(string='Charges', required=True,copy=False)
    sh_late_charges = fields.Float(string='Late Charges', required=True,copy=False)
    sh_slot_time = fields.Selection(
        [("days", "Day(s)"), ("hours", "Hour(s)"), ("minutes", "Minute(s)")], string="Time", required=True,copy=False)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id,copy=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, default=lambda self: self.env.company,copy=False)
    sub_slot_line = fields.One2many(
        comodel_name='sh.parking.subslot', inverse_name='sh_slot_id', string='Subslot',copy=False)
    sh_create_record_boolean = fields.Boolean(
        string='sh_create_record_boolean', default=False,copy=False)

    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'sh.parking.slot_no') or _('New')
        vals['sh_create_record_boolean'] = True
        result = super(Slot, self).create(vals)

        if vals["sh_subslot_qty"]:
            for i in range(vals["sh_subslot_qty"]):
                self.env["sh.parking.subslot"].sudo().create({
                    'sh_slot_id': result.id,
                    'sh_vehicle_id': result.sh_vehicle_id.id,
                    'name': self.env['ir.sequence'].next_by_code(
                        'sh.parking.subslot_no') or _('New')
                })
        return result

    def unlink(self):
        for record in self:
            subslot_ids = self.env['sh.parking.subslot'].search(
                [('sh_slot_id', '=', record.id)])
            subslot_ids.unlink()
        super(Slot, self).unlink()
