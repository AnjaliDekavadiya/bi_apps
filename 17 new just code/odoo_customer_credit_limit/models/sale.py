# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class Sale(models.Model):
    _inherit = 'sale.order'

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     for rec in self:
    #         # rec.credit_limit = rec.partner_id.credit_limit
    #         rec.credit = rec.partner_id.credit
    #     return super(Sale, self).onchange_partner_id()
        
    
    is_website_order = fields.Boolean(
        string='Is Website Order',
        copy=False,
    )
    is_skip_credit_limit = fields.Boolean(
        string='Skip Credit Limit Validation',
        copy=True,
    )
    # @api.model
    # def create(self, vals):
    #     if self._context.get('website_id'):
    #         vals.update({'is_website_order':True,})
    #     return super(Sale, self).create(vals)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._context.get('website_id'):
            vals.update({'is_website_order':True,})
        return super(Sale, self).create(vals_list)



    
    def _partner_credit_limit(self):
        # invoice_obj = self.env['account.invoice']
        for rec in self:
            if rec.partner_id.credit_rule_id:
                if rec.partner_id.credit_rule_id.credit_type == 'customer':
                    if rec.partner_id.credit_limit < rec.partner_id.credit:
                        raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
                    elif rec.partner_id.credit == 0.0 and rec.partner_id.credit_limit < rec.amount_untaxed:
                        raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
                    elif rec.partner_id.credit_limit < rec.partner_id.credit + rec.amount_untaxed:
                        raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
                else:
                    days = rec.partner_id.credit_rule_id.credit_days
                    current_date = fields.Date.today()
                    first_date = datetime.datetime.strptime(str(current_date), "%Y-%m-%d") + timedelta(days)
                    tables, where_clause, where_params = self.env['account.move.line']._custom_query_get()
                    # where_params = [tuple(rec.partner_id.ids)] + [first_date] + where_params
                    where_params = [tuple(rec.partner_id.commercial_partner_id.ids)] + [first_date] + where_params
                    if where_clause:
                        where_clause = 'AND ' + where_clause

                    self._cr.execute("""SELECT account_move_line.partner_id, a.account_type,SUM(account_move_line.amount_residual)
                                      FROM """ + tables + """
                                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                                      AND account_move_line.partner_id IN %s
                                      AND account_move_line.reconciled IS FALSE
                                      AND account_move_line.date_maturity <= %s
                                      """ + where_clause + """
                                      GROUP BY account_move_line.partner_id,a.account_type
                                      """, where_params)
                                      
                    move_line = self._cr.fetchall()
                    credit = 0.0
                    for type,pid,val in move_line:
                        partner = self.browse(pid)
                        if type == 'asset_receivable':
                            credit = val

                    line_lst=[]
                    compute_credit_amt_limit = 0.0
                    credit_amt_limit = 0.0
                    if not (rec.partner_id.credit_rule_id.categ_ids and rec.partner_id.credit_rule_id.product_tmpl_ids):
                            credit_amt_limit += sum(line.price_subtotal for line in rec.order_line)
                    else:
                        for line in rec.order_line:
                            if rec.partner_id.credit_rule_id.categ_ids:
                                if line.product_id.categ_id in rec.partner_id.credit_rule_id.categ_ids:
                                    if line not in line_lst:
                                        line_lst.append(line)
                                        
                            if rec.partner_id.credit_rule_id.product_tmpl_ids:
                                if line.product_id.product_tmpl_id in rec.partner_id.credit_rule_id.product_tmpl_ids:
                                    if line not in line_lst:
                                        line_lst.append(line)
                    
                        credit_amt_limit += sum(line.price_subtotal for line in line_lst)

                    if rec.partner_id.credit_rule_id.currency_id != rec.pricelist_id.currency_id:
                        #compute_credit_amt_limit +=  rec.partner_id.credit_rule_id.currency_id.compute(credit_amt_limit, rec.pricelist_id.currency_id)
                        compute_credit_amt_limit +=  rec.partner_id.credit_rule_id.currency_id._convert(credit_amt_limit, rec.pricelist_id.currency_id, rec.company_id, rec.date_order)

                    else:
                        compute_credit_amt_limit += credit_amt_limit

                    compute_credit_amt_limit += credit
                    if rec.partner_id.credit_limit < compute_credit_amt_limit:
                        raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
        return True
        
    # @api.multi
    def action_confirm(self):
        if not self.is_website_order:
            if not self.is_skip_credit_limit:
                credit_limit = self._partner_credit_limit()
        return super(Sale, self).action_confirm()

    # def _partner_credit_limit(self):
    #     # invoice_obj = self.env['account.invoice']
    #     for rec in self:
    #         if rec.partner_id.credit_rule_id:
    #             if rec.partner_id.credit_rule_id.credit_type == 'customer':
    #                 if rec.partner_id.credit_limit < rec.partner_id.credit:
    #                     raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
    #                 elif rec.partner_id.credit == 0.0 and rec.partner_id.credit_limit < rec.amount_untaxed:
    #                     raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
    #                 elif rec.partner_id.credit_limit < rec.partner_id.credit + rec.amount_untaxed:
    #                     raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
    #             else:
    #                 days = rec.partner_id.credit_rule_id.credit_days
    #                 current_date = fields.Date.today()
    #                 first_date = datetime.datetime.strptime(str(current_date), "%Y-%m-%d") + timedelta(days)
    #                 tables, where_clause, where_params = self.env['account.move.line']._query_get()
    #                 # where_params = [tuple(rec.partner_id.ids)] + [first_date] + where_params
    #                 where_params = [tuple(rec.partner_id.commercial_partner_id.ids)] + [first_date] + where_params
    #                 if where_clause:
    #                     where_clause = 'AND ' + where_clause

    #                 self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
    #                                   FROM """ + tables + """
    #                                   LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
    #                                   LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
    #                                   WHERE act.type IN ('receivable','payable')
    #                                   AND account_move_line.partner_id IN %s
    #                                   AND account_move_line.reconciled IS FALSE
    #                                   AND account_move_line.date_maturity <= %s
    #                                   """ + where_clause + """
    #                                   GROUP BY account_move_line.partner_id, act.type
    #                                   """, where_params)
                                      
    #                 move_line = self._cr.fetchall()
    #                 credit = 0.0
    #                 for pid, type, val in move_line:
    #                     partner = self.browse(pid)
    #                     if type == 'receivable':
    #                         credit = val

    #                 line_lst=[]
    #                 compute_credit_amt_limit = 0.0
    #                 credit_amt_limit = 0.0
    #                 if not (rec.partner_id.credit_rule_id.categ_ids and rec.partner_id.credit_rule_id.product_tmpl_ids):
    #                         credit_amt_limit += sum(line.price_subtotal for line in rec.order_line)
    #                 else:
    #                     for line in rec.order_line:
    #                         if rec.partner_id.credit_rule_id.categ_ids:
    #                             if line.product_id.categ_id in rec.partner_id.credit_rule_id.categ_ids:
    #                                 if line not in line_lst:
    #                                     line_lst.append(line)
                                        
    #                         if rec.partner_id.credit_rule_id.product_tmpl_ids:
    #                             if line.product_id.product_tmpl_id in rec.partner_id.credit_rule_id.product_tmpl_ids:
    #                                 if line not in line_lst:
    #                                     line_lst.append(line)
                    
    #                     credit_amt_limit += sum(line.price_subtotal for line in line_lst)

    #                 if rec.partner_id.credit_rule_id.currency_id != rec.pricelist_id.currency_id:
    #                     #compute_credit_amt_limit +=  rec.partner_id.credit_rule_id.currency_id.compute(credit_amt_limit, rec.pricelist_id.currency_id)
    #                     compute_credit_amt_limit +=  rec.partner_id.credit_rule_id.currency_id._convert(credit_amt_limit, rec.pricelist_id.currency_id, rec.company_id, rec.date_order)

    #                 else:
    #                     compute_credit_amt_limit += credit_amt_limit

    #                 compute_credit_amt_limit += credit
    #                 if rec.partner_id.credit_limit < compute_credit_amt_limit:
    #                     raise ValidationError(_('You can not confirm quotation since customer has reached credit limit. If you want to forcefully confirm then please contact your manager.'))
    #     return True odoo15 18-11-2022
                    
            
    
    
