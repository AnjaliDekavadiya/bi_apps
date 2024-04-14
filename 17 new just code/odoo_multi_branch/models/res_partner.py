# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        tracking=True,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        admin_user = self.env.user.has_group('base.group_erp_manager')
        if  not admin_user and not self._context.get("from_multi_branch", False) and  any(arg[0] == 'company_branch_id' for arg in domain):
            domain = ['|',('company_branch_id','=',False), ('company_branch_id', '=', self.env.user.company_branch_id.id)] + list(domain)
        return super(ResPartner, self)._search(domain, offset, limit, order, access_rights_uid)


#    @api.multi odoo13
    def read(self, fields=None, load='_classic_read'):
        read_partner = super(ResPartner, self).read(fields, load=load)
        if len(read_partner) == 1:
            admin_user = self.env.user.has_group('base.group_erp_manager')
            if admin_user or self._context.get("from_multi_branch", False):
                return read_partner
            for partner in read_partner:
                if partner.get("company_branch_id") and self.env.user.company_branch_id.id != partner["company_branch_id"]:
                    if isinstance(partner["company_branch_id"] , tuple) and self.env.user.company_branch_id.id != partner["company_branch_id"][0]:
                        raise ValidationError("You are not allowed to access")
        return read_partner
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
