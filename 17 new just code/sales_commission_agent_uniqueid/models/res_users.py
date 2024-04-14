# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools , _
# from odoo.exceptions import Warning
from odoo.osv import expression
from odoo.exceptions import UserError

class Users(models.Model):
    _inherit = 'res.users'

    custom_number = fields.Char(string="Number", readonly=False, copy=False)
    custom_number_probc = fields.Char(
        string="Number", 
        related="custom_number",
        copy=False,
        readonly=True
    )

    def init(self): #for old users generation of number.
        search_user = self.env['res.users'].search([('custom_number', '=', False)])
        for user in search_user:
            if user.has_group('base.group_user'):
                user.custom_number = self.env['ir.sequence'].next_by_code('res.users.sequence.code')
            elif user.has_group('base.group_portal'):
                user.custom_number = self.env['ir.sequence'].next_by_code('res.users.sequence.code.portal')

        

    @api.model_create_multi
    def create(self, vals_list):
        users = super(Users, self).create(vals_list)
        for user in users:
            if user.has_group('base.group_user'):
                user.custom_number = self.env['ir.sequence'].next_by_code('res.users.sequence.code')
            elif user.has_group('base.group_portal'):
                user.custom_number = self.env['ir.sequence'].next_by_code('res.users.sequence.code.portal')
        return users

    
    def write(self, vals):
        if 'custom_number' in vals and vals.get('custom_number'):
            for rec in self:
                record_found = self.env['res.users'].search([('custom_number', '=', vals['custom_number']), ('id', '!=', rec.id)])
                if record_found:
                    raise UserError(_('The user number must be unique.'))
        return super(Users, self).write(vals)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        user_ids = []
        if operator not in expression.NEGATIVE_TERM_OPERATORS:
            if operator == 'ilike' and not (name or '').strip():
                domain = []
            elif operator in ('ilike', 'like', '=', '=like', '=ilike'):
                domain = expression.AND([
                    args or [],
                    [('custom_number', operator, name)]
                ])
            else:
                domain = [('login', '=', name)]
            user_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        if not user_ids:
            return super(Users, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
            # user_ids = self._search(expression.AND([[('name', operator, name)], args]), limit=limit, access_rights_uid=name_get_uid)
        return user_ids
        
    
