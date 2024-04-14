from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class FleetPassengers(models.Model):
    _name = "fleet.passengers"
    _inherit = ['mail.thread']
    _description = "Fleet Passengers"
    _order = 'id desc'
    _rec_name = 'partner_id'
    _rec_names_search = ['partner_id', 'vehicle_id']

    partner_id = fields.Many2one("res.partner", string="Partner", tracking=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string='Vehicle', tracking=True)
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('active','partner_id')
    def _check_partner_id(self):
        for rec in self:
            active = self.env['fleet.passengers'].search_count([('active', '=', True),('partner_id', '=', rec.partner_id.id)])
            if active > 1:
                raise ValidationError("Passengers is already here!")