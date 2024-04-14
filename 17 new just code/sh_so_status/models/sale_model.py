# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sh_fully_delivered = fields.Boolean(
        string="Delivered", default=False, copy=False, compute="_compute_check_delivery", store=True, compute_sudo=True)
    sh_partially_delivered = fields.Boolean(
        string="Partially Delivered", default=False, copy=False, compute="_compute_check_delivery", store=True, compute_sudo=True)
    sh_fully_paid = fields.Boolean(string="Paid", default=False, copy=False,
                                   compute="_compute_check_delivery", search="_search_fully_paid", compute_sudo=True)
    sh_partially_paid = fields.Boolean(string="Partially Paid",  default=False, copy=False,
                                       compute="_compute_check_delivery", search="_search_partial_paid", compute_sudo=True)
    sh_hidden_compute_field = fields.Boolean(
        string="Hidden Compute", readonly=True, compute="_compute_check_delivery", compute_sudo=True)

    def _search_partial_paid(self, operator, value):
        paid_ids = []
        unpaid_ids = []
        for so_rec in self.search([]):
            if so_rec.invoice_ids:
                sum_of_invoice_amount = 0.0
                sum_of_due_amount = 0.0
                for invoice_id in so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                    sum_of_invoice_amount = sum_of_invoice_amount + invoice_id.amount_total_signed
                    sum_of_due_amount = sum_of_due_amount + invoice_id.amount_residual_signed
                    if invoice_id.amount_residual_signed != 0 and invoice_id.amount_residual_signed < invoice_id.amount_total_signed:
                        if so_rec.id not in paid_ids:
                            paid_ids.append(so_rec.id)
                    # down payment
                    if invoice_id.amount_residual_signed == 0 and invoice_id.amount_total_signed < so_rec.amount_total:
                        if so_rec.id not in paid_ids:
                            paid_ids.append(so_rec.id)

                # down payment
                if sum_of_due_amount == 0 and sum_of_invoice_amount < so_rec.amount_total:
                    if so_rec.id not in paid_ids:
                        paid_ids.append(so_rec.id)

                if sum_of_due_amount == 0 and sum_of_invoice_amount >= so_rec.amount_total:
                    if so_rec.id in paid_ids:
                        paid_ids.remove(so_rec.id)

        for so_rec in self.search([('id', 'not in', paid_ids)]):
            unpaid_ids.append(so_rec.id)
        if operator == '=':
            return [('id', 'in', paid_ids)]
        elif operator == '!=':
            return [('id', 'in', unpaid_ids)]
        else:
            return []

    def _search_fully_paid(self, operator, value):
        paid_ids = []
        unpaid_ids = []
        for so_rec in self.search([]):
            if so_rec.invoice_ids:
                sum_of_invoice_amount = 0.0
                sum_of_due_amount = 0.0
                for invoice_id in so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                    sum_of_invoice_amount = sum_of_invoice_amount + invoice_id.amount_total_signed
                    sum_of_due_amount = sum_of_due_amount + invoice_id.amount_residual_signed

                    if sum_of_due_amount == 0 and sum_of_invoice_amount >= so_rec.amount_total:
                        paid_ids.append(so_rec.id)
                    else:
                        unpaid_ids.append(so_rec.id)

            else:
                unpaid_ids.append(so_rec.id)
        if operator == '=':
            return [('id', 'in', paid_ids)]
        elif operator == '!=':
            return [('id', 'in', unpaid_ids)]
        else:
            return []

    @api.depends('order_line.qty_delivered')
    def _compute_check_delivery(self):
        if self:
            for so_rec in self:
                so_rec.sh_partially_delivered = False
                so_rec.sh_fully_delivered = False
                so_rec.sh_partially_paid = False
                so_rec.sh_fully_paid = False
                so_rec.sh_hidden_compute_field = False
                if so_rec.order_line and type(so_rec.id) == int:
                    no_service_product_line = so_rec.order_line.filtered(
                        lambda line: (line.product_id) and (line.product_id.type != 'service'))
                    if no_service_product_line:
                        so_rec.sh_partially_delivered = False
                        so_rec.sh_fully_delivered = False
                        product_uom_qty = qty_delivered = 0
                        for line in no_service_product_line:
                            qty_delivered += line.qty_delivered
                            product_uom_qty += line.product_uom_qty
                        if product_uom_qty == qty_delivered:
                            so_rec.sh_fully_delivered = True
                        elif product_uom_qty > qty_delivered and qty_delivered != 0.0:
                            so_rec.sh_partially_delivered = True
                if so_rec.invoice_ids:
                    sum_of_invoice_amount = 0.0
                    sum_of_due_amount = 0.0
                    sum_of_credit_note_amount = 0.0
                    sum_of_credit_not_due_amount = 0.0
                    so_rec.sh_fully_paid = False
                    so_rec.sh_partially_paid = False
                    for invoice_id in so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft'] and inv.move_type == 'out_invoice'):
                        sum_of_invoice_amount = sum_of_invoice_amount + invoice_id.amount_total_signed
                        sum_of_due_amount = sum_of_due_amount + invoice_id.amount_residual_signed
                        if invoice_id.amount_residual_signed != 0 and invoice_id.amount_residual_signed < invoice_id.amount_total_signed:

                            so_rec.sh_partially_paid = True

                        # down payment
                        if invoice_id.amount_residual_signed == 0 and invoice_id.amount_total_signed < so_rec.amount_total:
                            so_rec.sh_partially_paid = True

                    if sum_of_due_amount == 0 and sum_of_invoice_amount >= so_rec.amount_total:
                        so_rec.sh_fully_paid = True
                        so_rec.sh_partially_paid = False
                    # down payment
                    if sum_of_due_amount == 0 and sum_of_invoice_amount < so_rec.amount_total and so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                        so_rec.sh_partially_paid = True

                    # if there is credit note
                    if so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft'] and inv.move_type == 'out_refund'):

                        for invoice_id in so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft'] and inv.move_type == 'out_refund'):
                            sum_of_credit_note_amount = sum_of_credit_note_amount + \
                                invoice_id.amount_total_signed
                            sum_of_credit_not_due_amount = sum_of_credit_not_due_amount + \
                                invoice_id.amount_residual_signed
                        invoice_payment = sum_of_invoice_amount - sum_of_due_amount
                        credit_note_payment = abs(
                            sum_of_credit_note_amount) - abs(sum_of_credit_not_due_amount)

                        if invoice_payment == credit_note_payment:
                            so_rec.sh_fully_paid = False
                            so_rec.sh_partially_paid = False

                        elif (invoice_payment - credit_note_payment) > 0 and (invoice_payment - credit_note_payment) == so_rec.amount_total:
                            so_rec.sh_fully_paid = True
                            so_rec.sh_partially_paid = False

                        elif (invoice_payment - credit_note_payment) > 0:
                            so_rec.sh_fully_paid = False
                            so_rec.sh_partially_paid = True
