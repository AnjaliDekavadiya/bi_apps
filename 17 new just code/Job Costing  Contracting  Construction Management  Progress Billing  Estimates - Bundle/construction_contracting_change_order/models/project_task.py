# -*- coding: utf-8 -*-

# from openerp import models, api
from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.task'

    # @api.multi #odoo13
    def show_changeorder(self):
        self.ensure_one()
        # res = self.env.ref('construction_contracting_change_order.action_construction_contract_change_order')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('construction_contracting_change_order.action_construction_contract_change_order')
        res['domain'] = str([('task_id', '=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
