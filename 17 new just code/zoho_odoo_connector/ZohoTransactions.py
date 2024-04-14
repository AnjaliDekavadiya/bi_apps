# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from logging import getLogger
import pytz

_logger = getLogger(__name__)

class ZohoProductRequiredParam(Exception):
    pass

ACCOUNT_IN = {
    "bank"                   : "asset_cash",
    "cash"                   : "asset_cash",
    "accounts_receivable"    : "asset_receivable",
    "fixed_asset"            : "asset_fixed",
    "other_current_asset"    : "asset_current",
    "other_asset"            : "asset_non_current",
    "other_current_liability": "liability_current",
    "long_term_liability"    : "liability_current",
    "equity"                 : "equity",
    "other_income"           : "income_other",
    "expense"                : "expense",
    "other_expense"          : "expense",
    "cost_of_goods_sold"     : "expense_direct_cost",
    "accounts_payable"       : "liability_payable",
    "credit_card"            : "liability_credit_card",
    "income"                 : "income",
    "other_liability"        : "liability_current",              
}
ACCOUNT_OUT = {
    "asset_cash"            : "bank",
    "asset_receivable"      : "accounts_receivable",
    "asset_fixed"           : "fixed_asset",
    "asset_current"         : "other_current_asset",
    "liability_current"     : "other_current_liability",
    "equity"                : "equity",
    "income_other"          : "other_income",
    "expense"               : "expense",
    "expense_direct_cost"   : "cost_of_goods_sold",
    "liability_payable"     : "accounts_payable",
    "liability_credit_card" : "credit_card",
    "income"                : "income",
    "liability_current"     : "other_liability"
}


class ZohoTransactions:

    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.gst_in = True if instance_id.user_domain == 'in' else False # gst_india
    
    #####################
    # Import Operations #
    #####################

    def get_accounts(self,zoho, **kwargs)->list:
        data_list = []
        accounts = zoho.get("chartofaccounts",params=kwargs)
        accounts_json = accounts.get('json')
        if not accounts_json:
            err_message = f"Error in getting Accounts : {accounts.get('f_error')}"
            kwargs.update({'message': err_message})
            _logger.error(err_message)
        else:
            data_list = list(map(self._get_account, accounts_json.get("chartofaccounts")))
        if accounts_json and not accounts_json.get('page_context',{}).get('has_more_page'):
            kwargs.update(stop=True)
        return kwargs, data_list
    
    def _get_account(self, account)->dict:
        account_type = self._get_odoo_account_type(account.get('account_type'))
        return {
            'name': account.get('account_name'),
            'instance_id': self.instance_id.id,
            'remote_id':account.get('account_id'),
            'code':account.get('account_code'),
            'account_type': account_type
        } 
    
    def _get_odoo_account_type(self, zoho_account_type):
        odoo_account_type = ACCOUNT_IN.get(zoho_account_type, "asset_cash")
        return odoo_account_type

    def get_customers(self, zoho, **kwargs)->list:
        data_list = []
        customers = zoho.get("contacts", params=kwargs)
        customers_json = customers.get('json')
        if not customers_json:
            err_message = f"Error in getting Customers : {customers.get('f_error')}"
            _logger.error(err_message)
            kwargs.update({'message': err_message})
        else:
            data_list = list(map(self._get_customer, customers_json.get("contacts")))
        if customers_json and not customers_json.get('page_context',{}).get('has_more_page'):
            kwargs.update(stop = True)
        return kwargs, data_list

    def _get_customer(self, contact)->dict:
        vals = {}
        instance_id = self.instance_id
        zoho = instance_id.get_zohoapi_object()
        contact = zoho.get('contacts', resource_id = contact.get('contact_id'))
        contact_json = contact.get('json')
        if contact_json:
            contact = contact_json.get('contact')
            remote_id = contact.get('contact_id')
            if contact.get("first_name") and contact.get('last_name'):
                name = contact.get("first_name") +" "+ contact.get('last_name')
            else:
                name = contact.get('contact_name')
            vals = {
                'name': name,
                'instance_id': instance_id.id,
                'remote_id': remote_id,
                'email': contact.get("email"),
                'type': 'contact',
                'customer_type': contact.get('contact_type'),
                'phone':contact.get('phone'),
                'mobile':contact.get('mobile'),
                'website':contact.get('website'),
                # 'company_name':contact.get('company_name'),
                'street'      : contact['billing_address'].get('address'),
                'street2'     : contact['billing_address'].get('street2'),
                'city'        : contact['billing_address'].get('city'),
                'state_code'  : contact['billing_address'].get('state_code'),
                'state_name'  : contact['billing_address'].get('state'),
                'country_code': contact['billing_address'].get('country_code'),
                'zip'         : contact['billing_address'].get('zip'),
            }
            shipping_address = contact['shipping_address']
            if shipping_address.get('address') or shipping_address.get('street2') or shipping_address.get('city') or shipping_address.get('state_code'):
                ship_contact = [
                    {
                        'type'        : 'delivery',
                        'name'        : name,
                        'street'      : contact['shipping_address'].get('address'),
                        'street2'     : contact['shipping_address'].get('street2'),
                        'city'        : contact['shipping_address'].get('city'),
                        'state_code'  : contact['shipping_address'].get('state_code'),
                        'state_name'  : contact['billing_address'].get('state'),
                        'country_code': contact['shipping_address'].get('country_code'),
                        'zip'         : contact['shipping_address'].get('zip'),
                        'email'       : contact.get('email'),
                        'phone'       : contact['shipping_address'].get('phone'),
                    }
                ]
                vals.update({'contacts': ship_contact})
        return vals
    
    def get_products(self, zoho, **kwargs)->list:
        data_list = []
        products = zoho.get("items", params=kwargs)
        products_json = products.get('json')
        if not products_json:
            kwargs.update({'message': f"Error in Getting Products: {products.get('f_error')}"})
        else:
            data_list = list(map(self._get_product, products_json.get("items")))
        if products_json and not products_json.get('page_context',{}).get('has_more_page'):
            kwargs.update(stop=True)
        return kwargs, data_list
    
    def _get_product(self, product)->dict:
        return {
            'name': product.get("name"),
            'instance_id': self.instance_id.id,
            'remote_id': product.get("item_id"),
            'type':"product" if product.get("product_type") == 'goods' else "service",
            'sale_ok':True if product.get('item_type') == "sales_and_purchases" or product.get('item_type') == "sales" else False,
            'purchase_ok':True if product.get('item_type') == "sales_and_purchases" or product.get('item_type') == "purchases" else False,
            'list_price':product.get("rate"),
            'default_code':product.get("sku"),
            'description_sale':product.get("description"),
            'description_purchase':product.get('purchase_description'),
            'standard_price':product.get('purchase_rate'),
            'qty_available':product.get('stock_on_hand',''),
        }
    
    def get_orders(self, zoho, **kwargs)->list:
        instance_id = self.instance_id
        data_list = []
        if kwargs.get('from_cron'):
            orders = zoho.get('salesorders', params = {
                'page':kwargs.get('page'),
                'per_page':kwargs.get('per_page'),
                'date_start' : instance_id.import_order_date.strftime('%Y-%m-%d'),
                'sort_column': 'date',
            })
        else:
            orders = zoho.get("salesorders", params=kwargs)
        orders_json = orders.get('json')
        if not orders_json:
            kwargs.update({'message': f"Error in Getting Orders: {orders.get('f_error')}"})
        else:
            data_list = list(map(self._get_order, orders_json.get("salesorders")))
        if orders_json and not orders_json.get('page_context',{}).get('has_more_page'):
            kwargs.update(stop=True)
        if data_list and data_list[0].get('date_order') and kwargs.get("from_cron"):
            instance_id.import_order_date = data_list[0].get('date_order')
        return kwargs, data_list

    def _get_order(self, order)->dict:
        vals = {}
        instance_id = self.instance_id
        zoho = instance_id.get_zohoapi_object()
        order = zoho.get('salesorders', resource_id = order.get('salesorder_id'))
        order_json = order.get('json',{}).get('salesorder')
        if order_json:
            vals = {
                'instance_id':instance_id.id,
                'remote_id':order_json.get("salesorder_id"),
                'zoho_doc_number': order_json.get("reference_number"),
                'origin':order_json.get("salesorder_number"),
                'partner_id': order_json.get('customer_id'),
                'date_order': order_json.get('date'),
                'order_state':order_json.get('status'),
                'currency_code':order_json.get('currency_code'),
            }
            order_line = self._create_sale_order_lines(order_json.get('discount_type'),order_json.get('discount'), order_json.get('is_inclusive_tax'), order_json.get("line_items"))
            if order_json.get('discount_type') == 'entity_level' and order_json.get("discount_amount"):
                if type(order_json.get('discount')) != str:
                    tax_list = []
                    for line in order_line:
                        if line.get('line_taxes'):
                            tax_list.extend(line.get('line_taxes'))
                    order_line.append({
                        "name":"Discount",
                        "product_uom_qty": 1,
                        "price_unit": -float(order_json.get("discount_amount")),
                        'line_source' : 'discount',
                        "line_taxes": tax_list if order_json.get('is_discount_before_tax') else False,
                    })
            vals["order_lines"] = order_line
        return vals
    
    def _create_sale_order_lines(self, discount_type, discount, is_incusive_tax, line_items:list)->list:
        data_list = [self._get_order_line_item(line, is_incusive_tax, discount_type, discount) for line in line_items]
        return data_list
    
    def _get_order_line_item(self, item:dict, is_inclusive_tax, discount_type, discount)->tuple:
        discount_amount = False
        item_rate = item.get('rate')
        if discount_type == 'entity_level':
            if discount:
                if type(discount) == str:
                    discount_amount = float(discount.replace('%',''))
        if item.get('discount'):
            if type(item.get('discount')) == str:
                discount_amount = float(item.get('discount').replace('%',''))
            else:
                if is_inclusive_tax:
                    item_exclusive_amount = item_rate/(1+item.get('tax_percentage')/100)
                    discount_amount = (item.get('discount_amount')/item_exclusive_amount)*100
                else:
                    discount_amount = item.get('discount_amount')/item_rate * 100
        return dict(
            product_id = item.get("item_id"),
            product_uom_qty = item.get("quantity"),
            price_unit = item.get("rate"),
            name = item.get("name"),
            variant_id = item.get('variant_id'),
            line_taxes = self.get_order_line_taxes(item.get('tax_id')),
            discount = discount_amount
        )
        
    def get_order_line_taxes(self, tax_id):
        if tax_id:
            match_tax = self.instance_id.match_tax_mapping(remote_id=tax_id)
            if match_tax and match_tax.name:
                return [{'remote_id': tax_id}]
            zoho = self.instance_id.get_zohoapi_object()
            tax_data = zoho.get('settings/taxes', resource_id = tax_id)
            tax_json = tax_data.get('json',{})
            if tax_json:
                tax_json = tax_json.get('tax')
                return [{
                            'rate': tax_json.get("tax_percentage"),
                            'name': tax_json.get('tax_name'),
                            'type': "percent",
                            'include' : True if self.instance_id.default_tax_type == "include" else False,
                            'remote_id': tax_id,
                        }]
        return False

    def get_purchase_orders(self, zoho, **kwargs) -> list:
        instance_id = self.instance_id
        data_list =[]
        if kwargs.get("from_cron"):
            purchase_orders = zoho.get("purchaseorders", params={
                                "page": kwargs.get("page"),
                                'per_page':kwargs.get('per_page'),
                                'date_start' : instance_id.import_purchase_order_date.strftime('%Y-%m-%d'),
                                'sort_column': 'date'
                              })
        else:
            purchase_orders = zoho.get("purchaseorders", params=kwargs)
        purchase_orders_json = purchase_orders.get("json")
        if not purchase_orders_json:
            kwargs.update({'message': f"Error in Getting Purchase Orders: {purchase_orders.get('f_error')}"})
        else:
            data_list = list(map(self._get_purchase_order, purchase_orders_json.get("purchaseorders")))
        if purchase_orders_json and not purchase_orders_json.get('page_context',{}).get('has_more_page'):
            kwargs.update(stop=True)
        if data_list and data_list[0].get('date_order') and kwargs.get("from_cron"):
            instance_id.import_purchase_order_date = data_list[0].get('date_order')
        return kwargs, data_list
    
    def _get_purchase_order(self, order) -> dict:   
        vals = {}
        instance_id = self.instance_id
        zoho = instance_id.get_zohoapi_object()
        order = zoho.get('purchaseorders', resource_id = order.get('purchaseorder_id'))
        order_json = order.get('json',{}).get('purchaseorder')
        if order_json:
            remote_po_states = {
                'draft': 'draft',
                'open': 'purchase',
                'billed': 'done',
                'cancelled': 'cancel',
            }
            vals = {
                'instance_id':instance_id.id,
                'remote_id':order_json.get("purchaseorder_id"),
                'zoho_doc_number': order_json.get("reference_number"),
                'origin':order_json.get("purchaseorder_number"),
                'partner_id': order_json.get('vendor_id'),
                'date_order': order_json.get('date'),
                'date_planned': order_json.get('delivery_date'),
                'state':remote_po_states.get(order_json.get('status')),
                'currency_code':order_json.get('currency_code'),
            }
            order_line = self._create_purchase_order_lines(order_json.get('discount'), order_json.get("is_discount_before_tax"), order_json.get("line_items"))
            if order_json.get('discount_amount'):
                if type(order_json.get('discount')) != str:
                    tax_list = []
                    for tax_line in order_line:
                        if tax_line.get('line_taxes'):
                            tax_list.extend(tax_line.get('line_taxes'))
                    discount_line = self._get_purchase_discount_line_item(order_json.get('discount_amount'))
                    if order_json.get("is_discount_before_tax"):
                        discount_line.update({'line_taxes':tax_list})
                    order_line.append(discount_line)
            vals["order_lines"] = order_line
        return vals

    def _create_purchase_order_lines(self, discount, discount_before_tax, line_items: list) -> list:
        data_list = []
        discount_line = False
        for data in line_items:
            line_vals = self._get_purchase_order_line_item(data)
            data_list.append(line_vals)
            if discount:
                if type(discount) == str:
                    discount_percent = float(discount.replace('%',''))
                    discount_amount = (discount_percent * data.get('rate')) / 100
                    discount_line = self._get_purchase_discount_line_item(discount_amount)
                    discount_line.update({'line_taxes':line_vals.get('line_taxes')})
            if data.get('discount'):
                if type(data.get('discount')) == str:
                    discount_percent = float((data.get('discount')).replace('%', ''))
                    discount_amount = (discount_percent * data.get('rate')) / 100
                    discount_line = self._get_purchase_discount_line_item(discount_amount)
                else:
                    discount_line = self._get_purchase_discount_line_item(data.get('discount_amount'))
                if discount_before_tax:
                    discount_line.update({'line_taxes':line_vals.get('line_taxes')})
            if discount_line:
                data_list.append(discount_line)
        return data_list
            
    
    def _get_purchase_order_line_item(self, item: dict) -> tuple:
        return dict(
            product_id=item.get("item_id"),
            product_qty=item.get("quantity"),
            price_unit=item.get("rate"),
            name=item.get("description"),
            line_taxes=self.get_order_line_taxes(item.get('tax_id'))
        )

    def _get_purchase_discount_line_item(self, discount_amount):
        return dict(
                name= "Discount",
                product_qty = 1,
                price_unit= -float(discount_amount or 0),
                line_source = 'discount',
        )

    def get_invoices(self, zoho, **kwargs)->list:
        instance_id = self.instance_id
        invoice_list = []
        params = {
            'page': kwargs.get('page'),
            'per_page': kwargs.get('per_page'),
        }
        if kwargs.get('move_type', False):
            if kwargs.get('move_type') == 'out_invoice':
                resource = "invoices"
                cron_date_field = 'import_invoice_date'
                import_cron_date = instance_id.import_invoice_date
            else:
                resource = "bills"
                cron_date_field = 'import_bill_date'
                import_cron_date = instance_id.import_bill_date
            if kwargs.get('from_cron') and import_cron_date:
                params.update({
                    'date_start':import_cron_date.strftime('%Y-%m-%d'), 
                    'sort_column': 'date'})
            response = zoho.get(resource, params=params)
            if response.get('json'):
                data_list = response.get('json').get(resource)
                if resource == 'invoices':
                    for data in data_list:
                        inv_id = data.get('invoice_id')
                        invoice_datalist = zoho.get(f'invoices/{inv_id}')
                        if not invoice_datalist.get("json"):
                            _logger.info("Error in Getting Invoices : %r", invoice_datalist.get("f_error"))
                        else:
                            invoice_data = self._get_invoice(invoice_datalist.get("json",{}).get("invoice"))
                            invoice_list.append(invoice_data)
                else:
                    for data in data_list:
                        inv_id = data.get('bill_id')
                        invoice_datalist = zoho.get(f'bills/{inv_id}')
                        if not invoice_datalist.get("json"):
                            _logger.info("Error in Getting Invoices : %r",
                                        invoice_datalist.get("f_error"))
                        else:
                            invoice_data = self._get_invoice(invoice_datalist.get("json",{}).get("bill"))
                            invoice_list.append(invoice_data)
            if invoice_list and invoice_list[0].get('invoice_date') and kwargs.get('from_cron'):
                self.instance_id.write({cron_date_field: invoice_list[0].get('invoice_date')})
        return kwargs, invoice_list

    def _get_invoice(self, invoice)->dict:
        if invoice.get('invoice_id'):
            zoho_id = invoice.get('invoice_id')
        else:
            zoho_id = invoice.get('bill_id')
        vals = {
            'instance_id':self.instance_id.id,
            'remote_id': zoho_id,
            'partner_id': invoice.get('vendor_id') if invoice.get('bill_id') else invoice.get('customer_id'),
            'invoice_date': invoice.get("date", ""),
            'invoice_date_due': invoice.get("due_date", ''),
            'ref': invoice.get("invoice_number"),
            'zoho_doc_number': invoice.get('reference_number')
        }
        if invoice.get('bill_id'):
            vals.update({'type': 'in_invoice'})
        else:
            vals.update({'type': 'out_invoice'})
        invoice_line_ids = self._get_invoice_line_items(invoice.get('discount_type'), invoice.get('discount'), invoice.get('is_inclusive_tax'), invoice.get("line_items",[]))
        if invoice.get('discount_type') == 'entity_level' and invoice.get('discount_amount'):
            if type(invoice.get('discount')) != str:
                discount_line = self.get_invoice_discount_line(invoice, invoice_line_ids)
                invoice_line_ids.append(discount_line)
        vals["invoice_lines"] = invoice_line_ids
        return vals

    def get_credit_notes(self, zoho, **kwargs):
        instance_id = self.instance_id
        credit_note_list = []
        params = kwargs
        if kwargs.get('move_type', False) and kwargs.get('move_type') == 'in_refund':
            resource = "vendorcredits"
            cron_date_field = 'import_refund_date'
            cron_date = instance_id.import_refund_date
        else:
            resource = "creditnotes"
            cron_date_field = 'import_credit_notes_date'
            cron_date = instance_id.import_credit_notes_date
        if cron_date and kwargs.get('from_cron'):
            params.update({
                'date_start':cron_date.strftime('%Y-%m-%d'), 
                'sort_column': 'date'})
            params.update({'last_modified_time': cron_date.replace(tzinfo=pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')})
        credit_data = zoho.get(resource, params=kwargs)
        if credit_data.get('json'):
            if resource == "vendorcredits":
                id_field_name = 'vendor_credit_id'
                entity_key = "vendor_credit"
                credit_ids = credit_data.get('json').get('vendor_credits', [])
            else:
                id_field_name = 'creditnote_id'
                entity_key = "creditnote"
                credit_ids = credit_data.get('json').get('creditnotes', [])
            for credit in credit_ids:
                resource_id = credit.get(id_field_name)
                final_data = zoho.get(resource + f'/{resource_id}')
                if final_data.get("json"):
                    credit_note_list.append(self._get_credit_note(final_data.get("json").get(entity_key)))
            if credit_note_list and credit_note_list[0].get('invoice_date') and kwargs.get('from_cron'):
                self.instance_id.write({cron_date_field: credit_note_list[0].get('invoice_date')})
        return kwargs,credit_note_list

    def _get_credit_note(self, invoice):
        if invoice.get('vendor_credit_id'):
            zoho_id = invoice.get('vendor_credit_id')
        else:
            zoho_id = invoice.get('creditnote_id')
        vals = {
            'instance_id': self.instance_id.id,
            'remote_id': zoho_id,
            'partner_id': invoice.get("vendor_id") if invoice.get('vendor_credit_id') else invoice.get("customer_id"),
            'invoice_date': invoice.get("date", ""),
            'zoho_doc_number': invoice.get('reference_number'),
            'currency_code': invoice.get('currency_code'),
        }
        if invoice.get('vendor_credit_id'):
            vals.update({'type': 'in_refund'})
        else:
            vals.update({'type': 'out_refund'})
        invoice_line_ids = self._get_invoice_line_items(invoice.get('discount_type'), invoice.get('discount'), invoice.get('is_inclusive_tax'), invoice.get("line_items",[]))
        if invoice.get('discount_type') == 'entity_level' and invoice.get('discount_amount'):
            if type(invoice.get('discount')) != str:
                discount_line = self.get_invoice_discount_line(invoice, invoice_line_ids)
                invoice_line_ids.append(discount_line)
        vals["invoice_lines"] = invoice_line_ids
        return vals

    def _get_invoice_line_items(self,  discount_type, discount, is_inclusive_tax, line_items:list)->list:
        data_list = []
        data_list = [self._get_invoice_line_item(line, is_inclusive_tax, discount_type, discount) for line in line_items]
        return data_list
    
    def _get_invoice_line_item(self, item:dict, is_inclusive_tax, discount_type, discount)->tuple:
        discount_amount = False
        item_rate = item.get('rate')
        if discount_type == 'entity_level':
            if discount:
                if type(discount) == str:
                    discount_amount = float(discount.replace('%',''))
        if item.get('discount'):
            if type(item.get('discount')) == str:
                discount_amount = float(item.get('discount').replace('%',''))
            else:
                if is_inclusive_tax:
                    item_exclusive_amount = item_rate/(1+item.get('tax_percentage')/100)
                    discount_amount = (item.get('discount_amount')/item_exclusive_amount)*100
                else:
                    discount_amount = item.get('discount_amount')/item_rate * 100
        return dict(
                product_id = item.get("item_id"),
                product_uom_qty = item.get("quantity"),
                price_unit = item_rate,
                name = item.get("name"),
                account_remote_id = item.get('account_id'),
                line_taxes = self.get_order_line_taxes(item.get('tax_id')),
                discount = discount_amount
            )

    def get_invoice_discount_line(self, invoice_response, lines_data):
        tax_list = []
        if invoice_response.get('is_discount_before_tax'):
            for invoice_line in lines_data:
                if invoice_line.get('line_taxes'):
                    tax_list.extend(invoice_line.get('line_taxes'))
        return {
                "name":"Discount",
                "product_uom_qty": 1,
                "price_unit" : -float(invoice_response.get("discount_amount")),
                "line_source":'discount',
                "line_taxes": tax_list,
            }

    def get_payments(self, zoho, **kwargs)->list:
        instance_id = self.instance_id
        data_list = []
        if kwargs.get('from_cron'):
            payments = zoho.get('customerpayments', params = {
                'page':kwargs.get('page'),
                'per_page':kwargs.get('per_page'),
                'date_start': instance_id.import_payment_date.strftime('%Y-%m-%d'),
                'sort_column': 'date'
            })
        else:
            payments = zoho.get("customerpayments", params=kwargs)
        payments_json = payments.get('json')
        if payments_json:
            data_list = list(map(self._get_payment, payments_json.get("customerpayments")))
            if not payments_json.get('page_context',{}).get('has_more_page'):
                kwargs.update(stop=True)
            if kwargs.get('from_cron') and data_list and data_list[0].get('date'):
                instance_id.import_payment_date = data_list[0].get('date')
        else:
            kwargs.update({'message': f"Error in Getting Payments : {payments.get('f_error')}"})
            _logger.error("Error in Getting Payments : %r", payments.get("f_error"))
        return kwargs, data_list
 
    def _get_payment(self, payment)->dict:
        vals = {}
        instance_id = self.instance_id
        zoho = instance_id.get_zohoapi_object()
        payment = zoho.get('customerpayments', resource_id = payment.get("payment_id"))
        payment_json = payment.get('json',{}).get('payment')
        if payment_json:
            vals = {
                'remote_id':payment_json.get("payment_id"),
                'instance_id':instance_id.id,
                'partner_type' : "customer",
                'partner_id': payment_json.get('customer_id'),
                'amount' : payment_json.get("amount"),
                'ref' : payment_json.get("reference_number",""),
                'date' : payment_json.get("date"),
                'payment_type' :'inbound',
                'invoice_ids': [invoice.get('invoice_id') for invoice in payment_json.get('invoices')]
            }
        return vals

    def get_taxes(self, zoho, **kwargs):
        data_list= []
        taxes = zoho.get('settings/taxes', params={"page":kwargs.get("page")})
        taxes_json = taxes.get('json')
        if not taxes_json:
            err_message = f"Error in Getting Taxes : {taxes.get('f_error')}"
            _logger.error(err_message)
            kwargs.update({'message': err_message})
        else:
            data_list = list(map(self.get_tax, taxes_json.get('taxes')))
        kwargs.update({'stop':True})
        return kwargs, data_list

    def get_tax(self,tax) -> dict:
        return {
            'instance_id':self.instance_id.id,
            'remote_id':tax.get('tax_id'),
            'name':tax.get('tax_name'),
            'amount':tax.get('tax_percentage'),
            'amount_type':'percent',
            'active': True if tax.get('status') == "ACTIVE" else False,
            'price_include':True if self.instance_id.default_tax_type == "include" else False
        }

    def get_journals(self, zoho, **kwargs) -> list:
        data_list = []
        journals = zoho.get('journals', params={"page":kwargs.get("page")})
        if not journals.get('json'):
            err_message = f"Error in Getting Payment Methods : {journals.get('f_error')}"
            _logger.error(err_message)
            kwargs.update({'message': err_message})
        else:
            data_list = list(map(self.get_journal, journals.get('json').get('journals')))
        return kwargs, data_list

    def get_journal(self, journal):
        return {
            'instance_id':self.instance_id.id,
            'remote_id':journal.get('journal_id'),
            'name':journal.get('entry_number'),
        }

    ####################
    # Export Operation #
    ####################

    def post_account(self, zoho, record, **kwargs):
        acc_type = self.get_zoho_account_type(record.account_type)
        exported, zoho_id = False, False
        response = zoho.post("chartofaccounts", json = {
            "account_name": record.name,
            "account_code": record.code,
            "account_type": acc_type,
        })
        if response.get("json"):
            exported = True
            zoho_id = response.get("json").get("chart_of_account").get('account_id')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, kwargs

    def get_zoho_account_type(self, odoo_account_type):
        zoho_account_type = ACCOUNT_OUT.get(odoo_account_type, "bank")
        return zoho_account_type

    def post_customer(self, zoho, record, **kwargs):
        exported, zoho_id = False, False
        vals = self._get_customer_data(record)
        if self.gst_in:
            vals.update({'gst_treatment': 'business_none'}) # overseas/business_gst/business_none/consumer
        response = zoho.post("contacts", json = vals)
        if response.get("json"):
            exported=True
            zoho_id = response.get('json').get('contact').get('contact_id')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, kwargs
    
    def _get_customer_data(self, record):
        contact_type = 'vendor' if record.supplier_rank else 'customer'
        return {
                "contact_name" : record.name,
                "company_name" : record.parent_id.name if record.parent_id else '',
                'website': record.website or '',
                'email':record.email or '',
                'contact_type': contact_type,
                'billing_address':{
                    "attention": record.name or '',
                    "address": record.street or '',
                    "street2": record.street2 or '',
                    "state_code": record.state_id.code or '',
                    "city": record.city or '',
                    "zip": record.zip or '',
                    "country": record.country_id.name,
                    "phone": record.phone or ''
                }
            }
    
    def post_product(self, zoho, record, **kwargs):
        instance_id = self.instance_id
        exported, zoho_id,remote_itemCode = False, False, False
        data = record.read()[0]
        if not data['default_code'] and not instance_id.product_sequence_id:
            raise ZohoProductRequiredParam("SKU(internal_reference) is Required Parameter For Zoho Product. Define Product Default code or Set Product Sequence from Connected Instance Configuration.")
        itemCode = data['default_code'] or instance_id.product_sequence_id.next_by_id()
        response = zoho.post("items", json = {
            'name' : data['name'],
            'sku':itemCode,
            'description' : data['description_sale'] or '',
            'purchase_description' : data['description_purchase'] or '',
            'rate':data['list_price'],
            'purchase_rate':data['standard_price'],
            'product_type' : 'goods' if data['type'] == 'product' else 'service',
            'item_type':'sales_and_purchases' if data['sale_ok'] and data['purchase_ok'] else 'purchases' if data['purchase_ok'] else 'sales'
        })
        if response.get("json"):
            exported = True
            zoho_id = response.get("json").get("item").get("item_id")
            if not data['default_code']:
                remote_itemCode = itemCode
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, remote_itemCode, kwargs
    
    def post_order(self, zoho, record, **kwargs):
        instance_id = self.instance_id
        exported, zoho_id = False, False
        data = record.read()[0]
        customer_id = instance_id.match_customer_mapping(odoo_id = data['partner_id'][0])
        if customer_id:
            customer_id = customer_id.remote_id
        else:
            message = f'Customer {data["partner_id"][1]} is not mapped'
            _logger.error(message)
            kwargs.update({'message': message})
            return exported, zoho_id , kwargs
        vals = {
            'customer_id' : customer_id or '',
            'date' : data['date_order'].strftime("%Y-%m-%d"),
            'reference_number':data['zoho_doc_number'] or '',
            "is_inclusive_tax": False,
            'line_items' : self._get_order_lines(record)
        }
        response = zoho.post("salesorders", json = vals)
        if response.get("json"):
            exported = True
            zoho_id = response.get("json").get("salesorder").get('salesorder_id')
            record.origin = response.get("json").get("salesorder").get('salesorder_number')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, kwargs

    def _get_order_lines(self,record:object)->list:
        return list(map(self._get_order_line, record.order_line))
    
    def _get_order_line(self, order_line:object)->dict:
        remote_id = ''
        tax_remote_id = ''
        tax_exemption_code = 'SALES'
        order_line_data = order_line.read()[0]
        product_id = order_line_data['product_id'][0]
        instance_id = self.instance_id
        match = instance_id.match_product_mapping(odoo_id = product_id)
        if not match:
            raise Exception(f"Product '{order_line_data['product_id'][1]}' is not mapped")
        remote_id = match.remote_id
        if order_line.tax_id:
            tax_mapping_object = instance_id.match_tax_mapping(odoo_id = order_line.tax_id[0].id)
            tax_remote_id = tax_mapping_object.remote_id
            if tax_remote_id:
                tax_remote_id = tax_remote_id
            else:
                _logger.warning(f'Tax {order_line.tax_id[0].name} Mapping Does Not Exist at Zoho End')
        data = dict(
                item_id = remote_id,
                name = order_line_data['product_id'][1],
                quantity = order_line_data['product_uom_qty'],
                rate = order_line_data['price_unit'],
                description = order_line_data['name'],
            )
        if tax_remote_id:
            data.update({'tax_id':tax_remote_id})
        else:
            data.update({'tax_exemption_code':tax_exemption_code})
        if order_line.order_id._name == 'sale.order':
            data.update({'discount': f'{order_line.discount or 0}%',})
        return data
    
    def post_purchase_order(self, zoho, record, **kwargs):
        instance_id = self.instance_id
        exported, zoho_id = False, False
        data = record.read()[0]
        vendor_id = instance_id.match_customer_mapping(odoo_id = data['partner_id'][0])
        if vendor_id:
            vendor_id = vendor_id.remote_id
        else:
            message = f'Vendor {data["partner_id"][1]} is not mapped'
            _logger.error(message)
            kwargs.update({'message': message})
            return exported, zoho_id , kwargs
        vals = {
            'vendor_id' : vendor_id or '',
            'date' : data['date_order'].strftime("%Y-%m-%d"),
            'reference_number':data['zoho_doc_number'] or '',
            "is_inclusive_tax": False,
            'line_items' : self._get_purchase_order_lines(record)
        }
        response = zoho.post("purchaseorders", json = vals)
        if response.get("json"):
            exported = True
            zoho_id = response.get("json").get("purchaseorder").get('purchaseorder_id')
            record.origin = response.get("json").get("purchaseorder").get('purchaseorder_number')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, kwargs

    def _get_purchase_order_lines(self, record:object)->list:
        return list(map(self._get_purchase_order_line, record.order_line))
        
    def _get_purchase_order_line(self, order_line:object)->dict:
        remote_id = ''
        tax_remote_id = ''
        tax_exemption_code = 'PURCHASE'
        order_line_data = order_line.read()[0]
        instance_id = self.instance_id
        match = instance_id.match_product_mapping(odoo_id = order_line_data['product_id'][0])
        if not match:
            raise Exception(f"Product '{order_line_data['product_id'][1]}' is not mapped")
        remote_id = match.remote_id
        if order_line.taxes_id:
            tax_mapping_object = instance_id.match_tax_mapping(odoo_id = order_line.taxes_id[0].id)
            tax_remote_id = tax_mapping_object.remote_id
            if tax_remote_id:
                tax_remote_id = tax_remote_id
            else:
                _logger.warning(f'Tax {order_line.taxes_id[0].name} Mapping Does Not Exist at Zoho End')
        data = dict(
                item_id = remote_id,
                name = order_line_data['product_id'][1],
                quantity = order_line_data['product_qty'],
                rate = order_line_data['price_unit'],
                description = order_line_data['name'],
            )
        
        if tax_remote_id:
            data.update({'tax_id':tax_remote_id})
        else:
            data.update({'tax_exemption_code':tax_exemption_code})
        return data

    def post_tax(self, tax_id, **kwargs):
        if tax_id:
            tax_id = tax_id[0]
            instance_id = self.instance_id
            mapping = instance_id.match_tax_mapping(tax_id.id)
            if  mapping:
                return mapping.remote_id
            zoho = zoho = self.instance_id.get_zohoapi_object()
            response = zoho.post("settings/taxes", json = {
                "tax_name": tax_id.name,
                "tax_percentage": tax_id.amount,
            })
            if response.get('json'):
                instance_id.create_tax_mapping(tax_id, response.get('json').get('tax').get('tax_id'), "export")
                return response.get('json').get('tax').get('tax_id')
            else:
                kwargs.update({'message': response.get('f_error')})
        return False

    def post_invoice(self, zoho, record, **kwargs):
        exported, zoho_id = False, False
        data = record.read()[0]
        instance_id = self.instance_id
        customer_id = instance_id.match_customer_mapping(odoo_id = data['partner_id'][0])
        if customer_id:
            partner_remote_id = customer_id.remote_id
        else:
            message = f'Partner {data["partner_id"][1]} is not mapped'
            kwargs.update({'message': message})
            return exported, zoho_id, kwargs
        json = {
            'date': data['invoice_date'].strftime("%Y-%m-%d") if data['invoice_date'] else '',
            'due_date': data['invoice_date_due'].strftime("%Y-%m-%d") if data['invoice_date_due'] else '',
            'reference_number': data['zoho_doc_number'] or '',
            "gst_treatment": "business_gst",
            "reference_invoice_type": "registered", # registered/unregistered/consumer/overseas
            'is_draft': True,
            'status': 'draft',
            'is_inclusive_tax':True if self.instance_id.default_tax_type == "include" else False,
            'discount_type':'item_level',
            'line_items':self._get_invoice_lines(record)
        }
        if data['move_type'] == "out_invoice":
            resource = "invoices"
            json.update({'customer_id': partner_remote_id or ''})
        else:
            resource = "bills"
            json.update({'vendor_id':partner_remote_id or '', 
                        'bill_number': record.name if record.state == 'posted' else record.display_name
                        })
        response = zoho.post(resource, json=json)
        if response.get('json'):
            exported=True
            if response.get('json').get('invoice'):
                zoho_id = response.get('json').get('invoice').get('invoice_id')
                invoice_number = response.get('json').get('invoice').get('invoice_number')
            else:
                zoho_id = response.get('json').get('bill').get('bill_id')
                invoice_number = response.get('json').get('bill').get('bill_number')
            if invoice_number and not data['ref']:
                record.ref = invoice_number
            if zoho_id and data.get('state') == 'posted':
                self.sent_invoice_status(zoho, f'{resource}/{zoho_id}')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported,zoho_id, kwargs
    
    def _get_invoice_lines(self, record:object)->list:
        return list(map(self._get_invoice_line, record.invoice_line_ids))
    
    def _get_invoice_line(self, invoice_line:object)->dict:
        remote_id =''
        data = invoice_line.read()[0]
        product_id = invoice_line.product_id
        instance_id = self.instance_id
        account_remote_id=''
        tax_remote_id = ''
        tax_exemption_code = 'INVOICE'
        account_id = instance_id.match_account_mapping(odoo_id = data['account_id'][0])
        if account_id:
            account_remote_id = account_id.remote_id
        else:
            _logger.warning(f'Account {data["account_id"][1]} mapping does not exist')  
        if invoice_line.tax_ids:
            tax_mapping_object = instance_id.match_tax_mapping(odoo_id = invoice_line.tax_ids[0].id)
            tax_remote_id = tax_mapping_object.remote_id
            if tax_remote_id:
                tax_remote_id = tax_remote_id
            else:
                _logger.warning(f'Tax {invoice_line.tax_ids[0].name} Mapping Does Not Exist at Zoho End')
        match = instance_id.match_product_mapping(odoo_id = product_id)
        if not match:
            raise Exception(f"Product '{product_id.name}' is not mapped")
        remote_id = match.remote_id
        final_data = dict(
                item_id = remote_id,
                name = product_id.name or '',
                description = product_id.description or '',
                quantity = data['quantity'],
                account_id = account_remote_id or '',
                rate = data['price_unit'],
            )
        if data['discount']:
            final_data.update({'discount':f'{data["discount"]}%'})
        if tax_remote_id:
            final_data.update({'tax_id':tax_remote_id})
        else:
            _logger.warning(f'Tax Mapping Does not exist')
            final_data.update({'tax_exemption_code':tax_exemption_code})
        return final_data

    def post_credit_note(self, zoho, record, **kwargs):
        exported, zoho_id = False, False
        data = record.read()[0]
        instance_id = self.instance_id
        customer_id = instance_id.match_customer_mapping(odoo_id = data['partner_id'][0])
        if customer_id:
            partner_remote_id = customer_id.remote_id
        else:
            message = f'Vendor {data["partner_id"][1]} is not mapped'
            kwargs.update({'message': message})
            return exported, zoho_id , kwargs
        status = False
        if data['state'] == 'draft':
            status = True
        json = {
            'date': data['invoice_date'].strftime("%Y-%m-%d") if data['invoice_date'] else '',
            'reference_number': data['zoho_doc_number'] or '',
            "gst_treatment":"business_gst",
            "reference_invoice_type": "registered", # registered/unregistered/consumer/overseas
            'is_draft': status,
            'is_inclusive_tax':True if self.instance_id.default_tax_type == "include" else False,
            'line_items':self._get_invoice_lines(record)
        }
        if data['move_type'] == "out_refund":
            resource = "creditnotes"
            json.update({'customer_id': partner_remote_id or ''})
        else:
            resource = "vendorcredits"
            json.update({'vendor_id': partner_remote_id or '', 
                        # 'vendor_credit_number': record.name if record.state == 'posted' else record.display_name
                        })
        response = zoho.post(resource, json=json)
        if response.get('json'):
            exported=True
            if response.get('json').get('creditnote'):
                zoho_id = response.get('json').get('creditnote').get('creditnote_id')
                note_number = response.get('json').get('creditnote').get('creditnote_number')
            else:
                zoho_id = response.get('json').get('vendor_credit').get('vendor_credit_id')
                note_number = response.get('json').get('vendor_credit').get('vendor_credit_number')
            if note_number and not data['ref']:
                record.ref = note_number
            if zoho_id and data.get('state') == 'posted':
                self.sent_invoice_status(zoho, f'{resource}/{zoho_id}')
        else:
            kwargs.update({'message':response.get('f_error')})
        return exported,zoho_id, kwargs

    def post_payment(self, zoho, record, **kwargs):
        exported, zoho_id, invoice_list = False, False, []
        reconciled_invoice_ids = record.reconciled_invoice_ids
        remote_partner_id = False
        instance_id = self.instance_id
        partner_mapping = instance_id.match_customer_mapping(odoo_id = record.partner_id.id)
        if partner_mapping:
            remote_partner_id = partner_mapping.remote_id
        match = instance_id.match_invoice_mapping
        for invoice_id in reconciled_invoice_ids:
            invoice_id = match(odoo_id = invoice_id.id)
            if invoice_id:
                invoice_list.append({'invoice_id' : invoice_id.remote_id})
        response = zoho.post("customerpayments", json = {
            'customer_id': remote_partner_id,
            'payment_mode': 'banktransfer',
            'amount':record.amount,
            'invoices': invoice_list,
            'date' : record.date.strftime("%Y-%m-%d"),
            'amount_applied' : record.amount,
            'reference_number': record.ref or '',
        })
        if response.get("json"):
            exported = True
            zoho_id = response.get("json").get("payment").get('payment_id')
        else:
            kwargs.update({'message': response.get('f_error')})
        return exported, zoho_id, kwargs

    def sent_invoice_status(self, zoho, resource):
        if 'invoices' in resource:
            zoho.post(f"{resource}/status/sent")
            # zoho.post(f"{resource}/approve")
        # else:
        #     zoho.post(f"{resource}/status/open")
