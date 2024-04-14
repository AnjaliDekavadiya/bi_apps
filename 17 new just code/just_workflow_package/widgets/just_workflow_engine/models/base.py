# -*- coding: utf-8 -*-
##############################################################################
import logging

from lxml import etree

from odoo import api, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.models import BaseModel as BM
from odoo.addons.base.models.ir_ui_view import Model as VM
import datetime
import re, json

_logger = logging.getLogger(__name__)

## odoo.workflow.workitem.workflow_expr_eval_expr
def workflow_trans_condition_expr_eval(self, lines):
    result = False
    #_logger.info('condition_expr_eval %s' % lines)
    for line in lines.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line == 'True':
            result = True
        elif line == 'False':
            result = False
        else:
            result = eval(line)
    return result

default_create = BM.create

def default_create_new(self, vals):
    id = default_create(self, vals)
    ctx = self.env.context
    todo_id = ctx.get('workflow_todo_id')
    if todo_id:
        todo = self.env['todo.activity'].browse(int(todo_id))
        if todo.real_model == self._name:
            todo.write({'real_id':id})
    return id
        
default_write = BM.write

def default_write_new(self, vals):
    res = default_write(self, vals)
    event_model = self.env['ir.config_parameter'].sudo().get_param('event_model')
    if len(self) == 1 and event_model and self._name in event_model:
        ctx = self.env.context.copy()
        todos = self.env['todo.activity'].search([('real_model','=',self._name),('real_id','=',self.id),('todo_state','!=','complete')])
        for todo in todos:
            trans = self.env['workflow.trans'].browse(todo.trans_id)
            if self.workflow_trans_condition_expr_eval(trans.task_condition):
                todo.done()
                order = self.env[todo.res_model].browse(todo.res_id)
                ctx.update({'trans_id':trans.id})
                order.with_context(ctx).workflow_action(trans.name + _(' has done.'))
                
    return res
    
# Set default state
default_get_old = BM.default_get

@api.model
def default_get_new(self, fields_list):
    res = default_get_old(self, fields_list)
    if 'x_workflow_state' in fields_list:
        res.update({'x_workflow_state': self.env['workflow.base'].get_default_state(self._name)})
    return res

def workflow_button_action(self):
    ctx = self.env.context.copy()
    t_id = int(self.env.context.get('trans_id'))
    trans = self.env['workflow.trans'].browse(t_id)
    _logger.info('workflow_button_action %s' % self.env.context)
    ctx.update({'workflow_active_id': self.id, 'workflow_active_ids': self.ids})
    if trans.trans_type == 'note':
        logtype = 1
        if not ctx.get('workflow_todo_id') or self.env['log.workflow.trans'].search([('res_id', '=', self.id), ('trans_id', '=', t_id),('create_uid','=',self.env.user.id)], limit=1):
            logtype = 0
        ctx.update({'default_logType': logtype})
        return {
            'name': _(u'Flow Approve'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'wizard.workflow.message',
            'type': 'ir.actions.act_window',
            # 'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    elif trans.trans_type == 'task':
        ctx.update({'workflow_task_model': trans.task_model,'x_workflow_vstate':trans.node_from.id})
        if trans.context:
            ctx.update(eval(trans.context))
        self.env['todo.activity'].add_todo(
                 self,
                 datetime.date.today(),
                 trans.user_ids.ids or [self.env.uid],
                 trans.name,
                 _('Todo Task'),
                 trans.model_view_id,
                 'stage_workflow',
                 trans.menu_id,
                 trans.task_model,
                 eval(trans.real_id),
                 context = ctx,
                 note_type = 'one',
                 trans_id = trans.id)
    elif trans.trans_type == 'time':
        self.env['todo.activity'].add_todo(
                 self,
                 datetime.date.today(),
                 trans.user_ids.ids or [self.env.uid],
                 trans.name,
                 _('Event Detection'),
                 trans.model_view_id,
                 'stage_state',
                 trans.menu_id,
                 trans.task_model,
                 eval(trans.real_id),
                 context = ctx,
                 note_type = 'one',
                 trans_id = trans.id)
    else:
        return self.with_context(ctx).workflow_action()

def workflow_buttons_action(self):
    ctx = self.env.context.copy()
    _logger.info('workflow_button_action %s' % self.env.context)
    t_id = int(self.env.context.get('buttons_id'))
    button = self.env['workflow.buttons'].browse(t_id)
    ctx.update({'workflow_active_id': self.id, 'workflow_active_ids': self.ids})
    return button.with_context(ctx).run()

def workflow_action(self, message=''):
    t_id = int(self.env.context.get('trans_id'))
    trans = self.env['workflow.trans'].browse(t_id)

    # condition_ok = eval(trans.condition)
    condition_ok = workflow_trans_condition_expr_eval(self, trans.condition)
    #_logger.info('>>>>>>%s: %s, %s', trans.condition, condition_ok, self.env.context)

    if not condition_ok:
        if trans.trans_type in ['auto','task','time']:
            _logger.info('condition false:%s', trans.condition)
            return True
        else:
            raise UserError(_(u'Th condition is not allow to trans, Pleas contract with Administrator'))
            return False
        
    # check repeat trans
    if not trans.is_backward:
        if self.env['log.workflow.trans'].search([('res_id', '=', self.id), ('trans_id', '=', t_id),('create_uid','=',self.env.user.id)], limit=1):
            raise UserError(_('The transfer had finish'))
            return False;

    # check note
    # if trans.need_note and not self.x_workflow_note:
    #    raise Warning(_('The transfer can not empty note'))

    if (message == ''):
        message = trans.name

    log = trans.make_log(self.name, self.id, message)
    # self.x_workflow_note = False

    # check  can be trans
    node_to = trans.node_to
    node_from = trans.node_from
    can_trans = node_to.check_trans_in(self.id)
    
    if can_trans:
        self.write({'x_workflow_state': str(node_to.id)})
        self.write({'x_workflow_approve_user': False})
        trans_approve_users = []
        if trans.is_approve and not node_to.is_stop:
            for to in node_to.out_trans:
                if workflow_trans_condition_expr_eval(self, to.condition):
                    if to.user_ids:
                        trans_approve_users = to.user_ids.ids
                        self.write({'x_workflow_approve_user': ','.join(to.user_ids.mapped('name'))})
                        break
                    if to.group_ids:
                        employee_manager = self.env.user.employee_id.parent_id
                        employee_manager_has_group = False
                        if employee_manager:
                            for name in to.xml_groups.split(','):
                                if employee_manager.user_id.has_group(name):
                                    employee_manager_has_group = True
                                    break
                            if employee_manager_has_group:
                                trans_approve_users.append(employee_manager.user_id.id)
                                self.write({'x_workflow_approve_user': employee_manager.name})

        action, arg = node_to.action, node_to.arg
        # action
        if trans.is_backward:
            node_to.backward_cancel_logs(self.id)
        else:
            if action:
                _logger.info('======action:%s, arg:%s', action, arg)
                if arg:
                    getattr(self, action)(eval(arg))
                else:
                    getattr(self, action)()

        # 2:calendar event
        if node_to.event_need:
            node_to.make_event(self.name,trans_approve_users, self)

        # post todo task when is note type
        ctx = self.env.context.copy()
        todo_trains = filter(lambda t: t.trans_type in ['note'], node_to.out_trans)
        ctx.update({'workflow_active_id': self.id, 'workflow_active_ids': self.ids, 'x_workflow_vstate':node_to.id})
        for note_t in todo_trains:
            self.env['todo.activity'].add_todo(
                 self,
                 datetime.date.today(),
                 note_t.user_ids.ids or [self.env.uid],
                 note_t.name,
                 _('Review comments'),
                 note_t.workflow_id.view_id,
                 'stage_approve',
                 self.env.ref("just_workflow_engine.menu_workflow_root", False),
                 self._name,
                 self.id,
                 context = ctx,
                 note_type = 'many',
                 trans_id = note_t.id)

        # # message to user
        # self.message_post(
        #     body='%s %s' % (self.name, node_to.name),
        #     message_type="comment",
        #     subtype="mail.mt_comment",
        #     partner_ids=[u.partner_id.id for u in node_to.event_users],
        # )

        # 3 auto trans
        auto_trains = filter(lambda t: t.trans_type in ['auto','task','time'], node_to.out_trans)
        for auto_t in auto_trains:
            self.with_context(trans_id=auto_t.id).workflow_button_action()
    cx = self.env.context.copy() or {}
    return trans.with_context(cx).run()


def workflow_button_show_log(self):
    ctx = self.env.context.copy()
    ctx.update({'workflow_active_id': self.id, 'workflow_active_ids': self.ids, 'default_logType': 0})
    return {
        'name': _(u'Workflow approval log'),
        'view_type': 'form',
        "view_mode": 'form',
        'res_model': 'wizard.workflow.message',
        'type': 'ir.actions.act_window',
        # 'view_id': False,
        'target': 'new',
        'context': ctx,
    }

def workflow_button_link(self):
    self.ensure_one()
    workflow_id = self.env.context.get('workflow_id')
    view_id = self.env.ref("just_workflow_engine.view_workflow_base_diagram").id
    action = {
        'name': _('Diagram'),
        'type': 'ir.actions.act_window',
        'view_mode': 'diagram_plus',
        'view_id': view_id,
        'target': 'current',
        'res_model': 'workflow.base',
        'res_id': workflow_id,
        'context': {'workflow_id': workflow_id, 'res_model': self._name, 'res_id': self.id,'form_view_initial_mode': 'view'},
    }
    return action

def workflow_button_reset(self, workflow_id=False):
    logs = self.env['log.workflow.trans'].search([('res_id', '=', self[0].id), ('model', '=', self._name)])
    logs.write({'active': False})
    workflow_id = workflow_id or self.env.context.get('workflow_id')
    state = self.env['workflow.base'].browse(workflow_id).default_state
    self.write({'x_workflow_state': state})
    return True

def workflow_button_stop(self, workflow_id=False):
    #logs = self.env['log.workflow.trans'].search([('res_id', '=', self[0].id), ('model', '=', self._name)])
    #logs.write({'active': False})
    workflow_id = workflow_id or self.env.context.get('workflow_id')
    state = self.env['workflow.base'].browse(workflow_id).stop_state
    self.write({'x_workflow_state': state})
    return True

old_fields_view_get = VM.get_view

def update_fields_view(self, view_id, res):
    """
        Updates fields attributes.
        :param view_type: Type of view now rendering.
        :param res: View resource data.
        :return: Updated view resource.
    """
    # Objects
    workflow_obj = self.env['workflow.base']
    user_obj = self.env['res.users']
    # Variables
    model = self._name
    uid = self._uid
    workflow_rec = workflow_obj.search([('model_id', '=', model)])
    arch = etree.fromstring(res['arch'])
    is_workflow_from = arch.xpath("//field[@name='x_workflow_state']")
    if not workflow_rec.isActive or is_workflow_from is None:
        return res

    # Helper Functions
    def _get_external_id(group):
        arr = []
        ext_ids = group._get_external_ids()
        for ext_id in ext_ids:
            arr.append(ext_ids[ext_id][0])
        return arr

    # Read fields of view
    for field in res['models'][res['model']]:
        # Get Fields Instance
        field_inst = arch.xpath("//field[@name='%s']" % str(field))
        field_inst = field_inst[0] if field_inst else False
        # Scope Variables
        readonly_arr = []
        required_arr = []
        invisible_arr = []

        # Loop all nodes
        for node in workflow_rec.node_ids:
            # Loop Other Nodes
            for field_attrs in node.field_ids:
                # Record all states for each attribute
                if field_inst is not False and field_attrs.name.name == field_inst.attrib['name']:
                    flag_show = False
                    # Check Users & Groups
                    if field_attrs.user_ids:
                        user_rec = user_obj.browse(uid)
                        if user_rec in field_attrs.user_ids:
                            flag_show = True
                    if field_attrs.group_ids:
                        has_group = False
                        user_rec = user_obj.browse(uid)
                        ext_ids = _get_external_id(field_attrs.group_ids)
                        for ext_id in ext_ids:
                            has_group = user_rec.has_group(ext_id)
                            if has_group:                          
                                flag_show = True
                                        
                    if field_attrs.readonly and flag_show:
                        readonly_arr.append(str(node.id))
                    if field_attrs.required and flag_show:
                        required_arr.append(str(node.id))
                    if field_attrs.invisible and flag_show:
                        invisible_arr.append(str(node.id))

        # Construct XML attribute
        if readonly_arr != [] and field_inst is not False:
            field_inst.set('readonly', "x_workflow_vstate in " + str(readonly_arr))
        if required_arr != [] and field_inst is not False:
            field_inst.set('required', "x_workflow_vstate in " + str(required_arr))
        if invisible_arr != [] and field_inst is not False:
            field_inst.set('invisible', "x_workflow_vstate in " + str(invisible_arr))
    
    res['arch'] = etree.tostring(arch, encoding="utf-8")
    return res

@api.model
def new_fields_view_get(self, view_id=None, view_type='form', **options):
    '''<button   user_ids="1,2,3" '''
    res = old_fields_view_get(self, view_id=view_id, view_type=view_type, **options)
    if view_type == 'form' and res['models'][res['model']] and 'x_workflow_vstate' in res['models'][res['model']]:
        res = self.update_fields_view(view_id, res)
        view = etree.fromstring(res['arch'])
    
        for tag in view.xpath("//button[@user_ids]"):
            users_str = tag.get('user_ids')
            user_ids = [int(i) for i in users_str.split(',')]
            if self._uid not in user_ids and self._uid not in [SUPERUSER_ID,2]:
                tag.getparent().remove(tag)
        res['arch'] = etree.tostring(view)
    return res


BM.write = default_write_new
BM.create = default_create_new
BM.default_get = default_get_new
BM.workflow_button_action = workflow_button_action
BM.workflow_action = workflow_action
BM.workflow_button_show_log = workflow_button_show_log
BM.workflow_button_reset = workflow_button_reset
BM.workflow_button_stop = workflow_button_stop
VM.get_view = new_fields_view_get
BM.update_fields_view = update_fields_view
BM.workflow_button_link = workflow_button_link
BM.workflow_buttons_action = workflow_buttons_action
BM.workflow_trans_condition_expr_eval = workflow_trans_condition_expr_eval
######################################################################


##############################
