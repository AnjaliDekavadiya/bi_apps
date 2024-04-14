from odoo import api, fields, models, _
from odoo.exceptions import UserError
 
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    task_type = fields.Selection([
        ('task', 'Task'),
        ('milestone', 'Milestone')
        ], string="Task Type", required=True, default='task')
    color = fields.Integer('Oder color', default=4)
    sale_link_ids = fields.One2many('sale.order.link', 'source_id', string="Order Links")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),        
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)

    @api.model
    def search_read_links(self, domain=None):
        datas = []
        tasks = self.env['sale.order'].search(domain)
        for task in tasks:
            if task.sale_link_ids:                
                for link in task.sale_link_ids:                    
                    link_vals = {
                        'id' : link.id,
                        'source' : task.id,
                        'target': link.target_id.id, 
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas

class SaleOrderLink(models.Model):
    _name = "sale.order.link"
    _description = "Sale Order Links"

    source_id = fields.Many2one('sale.order', string='Order')
    target_id = fields.Many2one('sale.order', string='Target Order', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"), 
        ('1', "Start to Start"), 
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
        ], string="Link Type", required=True, default='1')
