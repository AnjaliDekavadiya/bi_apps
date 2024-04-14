# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    custom_team_id = fields.Many2one(
        'crm.team', 
        string='Sales Team'
    )

    def _compute_meeting_count(self):
        result = self.with_context(custom_partner=True)._compute_meeting()
        for p in self:
            p.meeting_count = len(result.get(p.id, []))

   
    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
    #     if restricted_customer:
    #         if self._context.get('custom_partner') == True:
    #             return super(ResPartner, self.with_context(do_not_include=True))._search(domain, offset, limit, order, access_rights_uid)
    #         domain = ['|',('salesperson_ids','in',self.env.user.ids),('custom_team_id.member_ids','in',self.env.user.ids)] + list(domain)
    #     return super(ResPartner, self.with_context(do_not_include=True))._search(domain, offset, limit, order, access_rights_uid)



    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     if not self.env.context.get('do_not_include'):
    #         restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
    #         if restricted_customer:
    #             domain = ['|',('salesperson_ids','in',self.env.user.ids),('custom_team_id.member_ids','in',self.env.user.ids)]
    #             if not any(arg[0] == 'id' or arg[0] == 'parent_id' for arg in domain):
    #                 domain += domain
    #     return super(ResPartner, self.with_context(do_not_include=True))._search(domain, offset, limit, order, access_rights_uid)


    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if not self.env.context.get('do_not_include'):
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                salesteam_domain = ['|',('salesperson_ids','in',self.env.user.ids),('custom_team_id.member_ids','in',self.env.user.ids)]
                if not any(arg[0] == 'id' or arg[0] == 'parent_id' for arg in domain):
                    domain += salesteam_domain
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

    def set_parent_salesteam_ids(self, partner_id, parent_id):
        if parent_id:
            partner_id.custom_team_id = parent_id.custom_team_id.id
        else:
            partner_id.custom_team_id = False
        return True

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        if res.parent_id and res.parent_id.custom_team_id:
            self.set_parent_salesteam_ids(res, res.parent_id)
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for rec in self:
            if 'parent_id' in vals:
                parent_id = self.browse(vals.get('parent_id', False))
                self.set_parent_salesteam_ids(rec, parent_id)
            if 'custom_team_id' in vals:
                if rec.child_ids:
                    for child_id in rec.child_ids:
                        child_id.custom_team_id = vals.get('custom_team_id', False)
        return res
