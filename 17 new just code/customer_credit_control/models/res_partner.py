# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_amount_credit_limit = fields.Boolean("Amount Credit Limit")
    credit_limit_amount = fields.Float("Credit Limit (Amount)")
    amount_tolerance = fields.Float("Tolerance (%)")
    warning_amount = fields.Float("Warning Amount")
    is_days_credit_limit = fields.Boolean("Days Credit Limit")
    credit_limit_days = fields.Integer("Credit Limit (Days)")
    days_tolerance = fields.Integer("Tolerance (Days)")
    warning_days = fields.Integer("Warning day")
    total_due_amount = fields.Float("Total Due Amount", compute="_get_total_due_amount", store=False)
    total_due_days = fields.Integer("Total Due Days", compute="_get_total_due_days", store=False)
    is_enable_warning = fields.Boolean("Enable Warnings")

    @api.constrains("credit_limit_amount", "credit_limit_days", "amount_tolerance", "days_tolerance", "warning_amount",
                    "warning_days")
    def amount_days_non_negative_check(self):
        """
        Checks all the Credit Control fields to make sure none has a Negative Value.
        :return: Raises Warning if any of the credit control field has a Negative value.
        """
        invalid_field = False
        if self.is_amount_credit_limit:
            if self.credit_limit_amount < 0:
                invalid_field = "Credit Limit (Amount)"
            if self.amount_tolerance < 0:
                invalid_field = "%s, Tolerance" % invalid_field
            if self.warning_amount < 0:
                invalid_field = "%s, Warning at" % invalid_field

        if self.is_days_credit_limit:
            if self.credit_limit_days < 0:
                invalid_field = "%s, Credit Limit (Days)" % invalid_field
            if self.days_tolerance < 0:
                invalid_field = "%s, Tolerance (Days)" % invalid_field
            if self.warning_days < 0:
                invalid_field = "%s, Warning day" % invalid_field

        if invalid_field:
            raise ValidationError(_("Value can not be Negative. Following field(s) has Negative Values : \n %s " % invalid_field))

    def _get_total_due_amount(self):
        """
        This method calculates total due amount of current partner and store in computed field
        :return:
        """
        invoice_obj = self.env["account.move"]
        for record in self:
            record.total_due_amount = 0
            invoice_ids = invoice_obj.search([
                ("partner_id", "=", record.id),
                ("amount_residual", ">", 0),
                ("state", "!=", "cancel")
            ])
            record.total_due_amount = sum(invoice_ids.mapped('amount_residual'))

    def _get_total_due_days(self):
        """
        This method calculates longest due amount days of current partner and store in computed field
        :return:
        """
        invoice_obj = self.env["account.move"]
        for record in self:
            record.total_due_days = 0

            due_invoice = invoice_obj.search([
                ("partner_id", "=", record.id),
                ("amount_residual", ">", 0),
            ], order="invoice_date", limit=1)

            child_due_invoice = invoice_obj.search([
                ("partner_id", "in", record.child_ids.ids),
                ("amount_residual", ">", 0),
            ], order="invoice_date", limit=1)

            if due_invoice.invoice_date_due and child_due_invoice.invoice_date_due:
                if child_due_invoice.invoice_date_due < due_invoice.invoice_date_due:
                    due_invoice = child_due_invoice

            first_due_date = due_invoice.invoice_date_due
            if first_due_date:
                diff_datetime = datetime.now().date() - first_due_date
                total_due_days = diff_datetime.days+1
                record.total_due_days = total_due_days
