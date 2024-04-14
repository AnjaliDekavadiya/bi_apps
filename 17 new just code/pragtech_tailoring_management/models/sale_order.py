from odoo import models, fields, api, _
import random



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cloth_type_id = fields.Many2one(related='product_template_id.cloth_type', string="Cloth Type")
    description = fields.Char(string="Description", compute='_compute_description', store=True)
    done = fields.Boolean('done')
    

    # ...........................................Compute Description..........................................
    @api.depends('product_template_id.description')
    def _compute_description(self):
        for line in self:
            if line.product_template_id.description:
                line.description = line.product_template_id.description


    def wizard_value_pass(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Measurement',
            'res_model': 'measurement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('pragtech_tailoring_management.view_measurement_wizard_form').id,
            'context': {
                'default_cloth_category_id': self.cloth_type_id.id,
                'default_order_id': self.order_id.id,
            },
        }



class SaleOrder(models.Model):
    _inherit = "sale.order"

    done = fields.Boolean('done', default=False)
    state = fields.Selection(selection_add=[('tailor assigned', 'Tailor Assigned'),
                                            ('ready to deliver', 'Ready To Deliver'),
                                            ('shipped','Shipped'), ('delivered', 'Delivered')])
    random_number = fields.Char(string='Random Number', readonly=True, store=True)

    # ...........................................Specific Tailor Record Form View..........................................
    def current_tailor_record(self):
        tailor_id = self.env['tailoring.tailor'].search([('order_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tailor',
            'res_id': tailor_id.id,
            'res_model': 'tailoring.tailor',
            'view_mode': 'form',
            'target': 'current',
            'view_id': self.env.ref('pragtech_tailoring_management.tailor_form_view').id
        }

    # ...........................................Specific Measrement Record Form View..........................................
    def current_measurement_record(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Measurement',
            'domain': [('order_id', '=', self.id)],
            'res_model': 'tailoring.customer.measurement',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({'done': False})
        measurement_records = self.env['tailoring.customer.measurement'].search([
            ('order_id', '=', self.id),
            ('state', '=', 'draft')
        ])
        measurement_records.write({'state': 'confirmed'})

        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(self.id)
        email_values = {
            'email_from': self.company_id.email,
            'email_to': self.partner_id.email,  
            'subject': 'Your Payment is Confirmed'
        }
        template = self.env.ref('pragtech_tailoring_management.mail_template_payment_confirm')
        template.send_mail(sale_order.id, force_send=True, email_values=email_values)

        return res