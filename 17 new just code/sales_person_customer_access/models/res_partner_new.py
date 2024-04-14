# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )

    def _compute_meeting_count(self):
        result = self.with_context(custom_partner=True)._compute_meeting()
        for p in self:
            p.meeting_count = len(result.get(p.id, []))

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        if self.env.user.has_group('sales_person_customer_access.group_restricted_customer'):
            if operator == 'ilike' and not (name or '').strip():
                domain = []

            elif operator in ('ilike', 'like', '=', '=like', '=ilike'):
                domain = expression.AND([
                    # args or [],
                    domain or [],
                    [('name', operator, name)]
                ])
               
            return self._search(expression.AND([domain, domain]), limit=limit, order=order)

        return super(ResPartner, self)._name_search(name, domain, operator, limit, order)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if not self.env.context.get('do_not_include'):
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                if self._context.get('custom_partner') == True:
                    # return super(ResPartner, self.with_context(do_not_include=True))._search(args, offset, limit, order, count, access_rights_uid)
                    return super(ResPartner, self.with_context(do_not_include=True))._search(domain, offset, limit, order, access_rights_uid)
                salesperson_domain = [('salesperson_ids', 'in', self.env.user.ids)]
                if not any(arg[0] == 'id' or arg[0] == 'parent_id' for arg in domain):
                    domain += salesperson_domain
        return super(ResPartner, self)._search(domain, offset, limit, order, access_rights_uid)

    def read(self, fields=None, load='_classic_read'):
        partners = super(ResPartner, self).read(fields=fields, load=load)
        if len(partners) == 1:
            if self.env.user.has_group("sales_person_customer_access.group_restricted_customer"):
                partner_restrict_access_config = self.env['res.partner'].sudo().search([('salesperson_ids', 'in', self.env.user.ids)])
                if partner_restrict_access_config:
                    for partner in partners:
                        if partner.get('id') and partner.get('id') not in partner_restrict_access_config.ids:
                            raise AccessError(_("You don't have the access!"))
        return partners



    def set_parent_salesperson_ids(self, partner_id, parent_id):
        if parent_id:
            partner_id.salesperson_ids = [(6, 0, parent_id.salesperson_ids.ids)]
        else:
            partner_id.salesperson_ids = [(6, 0, [])]
        return True

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        if res.parent_id and res.parent_id.salesperson_ids:
            self.set_parent_salesperson_ids(res, res.parent_id)
        return res


    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for rec in self:
            if 'parent_id' in vals:
                parent_id = self.browse(vals.get('parent_id', False))
                self.set_parent_salesperson_ids(rec, parent_id)
            if 'salesperson_ids' in vals:
                if rec.child_ids:
                    for child_id in rec.child_ids:
                        child_id.salesperson_ids = vals.get('salesperson_ids', [])
        return res
