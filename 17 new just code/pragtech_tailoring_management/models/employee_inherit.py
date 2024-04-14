from odoo import models, fields,api
from odoo.exceptions import ValidationError
import re



class MyEmployee(models.Model):
    _inherit = 'hr.employee'

    jobdata = fields.Many2one('tailoring.job',string='Job Positions')
    password = fields.Char('Password')
    done = fields.Boolean('Done')

    # Creating users from employee menu...................................................................................
    def create_user_from_employee(self):
        for employee in self:
            user = self.env['res.users']
            if employee.job_title == 'Driver':
                driver_login_group = [
                    self.env.ref('sales_team.group_sale_salesman_all_leads').id,
                    self.env.ref('base.group_user').id,
                    self.env.ref('stock.group_stock_user').id,
                    self.env.ref('pragtech_tailoring_management.group_driver').id,]
                user = user.create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'email': employee.work_email,
                    'password': employee.password,
                    'groups_id': [(6,0,driver_login_group)],

                })
                user.partner_id.function = 'Driver'

            elif employee.job_title == 'Tailor':
                tailor_login_group = [
                    self.env.ref('sales_team.group_sale_salesman').id,
                    self.env.ref('base.group_user').id,
                    self.env.ref('pragtech_tailoring_management.group_tailor').id,]
                user = user.create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'email': employee.work_email,
                    'password': employee.password,
                    'groups_id': [(6,0,tailor_login_group)]

                })
                user.partner_id.function = 'Tailor'
            elif employee.job_title == 'Admin':
                admin_login_group = [
                    self.env.ref('sales_team.group_sale_salesman').id,
                    self.env.ref('base.group_user').id,
                    self.env.ref('hr.group_hr_manager').id,
                    self.env.ref('purchase.group_purchase_manager').id,
                    self.env.ref('pragtech_tailoring_management.group_admin').id,]
                user = user.create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'email': employee.work_email,
                    'password': employee.password,
                    'groups_id': [(6,0,admin_login_group)]
                })
                user.partner_id.function = 'Admin'
                
            employee.done = True
            return user
        
    # Email and Password validation.............................................................................
    @api.constrains('work_email', 'password')
    def _check_valid_email_password(self):
        for employee in self:
            if employee.work_email and not self._is_valid_email(employee.work_email):
                raise ValidationError("Invalid email address. Please provide a valid email address. ⚠️")

            if employee.password and not self._is_valid_password(employee.password):
                raise ValidationError("Invalid password. Password must be at least 8 characters and contain at least one digit, one letter, and one special character. ⚠️")

    def _is_valid_email(self, email):
        import re
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        return False

    def _is_valid_password(self, password):
        # Password validation criteria: Must contain at least one digit, one letter, and one special character, and be at least 8 characters long
        if re.match(r"^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$%^&*()_+[\]{}|;:'\",.<>?]).{8,}$", password):
            return True
        return False

