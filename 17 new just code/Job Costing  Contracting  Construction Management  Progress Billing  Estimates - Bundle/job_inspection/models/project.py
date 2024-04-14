# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    _inherit = "project.project"

    # @api.multi
    def show_inspection(self):
        self.ensure_one()
        # res = self.env.ref('job_inspection.action_job_order_inspection')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('job_inspection.action_job_order_inspection')
        res['domain'] = str([('project_id','=', self.id)])
        res['context'] = {'default_project_id':self.id,'default_analytic_id':self.analytic_account_id.id}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
