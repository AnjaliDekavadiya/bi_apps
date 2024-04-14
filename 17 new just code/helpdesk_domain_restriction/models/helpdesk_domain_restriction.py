from odoo import models, fields, api, _
# from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from odoo.exceptions import UserError


class HelpdeskDomainRestriction(models.Model):
    
    _name = 'helpdesk.domain.restriction'
    _description = 'HelpdeskDomainRestriction'

    email_ids = fields.Many2many('helpdesk.domain', string='Domains')
    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True)

    @api.model
    def create(self, vals):
        data = self.env['helpdesk.domain.restriction'].search([])
        if data:
            # raise UserError(_('Only one record allowed.'))
            raise UserError(_('Only one record allowed.'))
        else:
            return super(HelpdeskDomainRestriction, self).create(vals)
