# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import requests
from urllib.parse import urlencode
from odoo import models, fields, api
from ...zoho_api import ZohoApi
from ...ZohoTransactions import ZohoTransactions

Organizations = []

class ZohoConfiguration(models.Model):
    _inherit = 'omas'

    user_domain = fields.Selection(string='Domain', selection=[('com', 'com'), ('in', 'in'),('eu','eu'),('com.au','com.au')],
                    help="User Belongs to which data center of zoho books accordingly need to set the Domain...")

    def get_zoho_organization_ids(self):
        self.refresh_access_token()
        organization_list = []
        organizations = requests.get(f'https://books.zoho.{self.user_domain}/api/v3/organizations', headers={
            'Authorization':f'Zoho-oauthtoken {self.access_token}',
        })
        organization_json = organizations.json()
        if organizations.ok:
            organization_list = [{
                'remote_id':organization.get('organization_id'),
                'name':organization.get('name')
                    } for organization in organization_json.get('organizations',[])]
            message = f"<span class='text-success'>Organizations Fetched Successfully for Zoho.</span>"
        else:
            message = f'Error in getting Organizations : {organization_json.get("Detail")}'
        return organization_list, message

    @api.model
    def get_instances(self)->list:
        res = super(ZohoConfiguration, self).get_instances()
        res.append(('zoho', 'Zoho'))
        return res

    def connect_zoho(self)->dict:
        scope = 'ZohoBooks.fullaccess.READ,ZohoBooks.fullaccess.UPDATE,ZohoBooks.fullaccess.CREATE'
        url = "?".join(
            [f"https://accounts.zoho.{self.user_domain}/oauth/v2/auth", urlencode({
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "access_type":"offline",
            "prompt":"consent",
            "state": "zohoodooconnector"
        })])
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target":"self"
        }

    def disconnect_zoho(self)->bool:
        refresh_token = self.refresh_token
        res = requests.post(f'https://accounts.zoho.{self.user_domain}/oauth/v2/token/revoke',params={'token':refresh_token})
        if res.status_code in [200, 204]:
            self.organization_id = False
            return True

    def create_zoho_online_connection(self)->None:
        status = True
        url = "?".join(
            [f"https://accounts.zoho.{self.user_domain}/oauth/v2/token", urlencode({
                "code":self.authorization_token,
                "client_id":self.client_id,
                "client_secret":self.client_secret,
                "redirect_uri":self.redirect_uri,
                "grant_type":'authorization_code',
                "scope": 'ZohoBooks.fullaccess.READ,ZohoBooks.fullaccess.UPDATE,ZohoBooks.fullaccess.CREATE'
        })])
        response = requests.post(url)
        if response.status_code in [200, 201]:
            res = response.json()
            if response.json().get('error'):
                status = False
            return {
                "is_connected": status,
                "access_token": res.get("access_token"),
                "refresh_token": res.get("refresh_token"),
            }
    
    def refresh_zoho_access_token(self)->None:
        url = "?".join(
            [f"https://accounts.zoho.{self.user_domain}/oauth/v2/token", urlencode({
                "refresh_token":self.refresh_token,
                "client_id":self.client_id,
                "client_secret":self.client_secret,
                "redirect_uri":self.redirect_uri,
                "grant_type":'refresh_token',
        })])
        response = requests.post(url)
        if response.status_code in [200, 201]:
            res = response.json()
            return {
                "is_connected": True,
                "access_token": res.get("access_token"),
                "refresh_token": res.get("refresh_token"),
            }
    
    def zoho_unavailable_features(self):
        message = """
            <ul>
                <li>Fixed Discount at Zoho can make difference in Total Amount in Odoo after import.</li>
                <li>Invoice Number, Credit Note Number should be set as auto generated at the Zoho.</li>
                <li>The Feature Category Mappings, Payment Term Mappings and Shipping Mappings not used in Zoho Connector.</li>
            </ul>
            """     
        return message

    def zoho_available_features(self):
        features = self._all_available_features_list()
        if 'import_customer_cron' in features:
            features.remove('import_customer_cron')
        if 'import_product_cron' in features:
            features.remove('import_product_cron')
        return features

    def get_zohoapi_object(self)->object:
        return ZohoApi(self.access_token, self.organization_id.remote_id, debug=self.debug, domain=self.user_domain)

    def import_zoho_accounts(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_accounts(zoho, **kwargs)

    def import_zoho_customers(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_customers(zoho, **kwargs)

    def import_zoho_templates(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_products(zoho, **kwargs)

    def import_zoho_orders(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_orders(zoho, **kwargs)
    
    def import_zoho_purchase_orders(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_purchase_orders(zoho, **kwargs)
    
    def import_zoho_invoices(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_invoices(zoho, **kwargs)

    def import_zoho_payments(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_payments(zoho, **kwargs)
    
    def import_zoho_payment_methods(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_journals(zoho, **kwargs)
    
    def import_zoho_taxes(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_taxes(zoho, **kwargs)

    def import_zoho_credit_notes(self, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).get_credit_notes(zoho, **kwargs)
    
    def export_zoho_accounts(self, record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_account(zoho, record, **kwargs)

    def export_zoho_customers(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_customer(zoho, record, **kwargs)

    def export_zoho_templates(self, record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_product(zoho, record, **kwargs)

    def export_zoho_orders(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_order(zoho, record, **kwargs)

    def export_zoho_purchase_orders(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_purchase_order(zoho, record, **kwargs)
    
    def export_zoho_invoices(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_invoice(zoho, record, **kwargs)

    def export_zoho_payments(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_payment(zoho, record, **kwargs)
    
    def export_zoho_credit_notes(self,record, **kwargs):
        self.refresh_access_token()
        zoho = self.get_zohoapi_object()
        return ZohoTransactions(self).post_credit_note(zoho, record, **kwargs)
    
    def zoho_import_order_cron(self):
        return self.import_entities('orders', from_cron = True)
    
    def zoho_import_invoice_cron(self, **kw):
        return self.import_entities('invoices', from_cron = True, **kw)
    
    def zoho_import_payment_cron(self):
        return self.import_entities('payments', from_cron = True)

    def zoho_import_credit_notes_cron(self,**kw):
        return self.import_entities('credit_notes', from_cron = True, **kw)

    def zoho_import_purchase_order_cron(self):
        return self.import_entities('purchase_orders', from_cron = True)
