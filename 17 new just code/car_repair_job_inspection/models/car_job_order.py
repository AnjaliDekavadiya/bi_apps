# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Task(models.Model):
    _inherit = "project.task"

    # @api.multi #odoo13
    def car_show_repair_inspection(self):
        self.ensure_one()
        # res = self.env.ref('car_repair_job_inspection.action_car_repair_order_inspection')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.actions']._for_xml_id('car_repair_job_inspection.action_car_repair_order_inspection')
        res['domain'] = str([('task_id','=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
