# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MachineJobEstimate(models.TransientModel):
    _name = "machine.job.estimate"
    _description = 'Machine Job Estimate'

    #@api.multi
    def create_job_estimate(self):
        return {
            "view_id" : self.env.ref("odoo_sale_estimates.view_sale_estimate_form").ids,
            "view_mode" : "form",
            "res_model" : "sale.estimate",
            "type" : "ir.actions.act_window",
            "context" : self.env.context,
        }
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
