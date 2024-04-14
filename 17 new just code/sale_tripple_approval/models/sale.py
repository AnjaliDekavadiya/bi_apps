# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('state')
    def _custom_set_sale_user(self):
        for rec in self:
            if rec.state == 'draft' or 'sent':
                rec.custom_sale_user_id = self.env.user.id,

    @api.model
    def _get_so_finance_validation_amount(self):
#         finance_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'finance_validation_amount')
        # so_finance_validation_amount = self.env.user.company_id.so_finance_validation_amount
        so_finance_validation_amount = self.env.company.so_finance_validation_amount
        return so_finance_validation_amount

    @api.model
    def _get_so_director_validation_amount(self):
#         director_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'director_validation_amount')
        # so_director_validation_amount = self.env.user.company_id.so_director_validation_amount
        so_director_validation_amount = self.env.company.so_director_validation_amount
        return so_director_validation_amount

    @api.model
    def _get_so_three_step_validation(self):
#         three_step_validation = self.env['ir.values'].get_default('purchase.config.settings', 'three_step_validation')
        # so_three_step_validation = self.env.user.company_id.so_three_step_validation
        so_three_step_validation = self.env.company.so_three_step_validation
        return so_three_step_validation

    @api.model
    def _get_so_email_template_id(self):
#         email_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'email_template_id')
        #so_email_template_id = self.env.user.company_id.so_email_template_id
        so_email_template_id = False
        so_email_template_id = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_email_template_id', 'False')
        so_email_template_id = self.env['mail.template'].search([('id', '=', int(so_email_template_id))])
        return so_email_template_id

    @api.model
    def _get_so_refuse_template_id(self):
#         refuse_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'refuse_template_id')
        # so_refuse_template_id = self.env.user.company_id.so_refuse_template_id
        so_refuse_template_id = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_refuse_template_id', 'False')
        so_refuse_template_id = self.env['mail.template'].search([('id', '=', int(so_refuse_template_id))])
        return so_refuse_template_id

    state = fields.Selection(selection_add=[
        ('to approve', 'To Approve'),
        ('finance_approval', 'Waiting Finance Approval'),
        ('director_approval', 'Waiting Director Approval'),
        ('refuse', 'Refuse')],
        string='Status',
    )
    so_refuse_user_id = fields.Many2one(
        'res.users',
        string="Refused By",
        readonly = True,
    )
    so_refuse_date = fields.Date(
        string="Refused Date",
        readonly=True
    )
    refuse_reason_note = fields.Text(
        string="Refuse Reason",
        readonly=True
    )
    dept_manager_id = fields.Many2one(
        'res.users',
        string='Sale/Department Manager',
        # states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    finance_manager_id = fields.Many2one(
        'res.users',
        string='Finance Manager',
        # states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    director_manager_id = fields.Many2one(
        'res.users',
        string='Director Manager',
        # states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    approve_dept_manager_id = fields.Many2one(
        'res.users',
        string='Approve Department Manager',
        readonly=True,
    )
    approve_finance_manager_id = fields.Many2one(
        'res.users',
        string='Approve Finance Manager',
        readonly=True,
    )
    approve_director_manager_id = fields.Many2one(
        'res.users',
        string='Approve Director Manager',
        readonly=True,
    )
    dept_manager_approve_date = fields.Datetime(
        string='Department Manager Approve Date',
        readonly=True,
    )
    finance_manager_approve_date = fields.Datetime(
        string='Finance Manager Approve Date',
        readonly=True,
    )
    director_manager_approve_date = fields.Datetime(
        string='Director Manager Approve Date',
        readonly=True,
    )
    custom_sale_user_id = fields.Many2one(
        'res.users',
        string='Sale User',
        compute='_custom_set_sale_user',
        store=True,
    )


#    @api.multi odoo13
# will getting updated order state instead of current state. so, this code move in write method.
#    def _write(self, vals):
#        for order in self:
#            print(":::::::::::::::::::order.state):::::::::vals:", vals, order.state)
#            amount_total = order.currency_id.compute(order.amount_total, order.company_id.currency_id)
#            so_finance_validation_amount = self._get_so_finance_validation_amount()
#            so_double_validation_amount = self.env.user.company_id.currency_id.compute(order.company_id.so_double_validation_amount, order.currency_id)
#            if vals.get('state') == 'to approve':
#                if not order.dept_manager_id:
#                    raise UserError(_('Please select Sales/Department Manager.'))
#                else:
#                    email_to = order.dept_manager_id.email
#                    so_email_template_id = self._get_so_email_template_id()
#                    ctx = self._context.copy()
#                    ctx.update({'name': order.dept_manager_id.name})
#                    #reminder_mail_template.with_context(ctx).send_mail(user)
#                    if so_email_template_id:
#                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})

#            if vals.get('state') == 'finance_approval':
#                if not order.finance_manager_id:
#                    raise UserError(_('Please select Finance Manager.'))
#                else:
#                    email_to = order.finance_manager_id.email
#                    so_email_template_id = self._get_so_email_template_id()
##                     mail = self.env['mail.template'].browse(email_template_id)
#                    ctx = self._context.copy()
#                    ctx.update({'name': order.finance_manager_id.name})
#                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Finance Manager Approve"})
#                    if so_email_template_id:
#                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})

#            if vals.get('state') == 'director_approval':
#                if not order.director_manager_id:
#                    raise UserError(_('Please select Director Manager.'))
#                else:
#                    email_to = order.director_manager_id.email
#                    so_email_template_id = self._get_so_email_template_id()
##                     mail = self.env['mail.template'].browse(email_template_id)
#                    ctx = self._context.copy()
#                    ctx.update({'name': order.director_manager_id.name})
#                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
#                    if so_email_template_id:
#                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})
#            print(":::::::::::::::::::::::;", order.state, vals.get('state'))
#            if order.state == 'to approve' and vals.get('state') == 'sale':
#                print(":::::::::::::::::::1::::::", )
#                order.approve_dept_manager_id = self.env.user.id
#                order.dept_manager_approve_date = fields.Datetime.now()
#            elif order.state == 'to approve' and vals.get('state') == 'finance_approval':
#                print(":::::::::::::::::::2::::::", )
#                order.approve_dept_manager_id = self.env.user.id
#                order.dept_manager_approve_date = fields.Datetime.now()

#            if order.state == 'finance_approval' and vals.get('state') == 'sale':
#                print(":::::::::::::::::::3::::::", )
#                order.approve_finance_manager_id = self.env.user.id
#                order.finance_manager_approve_date = fields.Datetime.now()
#            elif order.state == 'finance_approval' and vals.get('state') == 'director_approval':
#                print(":::::::::::::::::::4::::::", )
#                order.approve_finance_manager_id = self.env.user.id
#                order.finance_manager_approve_date = fields.Datetime.now()

#            if order.state == 'director_approval' and vals.get('state') == 'sale':
#                print(":::::::::::::::::::5::::::", )
#                order.approve_director_manager_id = self.env.user.id
#                order.director_manager_approve_date = fields.Datetime.now()
#        return super(SaleOrder, self)._write(vals)
        
    def write(self, vals):
        for order in self:
#            amount_total = order.currency_id.compute(order.amount_total, order.company_id.currency_id)
            amount_total = order.currency_id._convert(order.amount_total, order.company_id.currency_id, self.env.user.company_id, order.date_order)
            so_finance_validation_amount = self._get_so_finance_validation_amount()
            # so_double_validation_amount = self.env.user.company_id.currency_id.compute(order.company_id.so_double_validation_amount, order.currency_id)
#            so_double_validation_amount = self.env.company.currency_id.compute(order.company_id.so_double_validation_amount, order.currency_id)
            so_double_validation_amount = self.env.company.currency_id._convert(order.company_id.so_double_validation_amount, order.currency_id, self.env.user.company_id, order.date_order)

            if vals.get('state') == 'to approve':
                if not order.dept_manager_id:
                    raise UserError(_('Please select Sales/Department Manager.'))
                else:
                    email_to = order.dept_manager_id.email
                    so_email_template_id = self._get_so_email_template_id()
                    ctx = self._context.copy()
                    ctx.update({'name': order.dept_manager_id.name})
                    #reminder_mail_template.with_context(ctx).send_mail(user)
                    if so_email_template_id:
                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})


            if vals.get('state') == 'finance_approval':
                if not order.finance_manager_id:
                    raise UserError(_('Please select Finance Manager.'))
                else:
                    email_to = order.finance_manager_id.email
                    so_email_template_id = self._get_so_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.finance_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Finance Manager Approve"})
                    if so_email_template_id:
                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})

            
            if vals.get('state') == 'director_approval':
                if not order.director_manager_id:
                    raise UserError(_('Please select Director Manager.'))
                else:
                    email_to = order.director_manager_id.email
                    so_email_template_id = self._get_so_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                    ctx = self._context.copy()
                    ctx.update({'name': order.director_manager_id.name})
                    #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                    if so_email_template_id:
                        so_email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Sale Order: ') + order.name + _(' (Approval Waiting)')})
                        
                        
            if order.state == 'to approve' and vals.get('state') == 'sale':
                vals.update({
                    'approve_dept_manager_id' : self.env.user.id,
                    'dept_manager_approve_date' : fields.Datetime.now(),
                })
                
            elif order.state == 'to approve' and vals.get('state') == 'finance_approval':
                vals.update({
                    'approve_dept_manager_id' : self.env.user.id,
                    'dept_manager_approve_date' : fields.Datetime.now(),
                })
                
            if order.state == 'finance_approval' and vals.get('state') == 'sale':
                vals.update({
                    'approve_finance_manager_id' : self.env.user.id,
                    'finance_manager_approve_date' : fields.Datetime.now(),
                })
                
            elif order.state == 'finance_approval' and vals.get('state') == 'director_approval':
                vals.update({
                    'approve_finance_manager_id' : self.env.user.id,
                    'finance_manager_approve_date' : fields.Datetime.now(),
                })
                
            if order.state == 'director_approval' and vals.get('state') == 'sale':
                vals.update({
                    'approve_director_manager_id' : self.env.user.id,
                    'director_manager_approve_date' : fields.Datetime.now(),
                })
                
        return super(SaleOrder, self).write(vals)


#    @api.multi odoo13
    def button_finance_approval(self):
        so_finance_validation_amount = self._get_so_finance_validation_amount()
        so_director_validation_amount = self._get_so_director_validation_amount()
#        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        amount_total = self.currency_id._convert(self.amount_total, self.company_id.currency_id, self.env.user.company_id, self.date_order)
        for order in self:
            if amount_total > so_director_validation_amount:
                order.write({'state': 'director_approval'})
            if amount_total < so_director_validation_amount:
                order.button_director_approval()
        return True

#    @api.multi odoo13
    def button_director_approval(self):
        for order in self:
#            order.with_context(call_super=True)._action_confirm()
            order.with_context(call_super=True).action_confirm()
        return True

#    @api.multi odoo13
    def button_approve(self, force=False):
#        return self._action_confirm() odoo12
        return self.action_confirm()

#    @api.multi odoo13
    def action_confirm(self):
        if self._context.get('call_super', False):
            return super(SaleOrder, self).action_confirm()
        for order in self:
#            if order.state not in ['draft', 'sent']:
#                continue
            # Deal with double validation process
            if order.company_id.so_double_validation == 'one_step'\
                    or (order.company_id.so_double_validation == 'two_step'\
#                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.so_double_validation_amount, order.currency_id))\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(order.company_id.so_double_validation_amount, order.currency_id, self.env.user.company_id, order.date_order))\
                    or order.user_has_groups('sales_team.group_sale_manager'):
                #odoo12
                so_three_step_validation = self._get_so_three_step_validation()
                if not so_three_step_validation:
                    return super(SaleOrder, self).action_confirm() 

#                amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
#                amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
                amount_total = self.currency_id._convert(self.amount_total, self.company_id.currency_id, self.env.user.company_id, order.date_order)
                # so_double_validation_amount = self.env.user.company_id.currency_id.compute(self.company_id.so_double_validation_amount, self.currency_id)
#                so_double_validation_amount = self.env.company.currency_id.compute(self.company_id.so_double_validation_amount, self.currency_id)
                so_double_validation_amount = self.env.company.currency_id._convert(self.company_id.so_double_validation_amount, self.currency_id, self.env.user.company_id, order.date_order)
                so_finance_validation_amount = self._get_so_finance_validation_amount()
                so_director_validation_amount = self._get_so_director_validation_amount()
                
        #         if finance_validation_amount > amount_total:
        #             return super(PurchaseOrder, self).button_approve() 

                if so_three_step_validation and not self._context.get('call_super', False):
                     for order in self:
                        if amount_total > so_double_validation_amount and order.state != 'to approve':
                            order.write({'state': 'to approve'})
                        elif amount_total < so_finance_validation_amount and order.state == 'to approve':
                            return super(SaleOrder, self).action_confirm()
                        elif order.state == 'to approve':
                            order.state = 'finance_approval'
                        else:
                            return super(SaleOrder, self).action_confirm()
                return True
#                order._action_confirm()
            else:
                order.write({'state': 'to approve'})
        return True
    
#    @api.multi odoo13
    def button_reset_to_draft(self):
        for order in self:
            if order.state in ['refuse']:
#                order._action_confirm() #odoo12
                order.action_confirm()
                #order.write({'state': 'draft'})
    
#    @api.multi
#    def _action_confirm(self, force=False):
#        if self._context.get('call_super', False):
#            return super(SaleOrder, self)._action_confirm()
#        so_three_step_validation = self._get_so_three_step_validation()

#        if not so_three_step_validation:
#            return super(SaleOrder, self)._action_confirm() 

#        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
#        so_double_validation_amount = self.env.user.company_id.currency_id.compute(self.company_id.so_double_validation_amount, self.currency_id)
#        so_finance_validation_amount = self._get_so_finance_validation_amount()
#        so_director_validation_amount = self._get_so_director_validation_amount()
##         if finance_validation_amount > amount_total:
##             return super(PurchaseOrder, self).button_approve() 

#        if so_three_step_validation and not self._context.get('call_super', False):
#             for order in self:
#                if amount_total > so_double_validation_amount and order.state != 'to approve':
#                    order.write({'state': 'to approve'})
#                elif amount_total < so_finance_validation_amount and order.state == 'to approve':
#                    return super(SaleOrder, self)._action_confirm()
#                elif order.state == 'to approve':
#                    order.state = 'finance_approval'
#                else:
#                    return super(SaleOrder, self)._action_confirm()
#        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
