# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    _inherit = "project.project"

#     @api.multi               #odoo13
#    def show_inspection(self):
    def action_show_phases(self):
        self.ensure_one()
        # res = self.env.ref('odoo_project_phases.action_phase_type')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('odoo_project_phases.action_phase_type')
        res['domain'] = str([('project_id', '=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
