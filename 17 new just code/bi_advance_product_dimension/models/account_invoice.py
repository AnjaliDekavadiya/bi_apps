# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import psycopg2
import itertools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

class AccountInvoice(models.Model):
    _inherit = "account.move"

    dimension_method = fields.Selection([('l_w_h', 'LenghtxWidthxHeight'), ('w_h', 'WidthxHeight')], 'Dimention Method')

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                if base_line.company_id.price_calculation == 'dimension':
                    quantity = base_line.quantity * base_line.m2
                    quantity = base_line.quantity * base_line.tot_qty
                else:
                    quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            return base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            # Don't create tax lines with zero balance.
            if currency.is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            balance = currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))
    
    def _calculate_dimesion_m2(self):
        res=0.0
        total=0.0
        for self_obj in self:
            for line in self.invoice_line_ids:
                if line.company_id.price_calculation == 'dimension':
                    quantity = line.quantity * line.m2
                    quantity =  line.tot_qty * quantity
                    price_unit_wo_discount = line.price_unit * (1 - (line.discount / 100.0))
                    line.price_subtotal = quantity * price_unit_wo_discount
                    total += line.price_subtotal
                    res = total
        return res
    
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _compute_tax_totals(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
                if move.id:
                    # The invoice is stored so we can add the early payment discount lines directly to reduce the
                    # tax amount without touching the untaxed amount.
                    sign = -1 if move.is_inbound(include_receipts=True) else 1
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,
                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.currency_id or move.journal_id.currency_id or move.journal_id.company_id.currency_id,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    # In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
                    # we need to simulate them.
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.currency_id,
                            taxes=taxes,
                            price_unit=values['price_subtotal'],
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'],
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))
                tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
                rounding_line = move.line_ids.filtered(lambda l: l.display_type == 'rounding')
                if rounding_line:
                    amount_total_rounded = tax_totals['amount_total'] - rounding_line.balance
                    tax_totals['formatted_amount_total_rounded'] = formatLang(self.env, amount_total_rounded, currency_obj=move.currency_id) or ''
                
                res = self._calculate_dimesion_m2()
                if  self.env.user.company_id.price_calculation == 'dimension':
                    if tax_totals.get('amount_untaxed'):
                        tax_totals['amount_untaxed'] = res
                    if tax_totals.get('formatted_amount_total'):
                        format_tax_total = tax_totals['amount_untaxed'] + move.amount_tax
                        tax_totals['formatted_amount_total'] = formatLang(self.env, format_tax_total, currency_obj=self.currency_id)
                    if tax_totals.get('formatted_amount_untaxed'):
                        format_total = tax_totals['amount_untaxed']
                        tax_totals['formatted_amount_untaxed'] = formatLang(self.env, format_total, currency_obj=self.currency_id)

                    groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
                    if bool(groups_by_subtotal):
                        _untax_amount = groups_by_subtotal.get('Untaxed Amount', [])
                        if bool(_untax_amount):
                            for _tax in range(len(_untax_amount)):
                                if _untax_amount[_tax].get('tax_group_base_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_base_amount' : res
                                    })
                                if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                    format_total = res
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                    })

                    subtotals = tax_totals.get('subtotals', {})
                    if bool(subtotals):
                        for _tax in range(len(subtotals)):
                            if subtotals[_tax].get('amount'):
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'amount' :res
                                })
                            if subtotals[_tax].get('formatted_amount'):
                                format_total = subtotals[_tax]['amount']
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                })
                move.tax_totals = tax_totals
            else:
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals = None

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.depends('pro_width','pro_height','pro_length',)
    def get_tot_qty(self):
        for record in self:
            if not (record.pro_width or record.pro_height or record.pro_length):
                tot_qty = 1.00
            else:
                tot_qty = record.pro_width * record.pro_height * record.pro_length
            weight = tot_qty * record.product_id.weight
            record.update({
                'tot_qty' : tot_qty,
                'custom_weight' : weight
            })

    @api.onchange('pro_width')
    def onchange_width(self):
        
        if self.pro_width < self.product_id.width_min_2 or self.pro_width > self.product_id.width_max_2:
            warning = "You can only enter width between minimum " + str(self.product_id.width_min_2) + " to maximum " + str(self.product_id.width_max_2) + "feet"
            return {
                'warning': {'title': 'Error!', 'message': warning},
                'value': {
                    'pro_width': '',
                }
            } 

    @api.onchange('width')
    def onchange_for_width(self):
        if self.width < self.product_id.width_min_2 or self.width > self.product_id.width_max_2:
            warning = "You can only enter width between minimum " + str(self.product_id.width_min_2) + " to maximum " + str(self.product_id.width_max_2) + " feet"
            return {
                    'warning': {'title': 'Error!', 'message': warning},
                    'value': {
                              'width': '',
                    }
            }

    @api.onchange('height')
    def onchange_for_height(self):
        if self.height < self.product_id.height_min_3 or self.height > self.product_id.height_max_3:
            warning = "You can only enter height between minimum " + str(self.product_id.height_min_3) + " to maximum " + str(self.product_id.height_max_3) + " feet"
            return {
                    'warning': {'title': 'Error!', 'message': warning},
                    'value': {
                             'height': '',
                             }
            }
    
    @api.onchange('pro_height')
    def onchange_height(self):
        
        if self.pro_height < self.product_id.height_min_3 or self.pro_height > self.product_id.height_max_3:
            warning = "You can only enter height between minimum " + str(self.product_id.height_min_3) + " to maximum " + str(self.product_id.height_max_3) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_height': '',
                            }

            }

    @api.onchange('pro_length')
    def onchange_length(self):
        
        if self.pro_length < self.product_id.len_min_1 or self.pro_length > self.product_id.len_max_1:
            warning = "You can only enter length between minimum " + str(self.product_id.len_min_1) + " to maximum " + str(self.product_id.len_max_1) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_length': '',
                            }

            }
            
    width = fields.Float('Width (Mt.)', required='True', default=0.0)
    height = fields.Float('Height (Mt.)', required='True', default=0.0)
    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label = fields.Char('Label')
    
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(compute='get_tot_qty', string='Dim Qty', store=True)
    dimension_method = fields.Selection(related='move_id.dimension_method',string="Dimention Method")  
    custom_weight = fields.Float(compute='get_tot_qty',string='Weight Ea.', readonly=True, store=True)

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids','pro_length', 'pro_height','pro_width','height', 'width','tot_qty')
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line._get_m2()
            line.get_tot_qty()
            line.update(line.with_context(height=line.height,width=line.width)._get_price_total_and_subtotal(m2=line.m2))
            line.update(line.with_context(pro_width=line.pro_width,pro_height=line.pro_height,pro_length=line.pro_length,)._get_price_total_and_subtotal(tot_qty=line.tot_qty))
        
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, m2=None,tot_qty=None,weight=None):
        self.ensure_one() 
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.move_type,
            m2=m2 or (self.height * self.width),
            tot_qty=tot_qty or (self.pro_height * self.pro_width * self.pro_length),
            weight =weight or (self.pro_height * self.pro_width * self.pro_length * self.product_id.weight),
        )


    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type, m2=None,tot_qty=None,weight=None):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}


        if not m2:
            m2 = (self.height * self.width) or 1.0

        if not tot_qty:
            tot_qty = (self.pro_height * self.pro_width * self.pro_length) or 1.0
                
        if not weight:
            weight =(tot_qty * self.product_id.weight),

        if self.env.user.company_id.price_calculation == 'dimension':
            quantity = quantity * m2
            quantity =  tot_qty * quantity
        else:
            quantity = quantity

            
        price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * price_unit_wo_discount

        if taxes:
            taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal

        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res



    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, force_computation=False,m2=None , tot_qty=None,weight=None):
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param amount_currency: The new balance in line's currency.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        if not tot_qty:
            tot_qty = (self.pro_height * self.pro_width * self.pro_length) or 1.0
        
        tot_qty=tot_qty

        if not weight:
            weight =weight or (tot_qty * self.product_id.weight),

        custom_weight = weight

        if not m2:
            m2= self.height * self.width or 1.0

        if self.env.user.company_id.price_calculation == 'dimension':
            m2 = m2
        else:
            m2 = 1.0
        qty=m2*tot_qty

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if not force_computation and currency.is_zero(amount_currency - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']

        discount_factor = 1 - (discount / 100.0)
        if amount_currency and discount_factor:
            # discount != 100%
            vals = {
                'quantity': quantity or 1.0,
                'price_unit': amount_currency / discount_factor / ((quantity * qty) or 1.0),
            }
        elif amount_currency and not discount_factor:
            # discount == 100%
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': amount_currency / ((quantity * qty) or 1.0),
            }
        elif not discount_factor:
            # balance of line is 0, but discount  == 100% so we display the normal unit_price
            vals = {}
        else:
            # balance is 0, so unit price is 0 as well
            vals = {'price_unit': 0.0}
        return vals



    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        result = super(AccountMoveLine, self).create(vals_list)
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    if vals.get('currency_id'):
                        balance = vals.get('amount_currency', 0.0)
                    else:
                        balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                    price_subtotal = self.with_context(first=True)._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        m2=vals.get('width',1.0)*vals.get('height',1.0),
                        tot_qty=vals.get('pro_width',1.0)*vals.get('pro_height',1.0)*vals.get('pro_length',1.0),
                    ).get('price_subtotal', 0.0)
                    vals.update(self.with_context(other=True)._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        balance,
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal,
                        m2=vals.get('width',1.0)*vals.get('height',1.0),
                        tot_qty=vals.get('pro_width',1.0)*vals.get('pro_height',1.0)*vals.get('pro_length',1.0),
                    ))
                    vals.update(self.with_context(sec=True)._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        m2=vals.get('width',1.0)*vals.get('height',1.0),
                        tot_qty=vals.get('pro_width',1.0)*vals.get('pro_height',1.0)*vals.get('pro_length',1.0),
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self.with_context(third=True)._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        m2=vals.get('width',1.0)*vals.get('height',1.0),
                        tot_qty=vals.get('pro_width',1.0)*vals.get('pro_height',1.0)*vals.get('pro_length',1.0),
                    ))

                line = result.filtered(lambda x : x.name == vals.get('name'))
                line.write(vals)

        return result

