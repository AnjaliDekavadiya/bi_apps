# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    sh_amount_residual = fields.Monetary(string='Amount Due',
        compute='_compute_amount',precompute=True ,store=True)

    def action_pos_order_paid(self):
        self.ensure_one()

        # TODO: add support for mix of cash and non-cash payments when both cash_rounding and only_round_cash_method are True
        if not self.config_id.cash_rounding \
           or self.config_id.only_round_cash_method \
           and not any(p.payment_method_id.is_cash_count for p in self.payment_ids):
            total = self.amount_total
        else:
            total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding, rounding_method=self.config_id.rounding_method.rounding_method)

        isPaid = float_is_zero(total - self.amount_paid, precision_rounding=self.currency_id.rounding)
        if self and self.state == 'on_hold':
            if not isPaid and not self.config_id.cash_rounding:
                raise UserError(_("Order %s is not fully paid.", self.name))
            elif not isPaid and self.config_id.cash_rounding:
                currency = self.currency_id
                if self.config_id.rounding_method.rounding_method == "HALF-UP":
                    maxDiff = currency.round(self.config_id.rounding_method.rounding / 2)
                else:
                    maxDiff = currency.round(self.config_id.rounding_method.rounding)
            
                diff = currency.round(self.amount_total - self.amount_paid)
                if not abs(diff) <= maxDiff:
                    raise UserError(_("Order %s is not fully paid.", self.name))
        self.write({'state': 'paid'})

        return True

    @api.depends('amount_paid','amount_total')
    def _compute_amount(self):
        for each in self:
            if each.amount_paid < each.amount_total:
                each.sh_amount_residual = each.amount_total-each.amount_paid
            else:
                each.sh_amount_residual = 0.00

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(
            order, draft, existing_order)
        if order_id:
            order_obj = self.env['pos.order'].search([('id','=',order_id)])
            if order_obj and order_obj.to_invoice and not order_obj.account_move:
                order_obj.action_pos_order_invoice()

        return order_id

    def _create_invoice(self, move_vals):
        if self.config_id.cash_rounding and not self._is_pos_order_paid():
            self.ensure_one()
            new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type=move_vals['move_type']).create(move_vals)
            message = _("This invoice has been created from the point of sale session: %s",
                self._get_html_link())

            new_move.message_post(body=message)
            return new_move
        return super()._create_invoice(move_vals)

    @api.model
    def create_from_ui(self, orders, draft=False):
        existing_return_order = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
                if existing_order:
                    existing_return_order.append({'id':existing_order.id,'pos_reference':existing_order.pos_reference,'account_move':existing_order.account_move.id})
                    pos_session = self.env['pos.session'].browse(order['data']['pos_session_id'])
                    old_payment_line = []
                    if existing_order.payment_ids :
                        for each_payment_line in existing_order.payment_ids:
                            old_payment_line.append([0, 0, {'name': each_payment_line.payment_date, 'payment_method_id': each_payment_line.payment_method_id.id, 'amount': each_payment_line.amount, 'payment_status': each_payment_line.payment_status, 'ticket': each_payment_line.ticket, 'card_type': each_payment_line.card_type, 'cardholder_name': each_payment_line.cardholder_name, 'transaction_id': each_payment_line.transaction_id}])
                    self._process_payment_lines(order['data'], existing_order, pos_session, draft)

                    if existing_order and existing_order.to_invoice:
                        existing_order._apply_invoice_payments()

                    if old_payment_line and len(old_payment_line) > 0:
                            for each_old_payment_line in old_payment_line:
                                order['data']['statement_ids'].append(each_old_payment_line)
                    
                    self._process_payment_lines(order['data'], existing_order, pos_session, draft)
                    existing_order.action_pos_order_paid()
                    if existing_order and existing_order.to_invoice:
                        existing_order.write({'state':'invoiced'})
                    # if existing_return_order and len(existing_return_order) > 0:
                    #     for each_existing_return_order in existing_return_order:
                    #         order_id.append(each_existing_return_order)

                    order_id = [{'id': existing_order.id, 'pos_reference': order['data']['name'], 'account_move': existing_order.account_move.id}]
                    return order_id
                
                else:
                  order_id = super(PosOrder, self).create_from_ui(orders, draft=False)
                return order_id

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.

        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.currency_id.decimal_places

        order._clean_payment_lines()
        for payments in pos_order['statement_ids']:
            order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))
        # add condition "not order.to_invoice" for partial refund amounts
        if not draft and not order.to_invoice and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Datetime.now(),
                'payment_method_id': cash_payment_method.id,
                'is_change': True,
            }
            order.add_payment(return_payment_vals)

    def _apply_invoice_payments(self):
        receivable_account = self.env["res.partner"]._find_accounting_partner(self.partner_id).with_company(self.company_id).property_account_receivable_id
        payment_moves = self.payment_ids.sudo().with_company(self.company_id)._create_payment_moves()
        if receivable_account.reconcile:
            if self.refunded_order_ids:
                invoice_receivables = (self.account_move.line_ids | self.refunded_order_ids.mapped('account_move.line_ids')).filtered(lambda line: line.account_id == receivable_account and not line.reconciled)
            else:
                invoice_receivables = self.account_move.line_ids.filtered(lambda line: line.account_id == receivable_account and not line.reconciled)
            if invoice_receivables:
                payment_receivables = payment_moves.mapped('line_ids').filtered(lambda line: line.account_id == receivable_account and line.partner_id)
                (invoice_receivables | payment_receivables).sudo().with_company(self.company_id).reconcile()
        return payment_moves
