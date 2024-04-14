# -*- coding: utf-8 -*-

# from openerp import models, fields, api
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
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self.env.user.has_group('sales_person_customer_access.group_restricted_customer'):
            # partner_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
            if operator == 'ilike' and not (name or '').strip():
                domain = []

            elif operator in ('ilike', 'like', '=', '=like', '=ilike'):
                domain = expression.AND([
                    args or [],
                    [('name', operator, name)]
                ])
                # partner_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
                # return models.lazy_name_get(self.browse(partner_ids).with_user(name_get_uid))
            # return super(ResPartner, self)._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(ResPartner, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        # return super(ResPartner, self)._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    # @api.model
    # def _name_search_dummy(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     if self.env.user.has_group('sales_person_customer_access.group_restricted_customer'):
    #         # partner_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
    #         if operator == 'ilike' and not (name or '').strip():
    #             domain = []

    #         elif operator in ('ilike', 'like', '=', '=like', '=ilike'):
    #             domain = expression.AND([
    #                 args or [],
    #                 [('name', operator, name)]
    #             ])
    #             # partner_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
    #             # return models.lazy_name_get(self.browse(partner_ids).with_user(name_get_uid))
    #         return super(ResPartner, self)._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
    #     return super(ResPartner, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
    #     # return super(ResPartner, self)._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('do_not_include'):
            pass 
        else:
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            # partners = self.env['res.partner'].search([('salesperson_ids','in', self.env.user.id)],limit=1)
            if restricted_customer:
                if self._context.get('custom_partner') == True:
                    return super(ResPartner, self.with_context(do_not_include=True))._search(args, offset, limit, order, count, access_rights_uid)
                args = [('salesperson_ids','in',self.env.user.ids)] + list(args)
        return super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)

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

    #@api.model
    #def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        if res.parent_id and res.parent_id.salesperson_ids:
            self.set_parent_salesperson_ids(res, res.parent_id)
        return res

#    @api.multi #odoo13
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
