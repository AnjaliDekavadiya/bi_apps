from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"
    
    task_type = fields.Selection([
        ('task', 'Task'),
        ('milestone', 'Milestone')
        ], string="Task Type", required=True, default='task')
    color = fields.Integer('Order Color', default=4)
    workorder_link_ids = fields.One2many('mrp.workorder.link', 'source_id', string="Link Orders")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)    
    
    @api.model
    def search_read_links(self, domain=None):
        datas = []
        workorders = self.env['mrp.workorder'].search(domain)
        for workorder in workorders:
            if workorder.workorder_link_ids:                
                for link in workorder.workorder_link_ids:                    
                    link_vals = {
                        'id' : link.id,
                        'source' : workorder.id,
                        'target': link.target_id.id, 
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas

class MrpWorkorderLink(models.Model):
    _name = "mrp.workorder.link"
    _description = "MRP Workorder Links"

    source_id = fields.Many2one('mrp.workorder', string='Workorder')
    target_id = fields.Many2one('mrp.workorder', string='Target Workorder', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"), 
        ('1', "Start to Start"), 
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
        ], string="Link Type", required=True, default='1')