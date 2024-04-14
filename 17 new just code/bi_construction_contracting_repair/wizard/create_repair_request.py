# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class CreateRepairRequest(models.TransientModel):
    _name = 'create.repair.request'
    _description = "Create Repair Request"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, index=True,
                                 help="This Wizard Cereate Repair Request from Job Order.")
    new_order_line_ids = fields.One2many('createrepair.requestwizard', 'new_order_line_id', string="Order Line")
    new_order_line = fields.Many2one('machine.repair')

    def action_create_repair_request(self):
        self.ensure_one()
        job = self.env['job.order'].browse(self.env.context.get('active_id'))
        for product in self.new_order_line_ids:
            res = self.env['machine.repair']
            repair_list = []
            for repair in product.machine_service_type_id:
                repair_list.append(repair.id)
            res.create({
                'partner_id': self.partner_id.id,
                'product_id': product.product_id.id,
                'name': product.product_id.name,
                'company_id': job.user_id.company_id.id,
                'client_email': job.user_id.email,
                'damage': product.damage,
                'project_id': job.project_id.id,
                'machine_repair_team_id': product.machine_repair_team_id.id,
                'analytic_account_id': product.analytic_account_id.id,
                'machine_services_id': product.machine_services_id.id,
                'machine_service_type_id': [(6, 0, repair_list)],
                'problem': product.problem,
                'technician_id': self.env.uid,
            })
        return


class CreateRepairRequestWizard(models.TransientModel):
    _name = 'createrepair.requestwizard'
    _description = "Create Repair Request Wizard"

    new_order_line_id = fields.Many2one('create.repair.request')
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company')
    client_email = fields.Char(string='Email')
    product_id = fields.Many2one('product.product', string='Product')
    damage = fields.Text(string='Repair Description')
    machine_repair_team_id = fields.Many2one('machine.repair.team', string='Machine Repair Team')
    analytic_account_id = fields.Many2one('account.analytic.line', string='Analytic Account')
    machine_services_id = fields.Many2one('machine.services', string="Machine Services")
    machine_service_type_id = fields.Many2many('machine.service.type', string="Repair Type")
    lot_id = fields.Many2one('stock.lot', string="Lot")
    problem = fields.Text(string="Problem")

