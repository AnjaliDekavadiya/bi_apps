# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warning_mail_ids = fields.One2many("warning.mail", "sale_order_id", "Warning Mails",
                                       help="Warning Mails.")

    def action_confirm(self):
        """
        This is extended process of base method action_confirm of sale.order model.
        Here we are checking before confirming if customer has crossed credit limit or will cross credit limit after
        confirmation of this sale order?
        If yes : we raise warning saying this sale order can not be confirmed because dues have crossed credit limit.
        If no : then confirm sale order and proceeds normally.
        :return:
        """
        user_obj = self.env["res.users"]
        config_parameter_obj = self.env['ir.config_parameter']
        universal_credit_control = config_parameter_obj.get_param('enable_universal_credit_control', False)
        force_universal_credit_control = config_parameter_obj.get_param('force_universal_credit_control', False)

        credit_partner = self.partner_id
        if self.partner_id.parent_id:
            credit_partner = self.partner_id.parent_id

        if universal_credit_control:
            if (not credit_partner.is_amount_credit_limit and not credit_partner.is_days_credit_limit and not
            credit_partner.is_enable_warning or force_universal_credit_control):
                is_amount_credit_limit = bool(config_parameter_obj.get_param('cc_is_amount_credit_limit', False))
                credit_limit_amount = float(config_parameter_obj.get_param('cc_credit_limit_amount', 0))
                amount_tolerance = float(config_parameter_obj.get_param('cc_amount_tolerance', 0))
                warning_amount = float(config_parameter_obj.get_param('cc_warning_amount', 0)) if (
                    config_parameter_obj.get_param('cc_is_amount_credit_limit', False)) else 0
                is_days_credit_limit = bool(config_parameter_obj.get_param('cc_is_days_credit_limit', False))
                credit_limit_days = int(config_parameter_obj.get_param('cc_credit_limit_days', 0))
                days_tolerance = int(config_parameter_obj.get_param('cc_days_tolerance', 0))
                warning_days = int(config_parameter_obj.get_param('cc_warning_days', 0) if
                        config_parameter_obj.get_param('cc_is_days_credit_limit', False) else 0)
                enable_warning = bool(config_parameter_obj.get_param('cc_enable_warning', False)) if (
                        config_parameter_obj.get_param('cc_is_amount_credit_limit', False) or
                        config_parameter_obj.get_param('cc_is_days_credit_limit', False)) else False
            else:
                is_amount_credit_limit = credit_partner. is_amount_credit_limit
                credit_limit_amount = credit_partner.credit_limit_amount
                amount_tolerance = credit_partner.amount_tolerance
                warning_amount = credit_partner.warning_amount if credit_partner.is_amount_credit_limit == True else 0
                is_days_credit_limit = credit_partner.is_days_credit_limit
                credit_limit_days = credit_partner.credit_limit_days
                days_tolerance = credit_partner.days_tolerance
                warning_days = credit_partner.warning_days if credit_partner.is_days_credit_limit == True else 0
                enable_warning = credit_partner.is_enable_warning if (credit_partner.is_amount_credit_limit == True or
                                                                      credit_partner.is_days_credit_limit == True) else False
        else:
            is_amount_credit_limit = credit_partner.is_amount_credit_limit
            credit_limit_amount = credit_partner.credit_limit_amount
            amount_tolerance = credit_partner.amount_tolerance
            warning_amount = credit_partner.warning_amount if credit_partner.is_amount_credit_limit == True else 0
            is_days_credit_limit = credit_partner.is_days_credit_limit
            credit_limit_days = credit_partner.credit_limit_days
            days_tolerance = credit_partner.days_tolerance
            warning_days = credit_partner.warning_days if credit_partner.is_days_credit_limit == True else 0
            enable_warning = credit_partner.is_enable_warning if (credit_partner.is_amount_credit_limit == True or
                                                                  credit_partner.is_days_credit_limit == True) else False

        if is_amount_credit_limit:
            tolerance_amount = credit_limit_amount * amount_tolerance / 100
            actual_credit_limit = credit_limit_amount + tolerance_amount
            current_amount = self.amount_total + credit_partner.total_due_amount
            if current_amount > actual_credit_limit:
                raise ValidationError(
                    _("Customer Credit Limit Reached, You can not confirm sale orders of this customer unless "
                      "previous dues are cleared."))

        if is_days_credit_limit:
            actual_days_credit_limit = credit_limit_days + days_tolerance
            if credit_partner.total_due_days > actual_days_credit_limit:
                raise ValidationError(
                    _("Customer Credit Limit has reached, You can not confirm sale orders of this customer unless "
                      "past dues are cleared."))

        if enable_warning:
            current_amount = self.amount_total + credit_partner.total_due_amount
            if is_amount_credit_limit and current_amount > warning_amount:
                mail_user_id = config_parameter_obj.get_param('cc_email_from', self.user_id)
                mail_user = user_obj.browse(int(mail_user_id))
                subject = "Credit Limit Amount Warning"
                email_body = """
                Dear %s,
                <br/><br/>
                This is a warning email to inform you that you are close to your credit limit and can cross 
                anytime.<br/>
                Your allowed credit limit is : %s %s and you have currently outstanding bill : %s %s.<br/>
                Kindly pay your due bills to continue purchasing.<br/>
                <br/><br/>
                Regards,<br/>
                %s<br/>
                %s
                
                """ % (credit_partner.name, credit_limit_amount, credit_partner.currency_id.symbol,
                       current_amount, credit_partner.currency_id.symbol,
                       mail_user.name, mail_user.company_id.name)

                self.create_warning_mail(mail_user, self.partner_id, subject, email_body)

            if is_days_credit_limit and credit_partner.total_due_days > warning_days:
                mail_user_id = config_parameter_obj.get_param('cc_email_from', self.user_id)
                mail_user = user_obj.browse(int(mail_user_id))
                subject = "Credit Limit Days Warning"
                email_body = """
                                Dear %s,<br/><br/>
                                This is a warning email to inform you that you are close to your credit limit 
                                and can cross anytime.<br/>
                                Your allowed credit limit is : %s days and your current outstanding amount is 
                                from %s days agp.<br/><br/>
                                Kindly pay your old due bills which will be older than %s days soon, to continue 
                                purchasing.<br/><br/>

                                Regards,<br/>
                                %s<br/>
                                %s

                                """ % (credit_partner.name, credit_limit_days, credit_partner.total_due_days,
                                               credit_limit_days, mail_user.name, mail_user.company_id.name)

                self.create_warning_mail(mail_user, self.partner_id, subject, email_body)

        return super().action_confirm()


    def create_warning_mail(self, email_from, partner_to, subject, email_body):
        """
        This method creates a warning record from given parameters and current sale order.
        :param email_from: This is a res.users object
        :param partner_to: This is a res.partner object
        :param subject: This is a one line string.
        :param email_body:this is a large text
        :return: Returns created new warning mail record object
        """
        warning_mail_obj = self.env["warning.mail"]
        email_values = {
            'mail_user': email_from.id,
            'partner_id': partner_to.id,
            'mail_subject': subject,
            'mail_body': email_body,
            'sale_order_id': self.id,
            'is_send_warning_mail': True,
            'is_warning_mail_sent': False
        }
        if partner_to.parent_id:
            email_values.update({
                "partner_ids": [(4, partner_to.parent_id.id)]
            })
        return warning_mail_obj.create(email_values)
