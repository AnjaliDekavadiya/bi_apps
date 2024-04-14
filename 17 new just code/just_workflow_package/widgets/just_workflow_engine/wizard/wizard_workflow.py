# -*- coding: utf-8 -*-
##############################################################################

from odoo import api, fields, models, _
import datetime

class wizard_workflow_message(models.TransientModel):
    _name = 'wizard.workflow.message'
    _description = 'Workflow Message'
    
    name = fields.Text(u'Note', default=_('Agree'))
    logType = fields.Integer('logType', default=0)
    user_ids = fields.Many2many('res.users', string='加签人')
    note_type = fields.Selection([
        ('Agree', 'Agree'),
        ('Restart', 'Refuse and reStart'),
        ('Stop', 'Refuse and Stop'),
    ], string='Trans Type', default='Agree')

    def _compute_binding_info(self):
        type_dict = dict(self.fields_get(allfields=['note_type'])['note_type']['selection'])
        self.bind_info = type_dict[self.note_type]
       
    bind_info = fields.Char(compute='_compute_binding_info')

    def apply(self):
        self.ensure_one()
        ctx = self.env.context
        note_t = self.env['workflow.trans'].browse(int(ctx.get('trans_id')))
        note = note_t.name + _('Review comments')
        record = self.env[ctx.get('active_model')].browse(ctx.get('active_id'))
        if (self.user_ids):
            self.env['todo.activity'].add_todo(
                 record,
                 datetime.date.today(),
                 [x.id for x in self.user_ids],
                 note_t.name,
                 _('Countersignature opinion'),
                 note_t.workflow_id.view_id,
                 'stage_workflow',
                 self.env.ref("just_workflow_engine.menu_workflow_root", False),
                 ctx.get('active_model'),
                 ctx.get('active_id'),
                 context = ctx,
                 note_type = 'many',
                 trans_id = note_t.id)

        auto_note = self.name == _('Agree') and self.bind_info or self.name
        todo_id = ctx.get('workflow_todo_id')
        if (todo_id):
            todo = self.env['todo.activity'].browse(int(todo_id))
            todo.done()
            note = note_t.name + todo.summary

            todos = self.env['todo.activity'].search(['&',('trans_id','=',note_t.id),'&',('res_id','=',ctx.get('active_id')),('todo_state','!=','complete')])          
            if (todos):
                note_t.make_log(record.name, record.id, note + ':' + auto_note)
                return True

        if (self.note_type == 'Restart'):
            record.workflow_button_reset(note_t.workflow_id.id)
            return True

        if (self.note_type == 'Stop'):
            record.workflow_button_stop(note_t.workflow_id.id)
            todos = self.env['todo.activity'].search(['&',('trans_id','=',note_t.id),'&',('res_id','=',ctx.get('active_id')),('todo_state','!=','complete')])
            todos.write({'todo_state':'complete'})
            return True

        record.with_context(trans_id=note_t.id,x_workflow_vstate=False).workflow_action(note + ':' + auto_note)
        return True
