# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import models, fields, api
from markupsafe import Markup, escape

class MergeTicketWizard(models.TransientModel):

    _name = "helpdesk.ticket.merge.ticket.wizard"
    _description = "Merge Ticket Wizard"


    @api.model
    def _default_sh_check_multi_user(self):
        return self.env.company.sh_display_multi_user if self.env.company.sh_display_multi_user == True else False

    sh_user_id = fields.Many2one('res.users', string='Assigned User',domain = [('share','=',False)])
    ticket_type = fields.Many2one('helpdesk.ticket.type', string='Ticket Type')
    sh_partner_id = fields.Many2one('res.partner', string='Partner',required=True,readonly=True)
    sh_priority = fields.Selection([('0', 'All'),('1', 'Low priority'),('2', 'High priority'), ('3', 'Urgent')], string='Priority', default='0')
    sh_ticket_alarm_ids = fields.Many2many('sh.ticket.alarm', string='Ticket Reminder')
    sh_helpdesk_ticket_ids = fields.Many2many('helpdesk.ticket', string='Tickets',readonly=True)
    sh_team_id = fields.Many2one('helpdesk.team', string='Team')
    sh_user_ids = fields.Many2many('res.users', string='Assign Multi Users',domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    sh_helpdesk_tags = fields.Many2many('helpdesk.tag', string='Tags')
    sh_merge_history = fields.Boolean('Merge History',default=False)    
    sh_select_type = fields.Selection([('new', 'New'), ('existing', 'Existing')],string="Type",default="new",required=True)
    sh_existing_ticket= fields.Many2one('helpdesk.ticket',string="Select Ticket")
    sh_check_multi_user = fields.Boolean('sh_check_multi_user',default=_default_sh_check_multi_user)
    
    sh_select_merge_type = fields.Selection(
        string='Merge Type',
        selection=[
            ('close', 'Close other Tickets'),
            ('cancel', 'Cancel other Tickets'),
            ('done', 'Done other Tickets'),
            ('remove', 'Remove other Tickets'),
            ('do_nothing', 'Do Nothing'),
        ],default="do_nothing"
    )

    def action_merge_tickets(self):
        
        if self.sh_select_type=='new':
            ticket_name='Merge Ticket : ('
            for ticket in  self.sh_helpdesk_ticket_ids:
                ticket_name=ticket_name+'#'+str(ticket.id)+','
            ticket_name=ticket_name[:len(ticket_name)-1]
            ticket_name+=')'
            
            merged_ticket = self.env['helpdesk.ticket'].create({
                'name':ticket_name,
                'partner_id':self.sh_partner_id.id,
                'ticket_type_id':self.ticket_type.id if self.ticket_type else False, 
                'priority':self.sh_priority if self.sh_priority else False,
                'sh_ticket_alarm_ids':[(6,0,self.sh_ticket_alarm_ids.ids)] if self.sh_ticket_alarm_ids else False,
                'user_id':self.sh_user_id.id if self.sh_user_id else False,
                'team_id':self.sh_team_id.id if self.sh_team_id else False,
                'sh_user_ids': [(6,0,self.sh_user_ids.ids)] if self.sh_user_ids.ids else [],
                'tag_ids':[(6,0,self.sh_helpdesk_tags.ids)] if self.sh_helpdesk_tags else []
                })
        else:
            merged_ticket = self.sh_existing_ticket
        
        sorted_tickets = self.sh_helpdesk_ticket_ids.sorted(key=lambda i: i.id)
        product_ids_list=[]
        follower_ids = []
        for ticket in sorted_tickets:
            
            merged_ticket.sh_merge_ticket_ids=[(4,ticket.id)]
            get_messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'),('res_id','=',str(ticket.id))], order='id')
            
            if get_messages and self.sh_merge_history:
                # MERGE MAIL-MESSAGE
                for rec in get_messages:
                    rec.res_id = merged_ticket.id
                if ticket.product_ids:
                    product_ids_list = product_ids_list + ticket.product_ids.ids

            get_activities = self.env['mail.activity'].search([('res_id','=',ticket.id),('res_model','=','helpdesk.ticket')])
        
            # MERGE ACTIVITIES
            if get_activities and self.sh_merge_history:
                for rec in get_activities:
                    rec.res_id = merged_ticket.id
            
            follower_ids = follower_ids + ticket.message_partner_ids.ids
            
        
        # MERGE PRODUCTS
        merged_ticket.product_ids =  [(6,0,product_ids_list)]      
        
        
        # MERGE FOLLOWERS
        merged_ticket.message_subscribe(partner_ids = follower_ids)
        
        # Trigger Onchanges
        # merged_ticket.onchange_partner_id()
        merged_ticket.onchange_category()

        marged_disc=""
        merged_ticket.description = False
        for ticket in self.sh_helpdesk_ticket_ids:
            if ticket.description:
                marged_disc = marged_disc + ticket.name + escape(Markup("<hr/>")) + ticket.description + escape(Markup("<br/>")) if not ticket.description == '<p><br></p>' else False
            
            if self.sh_select_merge_type == 'close':
                ticket.stage_id = self.env.company.close_stage_id.id if self.env.company.close_stage_id else False 
            if self.sh_select_merge_type == 'cancel':
                ticket.stage_id = self.env.company.cancel_stage_id.id if self.env.company.close_stage_id else False 
            if self.sh_select_merge_type == 'done':
                ticket.stage_id = self.env.company.done_stage_id.id if self.env.company.close_stage_id else False
            
            
            if self.sh_existing_ticket and ticket.id == self.sh_existing_ticket.id:
                pass
            else:
                ticket.unlink() if self.sh_select_merge_type == 'remove' else False
        merged_ticket.description = marged_disc

