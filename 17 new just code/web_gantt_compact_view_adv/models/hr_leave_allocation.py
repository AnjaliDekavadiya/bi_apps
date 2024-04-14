from odoo import api, fields, models, _
from odoo.exceptions import UserError
 
class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"
    
    task_type = fields.Selection([
        ('task', 'Task'),
        ('milestone', 'Milestone')
        ], string="Task Type", required=True, default='task')
    color = fields.Integer('Leave color', default=4)
    leave_link_ids = fields.One2many('hr.leave.allocation.link', 'source_id', string="Order Links")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),        
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)

    @api.model
    def search_read_links(self, domain=None):
        datas = []
        tasks = self.env['hr.leave.allocation'].search(domain)
        for task in tasks:
            if task.leave_link_ids:                
                for link in task.leave_link_ids:                    
                    link_vals = {
                        'id' : link.id,
                        'source' : task.id,
                        'target': link.target_id.id, 
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas

class HolidaysAllocationLink(models.Model):
    _name = "hr.leave.allocation.link"
    _description = "Leave Report Calendar Links"

    source_id = fields.Many2one('hr.leave.allocation', string='Leave')
    target_id = fields.Many2one('hr.leave.allocation', string='Target Leave', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"), 
        ('1', "Start to Start"), 
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
        ], string="Link Type", required=True, default='1')