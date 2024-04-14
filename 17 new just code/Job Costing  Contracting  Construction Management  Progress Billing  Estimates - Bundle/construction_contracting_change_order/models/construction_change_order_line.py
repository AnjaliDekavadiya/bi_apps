# -*- coding: utf-8 -*-

# from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ConstructionChngeOrderLine(models.Model):
    _name = 'construction.change.order.line'
    _description = "Change Order Line"
    _order = 'id desc'
    _rec_name = 'product_id'

    # @api.depends('quantity', 'sale_price', 'tax_ids')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         price = line.sale_price * (1 - (0.0) / 100.0)
    #         taxes = line.tax_ids.compute_all(price, line.currency_id, line.quantity, product=line.product_id, partner=line.change_order_id.partner_id)
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             #'price_subtotal': taxes['total_excluded'],
    #             'subtotal': taxes['total_excluded'],
    #         })

    @api.depends('quantity', 'discount', 'sale_price', 'tax_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.sale_price * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, line.currency_id, line.quantity, product=line.product_id, partner=line.change_order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'subtotal': taxes['total_excluded'],
            })


    # @api.depends('quantity', 'sale_price', 'tax_ids', 'discount')
    # def _compute_amount(self):
    #     for rec in self:
    #         if rec.discount:
    #             disc_amount = (rec.sale_price * rec.quantity) * rec.discount / 100
    #             rec.subtotal = (rec.sale_price * rec.quantity) - disc_amount
    #             rec.price_total = (rec.sale_price * rec.quantity) - disc_amount
    #         else:
    #             rec.subtotal = rec.sale_price * rec.quantity
    #             rec.price_total = rec.sale_price * rec.quantity

    # @api.multi #odoo13
    @api.depends('quantity', 'sale_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.sale_price

    price_tax = fields.Float(
        compute='_compute_amount',
        string='Amount Taxes',
        readonly=True,
        store=True,
     )
    price_total = fields.Monetary(
        compute='_compute_amount',
        string='Total',
        readonly=True,
        store=True,
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product',
    )
    quantity = fields.Float(
        string='Quantity',
        # digits=dp.get_precision('Product Unit of Measure'),
        digits='Product Unit of Measure', #odoo13
        default=1.0
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='Uom',
    )
    description = fields.Text(
        string='Description',
        required=True,
    )
    sale_price = fields.Float(
        string='Sale Price',
        # digits=dp.get_precision('Product Price'),
        digits='Product Price', #odoo13
        default=0.0
    )
    change_order_id = fields.Many2one(
        'construction.change.order',
        string='Construction Change',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='change_order_id.currency_id',
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_amount',
        store=True,
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes',
    )
    discount = fields.Float(
        string='Discount (%)'
    )

    def _compute_tax_id(self):
        for line in self:
            # line = line.with_company(line.company_id)
            line = line.with_company(self.env.company)
            # fpos = self.env['account.fiscal.position'].get_fiscal_position(line.change_order_id.partner_id.id)
            fpos = self.env['account.fiscal.position']._get_fiscal_position(line.change_order_id.partner_id)
            # If company_id is set, always filter taxes by the company
            # taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            taxes = line.product_id.taxes_id.filtered(lambda r: not self.env.company or r.company_id == self.env.company)
            line.tax_ids = fpos.map_tax(taxes)

    def _get_custom_pricelist_item_id(self):
        for line in self:
            if not line.product_id or not line.change_order_id.pricelist_id:
                pricelist_item_id = False
            else:
                pricelist_item_id = line.change_order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.quantity or 1.0,
                    uom=line.uom_id,
                    date=line.change_order_id.date,
                )

            pricelist_item = pricelist_item_id

            pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_item)

            order_date = line.change_order_id.date or fields.Date.today()
            product = line.product_id
            qty = line.quantity or 1.0
            uom = line.uom_id or line.product_id.uom_id

            price = pricelist_rule._compute_price(
                # product, qty, uom, order_date, currency=self.currency_id)
                product, qty, uom, order_date, currency=line.change_order_id.pricelist_id.currency_id)
        return price

    def _get_pricelist_price_before_discount(self):
        for line in self:
            pricelist_item_id = line.change_order_id.pricelist_id._get_product_rule(
                        line.product_id,
                        line.quantity or 1.0,
                        uom=line.uom_id,
                        date=line.change_order_id.date,
                    )
            pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_item_id)

            order_date = line.change_order_id.date or fields.Date.today()
            product = line.product_id
            qty = line.quantity or 1.0
            uom = line.uom_id

            if pricelist_rule:
                pricelist_item = pricelist_rule
                if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                    # Find the lowest pricelist rule whose pricelist is configured
                    # to show the discount to the customer.
                    while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                        rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                            product, qty, uom=uom, date=order_date)
                        pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

                pricelist_rule = pricelist_item

            price = pricelist_rule._compute_base_price(
                product,
                qty,
                uom,
                order_date,
                target_currency=self.change_order_id.pricelist_id.currency_id,
            )

        return price

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # if self.change_order_id.pricelist_id.discount_policy == 'with_discount':
        #     return product.with_context(pricelist=self.change_order_id.pricelist_id.id).price
        # # product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date_order, uom=self.uom_id.id)#
        # product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date, uom=self.uom_id.id)#
        # price, rule_id = self.change_order_id.pricelist_id.get_product_price_rule(self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
        # base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, 
        #     self.uom_id, self.change_order_id.pricelist_id.id)
        # pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
        # if currency != self.change_order_id.pricelist_id.currency_id: #
        #     base_price = currency._convert(
        #         base_price, self.change_order_id.pricelist_id.currency_id,
        #         self.change_order_id.company_id or self.env.company, self.change_order_id.date or fields.Date.today()) #
        # return max(base_price, price) #


        # if self.change_order_id.pricelist_id.discount_policy == 'with_discount':
        #     return product.with_context(pricelist=self.change_order_id.pricelist_id.id, uom=self.uom_id.id).price
        # product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date, uom=self.uom_id.id)

        # # final_price, rule_id = self.change_order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
        # final_price, rule_id = self.change_order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
        # base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.uom_id.id, self.change_order_id.pricelist_id.id)
        # if currency != self.change_order_id.pricelist_id.currency_id:
        #     base_price = currency._convert(
        #         base_price, self.change_order_id.pricelist_id.currency_id,
        #         self.change_order_id.company_id or self.env.company, self.change_order_id.date or fields.Date.today())
        # # negative discounts (= surcharge) are included in the display price
        # return max(base_price, final_price)
        # if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
        #     price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
        #     return price
        # else:
        #     from_currency = self.change_order_id.company_id.currency_id
        #     return from_currency.compute(product.lst_price, self.change_order_id.pricelist_id.currency_id)
        pricelist_price = self._get_custom_pricelist_item_id()

        if self.change_order_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price
        
        base_price = self._get_pricelist_price_before_discount()

        return max(base_price, pricelist_price)

    @api.onchange('product_id')
    def _onchange_product(self):
        vals = {}
        desc = ' '
        for rec in self:
            if not rec.product_id: #
                return #
            if rec.product_id:
                if not rec.uom_id or (rec.product_id.uom_id.id != rec.uom_id.id): #
                    vals['uom_id'] = rec.product_id.uom_id #
                    vals['quantity'] = rec.quantity or 1.0 #
                rec.uom_id = rec.product_id.uom_id.id
                if rec.product_id.description_sale:
                    rec.description = rec.product_id.name + '\n' + rec.product_id.description_sale
                else:
                    rec.description = rec.product_id.name
                #rec.sale_price = rec.product_id.lst_price
                # rec.tax_ids = rec.product_id.taxes_id.ids

                self._compute_tax_id()

                vals['quantity'] = 1.0

                product = self.product_id.with_context(
                    lang=self.change_order_id.partner_id.lang,
                    partner=self.change_order_id.partner_id.id,
                    quantity=vals.get('quantity') or self.quantity,
                    date=self.change_order_id.date,
                    pricelist=self.change_order_id.pricelist_id.id,
                    uom=self.uom_id.id,
                )

                if self.change_order_id.pricelist_id and self.change_order_id.partner_id:
                    vals['sale_price'] = product._get_tax_included_unit_price(
                        # self.company_id,
                        self.env.company,
                        self.change_order_id.currency_id,
                        self.change_order_id.date,
                        'sale',
                        product_price_unit=self._get_display_price(product),
                        product_currency=self.change_order_id.currency_id
                    )

                # if self.change_order_id.pricelist_id and self.change_order_id.partner_id:
                #     a = self._get_display_price(rec.product_id)
                #     vals['sale_price'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_ids, self.change_order_id.company_id)
                #     rec.update(vals)

                self.update(vals)

                title = False #
                message = False #
                result = {} #
                warning = {} #

                if product and product.sale_line_warn != 'no-message':
                    if product.sale_line_warn == 'block':
                        self.product_id = False
                    return {
                        'warning': {
                            'title': _("Warning for %s", product.name),
                            'message': product.sale_line_warn_msg,
                        }
                    }
                # if product.sale_line_warn != 'no-message': #
                #     title = _("Warning for %s", product.name) #
                #     message = product.sale_line_warn_msg #
                #     warning['title'] = title #
                #     warning['message'] = message # 
                #     result = {'warning': warning} #
                #     if product.sale_line_warn == 'block': #
                #         rec.product_id = False #

                # return result #

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    # _price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.change_order_id.partner_id)
                    _price, rule_id = self.change_order_id.pricelist_id.with_context(product_context)._get_product_price_rule(self.product_id, self.quantity or 1.0)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
                product_currency = product.cost_currency_id
            elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.env.company, self.change_order_id.date or fields.Date.today())

        uom_id = self.env.context.get('uom') or product.uom_id.id
        # if uom and uom.id != uom_id:
        if uom and uom != uom_id:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    # @api.onchange('product_id', 'price_unit', 'uom_id', 'quantity', 'tax_id')
    @api.onchange('product_id', 'sale_price', 'uom_id', 'quantity', 'tax_ids')
    def _onchange_discount(self):
        if not (self.product_id and self.uom_id and
                self.change_order_id.partner_id and self.change_order_id.pricelist_id and
                self.change_order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.change_order_id.partner_id.lang,
            partner=self.change_order_id.partner_id,
            quantity=self.quantity,
            date=self.change_order_id.date,
            pricelist=self.change_order_id.pricelist_id.id,
            uom=self.uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date, uom=self.uom_id.id)

        # price, rule_id = self.change_order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
        price, rule_id = self.change_order_id.pricelist_id.with_context(product_context)._get_product_price_rule(self.product_id, self.uom_id or 1.0)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.uom_id, self.change_order_id.pricelist_id.id)

        if new_list_price != 0:
            if self.change_order_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.change_order_id.pricelist_id.currency_id,
                    self.change_order_id.company_id or self.env.company, self.change_order_id.date or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount

    # @api.multi #odoo13
    # def _get_display_price(self, product):
    #     # TO DO: move me in master/saas-16 on sale.order
    #     # if self.change_order_id.pricelist_id.discount_policy == 'with_discount':
    #     #     return product.with_context(pricelist=self.change_order_id.pricelist_id.id).price
    #     # # product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date_order, uom=self.uom_id.id)#
    #     # product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date, uom=self.uom_id.id)#
    #     # price, rule_id = self.change_order_id.pricelist_id.get_product_price_rule(self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
    #     # base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, 
    #     #     self.uom_id, self.change_order_id.pricelist_id.id)
    #     # pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
    #     # if currency != self.change_order_id.pricelist_id.currency_id: #
    #     #     base_price = currency._convert(
    #     #         base_price, self.change_order_id.pricelist_id.currency_id,
    #     #         self.change_order_id.company_id or self.env.company, self.change_order_id.date or fields.Date.today()) #
    #     # return max(base_price, price) #


    #     if self.change_order_id.pricelist_id.discount_policy == 'with_discount':
    #         return product.with_context(pricelist=self.change_order_id.pricelist_id.id, uom=self.uom_id.id).price
    #     product_context = dict(self.env.context, partner_id=self.change_order_id.partner_id.id, date=self.change_order_id.date, uom=self.uom_id.id)

    #     final_price, rule_id = self.change_order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
    #     base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.quantity, self.uom_id.id, self.change_order_id.pricelist_id.id)
    #     if currency != self.change_order_id.pricelist_id.currency_id:
    #         base_price = currency._convert(
    #             base_price, self.change_order_id.pricelist_id.currency_id,
    #             self.change_order_id.company_id or self.env.company, self.change_order_id.date or fields.Date.today())
    #     # negative discounts (= surcharge) are included in the display price
    #     return max(base_price, final_price)
    #     if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
    #         price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id, self.quantity or 1.0, self.change_order_id.partner_id)
    #         return price
    #     else:
    #         from_currency = self.change_order_id.company_id.currency_id
    #         return from_currency.compute(product.lst_price, self.change_order_id.pricelist_id.currency_id)

    # @api.multi #odoo13
    # @api.onchange('product_id')
    # def _onchange_product(self):
    #     vals = {}
    #     desc = ' '
    #     for rec in self:
    #         if not rec.product_id: #
    #             return #
    #         if rec.product_id:
    #             if not rec.uom_id or (rec.product_id.uom_id.id != rec.uom_id.id): #
    #                 vals['uom_id'] = rec.product_id.uom_id #
    #                 vals['quantity'] = rec.quantity or 1.0 #
    #             rec.uom_id = rec.product_id.uom_id.id
    #             if rec.product_id.description_sale:
    #                 rec.description = rec.product_id.name + '\n' + rec.product_id.description_sale
    #             else:
    #                 rec.description = rec.product_id.name
    #             #rec.sale_price = rec.product_id.lst_price
    #             rec.tax_ids = rec.product_id.taxes_id.ids
    #             vals['quantity'] = 1.0
    #             product = self.product_id.with_context(
    #                 lang=self.change_order_id.partner_id.lang,
    #                 partner=self.change_order_id.partner_id.id,
    #                 quantity=vals.get('quantity') or self.quantity,
    #                 date=self.change_order_id.date,
    #                 pricelist=self.change_order_id.pricelist_id.id,
    #                 uom=self.uom_id.id,
    #             )

    #             if self.change_order_id.pricelist_id and self.change_order_id.partner_id:
    #                 a = self._get_display_price(rec.product_id)
    #                 vals['sale_price'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_ids, self.change_order_id.company_id)
    #                 rec.update(vals)

    #             title = False #
    #             message = False #
    #             result = {} #
    #             warning = {} #
    #             if product.sale_line_warn != 'no-message': #
    #                 title = _("Warning for %s", product.name) #
    #                 message = product.sale_line_warn_msg #
    #                 warning['title'] = title #
    #                 warning['message'] = message # 
    #                 result = {'warning': warning} #
    #                 if product.sale_line_warn == 'block': #
    #                     rec.product_id = False #

    #             return result #

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
