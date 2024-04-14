# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    _inherit = "project.project"

    # @api.multi #odoo13
    def car_show_repair_inspection(self):
        self.ensure_one()
        # res = self.env.ref('car_repair_job_inspection.action_car_repair_order_inspection')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.actions']._for_xml_id('car_repair_job_inspection.action_car_repair_order_inspection')
        res['domain'] = str([('project_id','=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
