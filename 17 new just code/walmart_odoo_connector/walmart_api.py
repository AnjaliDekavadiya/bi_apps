# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

import os
import subprocess
import requests
import base64
import uuid
import json
from html import escape

from urllib import parse as urlparse
from pprint import pprint
from datetime import datetime, timedelta
from lxml import etree
from pathlib import Path
import logging
_logger = logging.getLogger(__name__)

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
from odoo.tools.misc import file_path

S_BASE_URL = "https://sandbox.walmartapis.com/v3/"
P_BASE_URL = "https://marketplace.walmartapis.com/v3/"

MARTKETPLACES_URL = {
    "US": {"production": P_BASE_URL, "sandbox": S_BASE_URL},
    "CA": {"production": P_BASE_URL+"ca", "sandbox": S_BASE_URL+"ca"},
    "MX": {"production": P_BASE_URL, "sandbox": S_BASE_URL},
}
MARTKETPLACE_MAP = {
    "US": "WALMART_US",
    "CA": "WALMART_CA",
    "MX": "WALMART_MEXICO",
    "UK": "ASDA_GM"
}
WalmartCancellationReasonMapping = {
    "1": "CUSTOMER_REQUESTED_SELLER_TO_CANCEL",
    "2": "SELLER_CANCEL_OUT_OF_STOCK",
    "3": "SELLER_CANCEL_CUSTOMER_DUPLICATE_ORDER",
    "4": "SELLER_CANCEL_CUSTOMER_CHANGE_ORDER",
    "5": "SELLER_CANCEL_CUSTOMER_INCORRECT_ADDRESS",
    "6": "SELLER_CANCEL_FRAUD_STOP_SHIPMENT",
    "7": "SELLER_CANCEL_PRICING_ERROR",
}
ProductType = {
    "wk_isbn": "ISBN",
    "wk_upc": "UPC",
    "wk_ean": "EAN",
}

class WalmartConnect:

    def __init__(self, client_id, client_secret, channel_id=None, client_token=None, channel_type=None, marketplace="US", sandbox=False, production=False, env=None):
        self.client_id = client_id or channel_id.walmart_client_id
        self.client_secret = client_secret or channel_id.walmart_client_secret
        self.client_token = client_token
        self.channel_id = channel_id
        self.channel_type = channel_type
        self.marketplace = marketplace
        self.base_url = production and MARTKETPLACES_URL[marketplace][
            "production"] or sandbox and MARTKETPLACES_URL[marketplace]["sandbox"]
        self.production = production
        self.sandbox = sandbox
        self.env = env or channel_id.env

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        del self

    def updateTemplateMapping(self):
        channel_id = self.channel_id
        in_active_template_mappings = self.env["channel.template.mappings"].search(
            [('active', '=', False), ('channel_id', '=', channel_id.id)])
        in_active_product_mappings = self.env["channel.template.mappings"].search(
            [('active', '=', False), ('channel_id', '=', channel_id.id)])

        feed_ids = in_active_template_mappings.mapped("store_product_id")
        for feed in feed_ids:
            result = self._call_feeds_api(feed, params={"includeDetails":"true"})
            if result["data"]:
                products_in_feed = result["data"].get(
                    "itemDetails", {}).get("itemIngestionStatus")
                if products_in_feed:
                    feed_match_tmp = in_active_template_mappings.filtered(
                        lambda map: map.store_product_id == feed)
                    feed_match_var = in_active_product_mappings.filtered(
                        lambda map: map.store_product_id == feed)
                    need_to_del = []
                    for feed_prod, temp_prod, temp_variant in zip(products_in_feed, feed_match_tmp, feed_match_var):
                        # in_active_product_mappings.search()
                        if not feed_prod["ingestionErrors"]:
                            if feed_prod["sku"] == temp_prod.default_code and feed_prod["wpid"]:
                                temp_prod.active = True
                                temp_prod.store_product_id = feed_prod["wpid"]
                                temp_variant.store_product_id = feed_prod["wpid"]
                            else:
                                need_to_del.append(temp_prod)
                                need_to_del.append(temp_variant)
                    for rec in need_to_del:
                        rec.unlink()

    def setHeaderAsPerMarketplace(self, request_url, method, **extra_header):
        if self.marketplace == "CA":
            jar = f'{os.path.dirname(os.path.abspath(__file__))}{os.sep}walmart.jar'
            try:
                subprocess.call(
                    [
                        'java', '-jar', jar, 'DigitalSignatureUtil',
                        request_url, self.client_id, self.client_secret, 'GET',
                        'response'
                    ]
                )
            except FileNotFoundError as e:
                subprocess.call(
					[
						f'''{file_path('walmart_odoo_connector')}/openlogic-openjdk-jre-8u292-b10-linux-x64/bin/java''',
						'-jar', jar, 'DigitalSignatureUtil',
						request_url, self.client_id, self.client_secret, 'GET',
						'response'
					]
				)
            else:
                try:
                    with open('response') as f:
                        for line in f.read().split('\n'):
                            key, value = line.split(':')
                            extra_header[key] = value
                except FileNotFoundError:
                    raise UserError('''JAR dependency not found in module. Please add the jar file:
                    Download from <b>https://developer.walmart.com/image/asdp/ca-jar/digitalSignatureUtil-1.0.0.jar<b> and rename it as walmart.jar and add inside module (<i>walmart_odoo_connector</i>).
                    ''')
                os.remove('response')
                extra_header.update({
                    "WM_CONSUMER.ID": self.client_id,
                    "WM_CONSUMER.CHANNEL.TYPE": self.channel_type,
                    "WM_TENANT_ID": "Walmart_CA",
                    "WM_LOCALE_ID": "en_CA", #its default but passing explicitly
                })
        elif self.marketplace in ["US", "MX"]:
            temp_key = f"{self.client_id}:{self.client_secret}"
            if self.channel_type:
                extra_header["WM_CONSUMER.CHANNEL.TYPE"] = self.channel_type
            if self.client_token:
                extra_header["WM_SEC.ACCESS_TOKEN"] = self.client_token
            extra_header.update({
                "Authorization": "Basic "+base64.b64encode(bytes(temp_key, encoding="ascii")).decode("utf-8"),
                "Host": "marketplace.walmartapis.com" if self.production else "sandbox.walmartapis.com",
                "WM_MARKET": self.marketplace
            })
        return extra_header

    def getToken(self, **kwargs):
        post = "grant_type=client_credentials"

        tokenInfo = dict(access_token="")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = self.getResponse('token', "post", headers, post, **kwargs)
        response_data = response["data"]
        if response_data:
            tokenInfo["access_token"] = response_data["access_token"]
        if "error" in response:
            tokenInfo["error"] = response["error"]
        return tokenInfo

    def checkTokenExpiry(self):
        result = self.getResponse("token/detail")
        if "error" in result:
            result = self.getToken()
            if "access_token" in result:
                self.channel_id.walmart_access_token = self.client_token = result["access_token"]
        else:
            result["access_token"] = self.channel_id.walmart_access_token
        return result

    def getResponse(self, resource_url, method="get", extra_header={}, post_data={}, **kwargs):
        result = dict(data=[])
        with requests.Session() as s:
            response = False
            request_url = self.base_url + resource_url
            basic_headers = {
                "WM_SVC.NAME": "Walmart Martketplace",
                "WM_QOS.CORRELATION_ID": uuid.uuid4().hex,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            other_details = {'request_url': request_url, 'method': method, **kwargs}
            try:
                extra_header = self.setHeaderAsPerMarketplace(**other_details, **extra_header)
                basic_headers.update(extra_header)
                if method == "get":
                    response = s.get(request_url, headers=basic_headers)
                if method == "post":
                    response = s.post(
                        request_url, headers=basic_headers, data=post_data)
                if method == "put":
                    response = s.put(
                        request_url, headers=basic_headers, data=post_data)
            except requests.exceptions.ConnectionError as e:
                result["error"] = f"{e.args[0]}"
            except ModuleNotFoundError as e:
                result["error"] = """Python dependency for Walmart module not found : \n
                        ~~ Please install pycryptodome using: pip install pycryptodome ~~~
                    """
            except Exception as e:
                result["error"] = f"{e.args[0]}"
            else:
                if response.status_code in [200, 201]:
                    try:
                        result["data"] = response.json()
                    except json.JSONDecodeError as e:
                        from xml.dom import minidom
                        result["data"] = minidom.parseString(
                            response.text).toprettyxml(indent="\t")
                else:
                    try:
                        response.json()
                    except json.JSONDecodeError as e:
                        result["error"] = response.reason
                    else:
                        if "error" in response.json():
                            api_resp = response.json()

                            if isinstance(api_resp["error"], list):
                                try:
                                    result["error"] = api_resp["error"][0]["description"]
                                except:
                                    result["error"] = True
                            else:
                                result["error"] = api_resp.get(
                                    "error_description", "") or api_resp.get("error") or True
        return result

    # Import Operation

    def _parse_category_feed(self, category_data):
        parent_store_id = category_data["category"].replace(
            ' ', '').replace('&', 'And')
        if ("Animal" not in parent_store_id and "Health" not in parent_store_id and
            "Baby" not in parent_store_id and "Electronics" not in parent_store_id and
                "Home" not in parent_store_id):
            parent_store_id += "Category"
            if "Other" in parent_store_id:
                parent_store_id = "OtherCategory"

        feed = [{
            "channel_id": category_data["channel_id"],
            "name": category_data["category"],
            "store_id": parent_store_id
        }]
        sub_categories = category_data.get("subcategory")
        CategoryFeed = self.env["category.feed"]

        if sub_categories:
            for sub_categ in sub_categories:
                sub_categ_id = sub_categ["subCategoryName"].replace(
                    ' ', '').replace(',', '').replace('&', 'And')
                if parent_store_id == "Baby":
                    if "Other" in sub_categ_id:
                        sub_categ_id = "BabyOther"
                    elif "Transport" in sub_categ_id:
                        sub_categ_id = "ChildCarSeats"
                elif parent_store_id == "Animal":
                    if "Other" in sub_categ_id:
                        sub_categ_id = "AnimalEverythingElse"
                elif parent_store_id == "HealthAndBeauty":
                    if "Medical" in sub_categ_id:
                        sub_categ_id = "MedicalAids"
                    elif "Personal" in sub_categ_id:
                        sub_categ_id = "PersonalCare"
                elif parent_store_id == "Home":
                    if "Other" in sub_categ_id:
                        sub_categ_id = "HomeOther"

                sub_categ_feed = {
                    "channel_id": category_data["channel_id"],
                    "name": sub_categ["subCategoryName"],
                    "store_id": sub_categ_id,
                    "parent_id": parent_store_id,
                    "leaf_category": True
                }
                feed.append(sub_categ_feed)

        return feed

    def _read_or_write_file_from_path(self, path, mode='r'):
        '''
            It will read the file/files from the path
            return generator Element Tree
        '''
        path_obj = Path(file_path('walmart_odoo_connector', path))
        if path_obj.is_dir():
            for xsd in path_obj.iterdir():
                with xsd.open(encoding='utf-8', mode=mode) as file:
                    if mode in ['r', 'r+']:
                        yield etree.parse(file), file
                    else:
                        yield file
        else:
            with path_obj.open(encoding='utf-8', mode=mode) as file:
                    if mode in ['r', 'r+']:
                        yield etree.parse(file), file
                    else:
                        yield path_obj

    @staticmethod
    def _generate_required_odoo_tmpl_fields(model, field_name, field_label,
            field_type='char', field_help=''):
        '''
            @field_name : <type str> starting with 'x_' as custom fields
            @field_label: <type str>
            @field_type:  <type str> eg char, float, int
            @field_help:  <type str>
        '''
        if not model.env['ir.model.fields'].search([
            ('name','=',field_name),
            ('model_id','=', model.id),
        ]):
            rec = model.env['ir.model.fields'].create({
                'name': field_name,
                'field_description': field_label,
                'model_id': model.id,
                'ttype': field_type,
                'help': field_help,
            })
            return rec

    @staticmethod
    def _generate_required_odoo_tmpl_form_view(view_id, view_xml):
        arch = f'''
            <xpath expr="//page[last()]" position="after">
                <page string="Walmart" name="walmart">
                    {view_xml}
                </page>
            </xpath>
        '''
        tree = etree.fromstring(view_id.arch).getroottree()
        page = tree.findall("//page[@name='walmart']")
        if page:
            page[0].insert(0, etree.XML(view_xml))
        else:
            tree.findall(".")[0].insert(0, etree.XML(arch))
        view_id.arch = etree.tostring(tree, pretty_print=True)

    def getCategories(self, **kw):
        category_list = []
        channel_id = self.channel_id.id

        root_categories_store_ids =  kw['walmart_category_ids'].mapped('store_category_id')
        # IF no root categories selected, need to import root first
        path = "data/us" if self.marketplace in ["US", "CN"] else "data/mx"
        for xsd_nodes, _ in self._read_or_write_file_from_path(path):
            nodes = xsd_nodes.findall('{http://www.w3.org/2001/XMLSchema}complexType')
            root_categ_id = nodes[0].attrib['name']
            if root_categ_id in root_categories_store_ids:
                model_id = self.env['ir.model'].search([('model','=','product.template')]) #Record id ir.model
                xml = ''
                for node in nodes[1:]:
                    category_list.append({
                        "channel_id": channel_id,
                        "name": node.attrib['name'],
                        "store_id": node.attrib['name'],
                        "parent_id": root_categ_id,
                        "leaf_category": True
                    })
                # for ele in node.iterdescendants("{http://www.w3.org/2001/XMLSchema}element"):
                all_name_node = node.getchildren()[0] # Get <xsd:all>
                for ele in all_name_node.iterchildren():
                    if ele.get('maxOccurs') == '1' and ele.get('minOccurs') == '1':
                        # for e in ele.iterchildren('{http://www.w3.org/2001/XMLSchema}complexType'):
                        #     self._generate_required_odoo_tmpl_fields(e.get('name'), e, model_id)
                        for _ in ele.iterchildren('{http://www.w3.org/2001/XMLSchema}simpleType'):
                            label = next(ele.iter('{http://walmart.com/}displayName')).text
                            field_name = f'x_{ele.get("name")}'
                            created = self._generate_required_odoo_tmpl_fields(model_id, field_name, label)
                            if created:
                                xml += f'''
<group>
    <field name="{field_name}"/>
</group>
'''
                            break

                view_id  = xml and self.env.ref('walmart_odoo_connector.product_template_form_view')
                if view_id:
                    xml_root = None
                    for xml_root,file in self._read_or_write_file_from_path('views/product.xml', mode='r+'):
                        arch = f'''
<xpath expr="//page[last()]" position="after">
    <page string="Walmart" name="walmart">
        {xml}
    </page>
</xpath>
'''
                        page = xml_root.findall("//field[@name='arch']//page[@name='walmart']")
                        if page:
                            page[0].insert(0, etree.XML(xml))
                        else:
                            xml_root.findall("//field[@name='arch']")[0].insert(0, etree.XML(arch))

                    self._generate_required_odoo_tmpl_form_view(view_id, xml)
                    for path in self._read_or_write_file_from_path('views/product.xml', mode='w'):
                        path.write_bytes(etree.tostring(xml_root, pretty_print=True))

            else:
                category_list.append({
                    "channel_id": channel_id,
                    "name": root_categ_id,
                    "store_id": root_categ_id,
                })
        channel_id = self.channel_id
        if "channel_id" not in kw:
            kw["channel_id"] = channel_id.id
        kw['page_size'] = float("inf")
        if kw.get("filter_type") == "all":
            result = self.getResponse(
                "utilities/taxonomy?feedType=item&version=3.2")
            if result["data"]:
                category_data = result["data"].get("payload")
                for category in category_data:
                    category["channel_id"] = channel_id.id
                    feed = self._parse_category_feed(category)
                    category_list.extend(feed)
        return category_list, kw

    def _parse_product_data(self, vals):
        data = vals
        variant_feed = []
        type = vals.get("upc") and "wk_upc" or vals.get(
            "gtin") and "wk_ean" or vals.get("isbn") and "wk_isbn"
        feed_vals = {
            "name": data.get("productName"),
            "default_code": data["sku"],
            "store_id": data["sku"],
            "wk_product_id_type": type,
            "barcode": vals.get("upc") or vals.get("gtin") or vals.get("isbn")
        }
        if isinstance(data["price"], list):
            for prices in data["price"]:
                if prices["currency"] == vals["currency_code"]:
                    price = prices["amount"]
                    break
        else:
            price = data["price"]["amount"]
        feed_vals.update({
            "list_price": price,
            "channel_id": data["channel_id"],
            "variants": variant_feed,
            "qty_available": data["quantity"]
        })
        return feed_vals

    def getTemplates(self, **kw):
        product_list = []
        channel_id = self.channel_id
        kw.setdefault("offset", 0) #Start from 0

        if kw.get("filter_type") == "all" or kw.get("object_id"):
            if kw.get("filter_type") == "all":
                product_api_url = "items?includeDetails=true&offset=%s&limit=%s&nextCursor=%s" % (
                    kw.get("offset"), kw.get("page_size"), kw.get("nextCursor", "*"))
                kw["offset"] += kw["page_size"]
            else:
                product_api_url = "items?productIdType=SKU&id=" + \
                    urlparse.quote_plus(kw["object_id"])

            result = self.getResponse(product_api_url)
            if result["data"]:
                kw["nextCursor"] = result["data"].get("nextCursor")

                products_data = result["data"].get("ItemResponse")
                currency_code = channel_id.pricelist_name.currency_id.name
                for prod_vals in products_data:
                    quantity = 0
                    sku = prod_vals["sku"]
                    quantity_res = self.getResponse("inventory?sku="+urlparse.quote_plus(
                        sku))
                    if quantity_res["data"]:
                        quantity = quantity_res["data"]["quantity"]["amount"]
                    prod_vals.update({
                        "quantity": quantity,
                        "currency_code": currency_code,
                        "channel_id": channel_id.id,
                    })
                    feed = self._parse_product_data(prod_vals)
                    product_list.append(feed)
        return product_list, kw

    def markOrderAsShipped(self, w_order_id):
        shipped = False
        extra_header = {
            "Content-type": "application/json",
        }
        response = self.getResponse(
            "orders/%s" % (w_order_id), 'get', extra_header=extra_header)
        if response.get('data'):
            order_line_data = response.get('data').get(
                'orderLines', {}).get('orderLine')
            new_xml = ''
            tracking_info = '''
			<trackingInfo>
				<shipDateTime>2019-08-27T05:30:15.000Z</shipDateTime>
				<carrierName>
				<carrier>FedEx</carrier>
				</carrierName>
				<methodCode>Standard</methodCode>
				<trackingNumber>12333634122</trackingNumber>
				<trackingURL>http://www.fedex.com</trackingURL>
			</trackingInfo>'''
            order_line_xml = '''
				<orderLine>
				<lineNumber>{line_no}</lineNumber>
				<orderLineStatuses>
					<orderLineStatus>
						<status>Shipped</status>
						<statusQuantity>
							<unitOfMeasurement>Each</unitOfMeasurement>
							<amount>{qty}</amount>
						</statusQuantity>
					</orderLineStatus>
				</orderLineStatuses>
				</orderLine>
			'''
            for order_line in order_line_data:
                data = {
                    "line_no": order_line["lineNumber"],
                    "qty": order_line["orderLineQuantity"].get("amount")
                }
                new_xml += order_line_xml.format(**data)
            order_shipment_xml = f'''
			<orderShipment xmlns="http://walmart.com/mp/v3/orders">
			<orderLines>
			{new_xml}
			</orderLines>
			</orderShipment>
			'''
            extra_header["Content-type"] = "application/xml"
            result = self.getResponse(
                "orders/%s/shipping" % (w_order_id), 'post', extra_header, post_data=order_shipment_xml)
            if result["data"]:
                shipped = True
        return shipped

    def refundOrderLines(self, w_order_id, **kwargs):
        refunded = False
        extra_header = {
            "Content-type": "application/xml",
        }
        response = self.getResponse(
            "orders/%s" % (w_order_id))
        # reason = WalmartCancellationReasonMapping[self.channel_id.walmart_default_cancel_reason]
        if response.get('data'):
            order_line_data = response.get('data').get(
                'orderLines', {}).get('orderLine')
            new_xml = line_no = currency = ''
            return_reason = '''
                <refundReason></refundReason>
            '''
            order_line_xml = '''
            <orderLine>
                <lineNumber>{line_no}</lineNumber>
            </orderLine>
            <refunds>
                <refund>
                <refundCharges>
                    <refundCharge>
                        {charge}
                    </refundCharge>
                </refundCharges>
                </refund>
            </refunds>
            '''

            for order_line in order_line_data:
                data = {
                    "line_no": order_line["lineNumber"],
                }
                if order_line.get('charges', {}).get('charge'):
                    line = order_line.get('charges', {}).get('charge')[0]
                    amt = line.get('chargeAmount', {}).get('amount')
                    if not currency:
                        currency = line.get('chargeAmount',{}).get('currency')
                    d = {'currency': currency, 'amt': amt}
                    tax = ''
                    if line.get('tax'):
                        tax = '''
                            <tax>
                                <taxName>{}</taxName>
                                <taxAmount>
                                    <currency>{currency}</currency>
                                    <amount>-{}</amount>
                                </taxAmount>
                            </tax>'''.format(line.get('tax').get('taxName'),
                            line.get('tax').get('taxAmount').get('amount'),
                            currency=currency)
                        d['tax'] = tax

                    charge = '''
                        <charge>
                            <chargeType>{}</chargeType>
                            <chargeName>{}</chargeName>
                            <chargeAmount>
                                <currency>{currency}</currency>
                                <amount>-{amt}</amount>
                            </chargeAmount>
                            {tax}
                        </charge>
                    '''.format(line.get('chargeType', line.get('chargeName'), **d))
                    data['charge'] = charge
                new_xml += order_line_xml.format(**data)

            order_refund_xml = f'''
            <?xml version="1.0" encoding="UTF-8"?>
            <orderRefund xmlns="http://walmart.com/mp/v3/orders">
                <purchaseOrderId>{w_order_id}</purchaseOrderId>
                <orderLines>
                    {new_xml}
                </orderLines>
            </orderRefund>'''
            result = self.getResponse(
                'orders/%s/refund' % (w_order_id), 'post', extra_header, post_data=order_refund_xml)
            if result['data']:
                refunded = True
        return refunded

    def cancelCompleteOrder(self, w_order_id):
        cancelled = False
        extra_header = {
            "Content-type": "application/json",
        }
        response = self.getResponse(
            "orders/%s" % (w_order_id), extra_header=extra_header, )
        reason = WalmartCancellationReasonMapping[self.channel_id.walmart_default_cancel_reason]
        if response.get('data'):
            order_line_data = response.get('data').get(
                'orderLines', {}).get('orderLine')
            new_xml = ''

            order_line_xml = '''
			<orderLine>
				<lineNumber>{line_no}</lineNumber>
				<orderLineStatuses>
					<orderLineStatus>
					<status>Cancelled</status>
					<cancellationReason>{reason}</cancellationReason>
					<statusQuantity>
						<unitOfMeasurement>EACH</unitOfMeasurement>
						<amount>{qty}</amount>
					</statusQuantity>
					</orderLineStatus>
				</orderLineStatuses>
			</orderLine>
			'''
            for order_line in order_line_data:
                data = {
                    "line_no": order_line["lineNumber"],
                    "reason": reason,
                    "qty": order_line["orderLineQuantity"].get("amount")
                }
                new_xml += order_line_xml.format(**data)

            order_cancel_xml = f'''
			<orderCancellation xmlns="http://walmart.com/mp/v3/orders">
			<orderLines>
				{new_xml}
			</orderLines>
			</orderCancellation>'''
            extra_header["Content-type"] = "application/xml"
            result = self.getResponse(
                "orders/%s/cancel" % (w_order_id), 'post', extra_header, post_data=order_cancel_xml)
            if result["data"]:
                cancelled = True
        return cancelled

    def acknowledgeOrder(self, w_order_id, **kwargs):
        acknowledged = False
        extra_header = {
            "Content-type": "application/json",
        }
        response = self.getResponse(
            "orders/%s" % (w_order_id), extra_header=extra_header)
        if response.get('data'):
            order_data = response.get('data')
            result = self.getResponse(
                "orders/%s/acknowledge" % (w_order_id), 'post', extra_header, post_data=order_data)
            if result["data"]:
                acknowledged = True
        return acknowledged

    def _getTaxName(self, tax_data):
        tax = []
        if tax_data:
            amount = tax_data["taxAmount"].get("amount", "")
            tax = [{
                "name": "Tax %s" % (amount),
                "tax_type": "fixed",
                "amount": amount,
                "rate": amount,
            }]
        return tax

    def _parse_order_data(self, order_val, **kw):
        data = order_val
        shipping_info = data.get("shippingInfo", {})
        order_feed = {
            "store_id": data["purchaseOrderId"],  # data["customerOrderId"]
            "partner_id": data.get("customerEmailId") or False,
            "customer_email": data.get("customerEmailId") or False,
            "line_type": "multi",
            "date_order": datetime.utcfromtimestamp(int(data["orderDate"])/1000).strftime(DATETIME_FORMAT),
            "channel_id": data["channel_id"]
        }
        order_lines = []
        currency = False
        carrier = False
        orderline_info = data["orderLines"].get("orderLine")
        skus = []
        if orderline_info:
            for order_line in orderline_info:
                charges = order_line["charges"]["charge"]
                for charge in charges:
                    line_source = (charge["chargeType"] == "PRODUCT" and "product"
                                   or charge["chargeType"] == "SHIPPING" and "delivery"
                                   or "discount")
                    tax_details = self._getTaxName(charge["tax"])
                    sku = order_line.get("item", {}).get("sku", "")
                    domain = [('default_code', '=', sku),
                              ('channel_id', '=', data["channel_id"])]
                    mapped = self.env["channel.template.mappings"].search(
                        domain).mapped('default_code')
                    if not mapped:
                        skus.append(sku)
                    line_data = {
                        "line_product_id": sku,
                        "line_source": line_source,
                        "line_name": order_line.get("item", {}).get("productName", ""),
                        "line_product_default_code": sku,
                        "line_product_uom_qty": order_line.get("orderLineQuantity", {}).get("amount", 1),
                        "line_price_unit": charge["chargeAmount"]["amount"],
                        "line_taxes": tax_details
                    }
                    order_lines.append((0, 0, line_data))
                    if not currency:
                        currency = charge["chargeAmount"]["currency"]

        order_feed["line_ids"] = order_lines
        other_info = orderline_info[0]["orderLineStatuses"].get(
            "orderLineStatus", {})
        if other_info:
            carrier_info = other_info[0].get("trackingInfo")
            order_feed.update(
                {
                    "order_state": other_info[0]["status"],
                    "currency": currency
                }
            )
            if carrier_info:
                carrier = carrier_info.get(
                    "carrierName", {}).get("carrier", "") or \
                        carrier_info.get(
                    "carrierName", {}).get("otherCarrier", "")

        order_feed["carrier_id"] = carrier

        if "postalAddress" in shipping_info:
            delivery_address = shipping_info["postalAddress"]
            order_feed["customer_name"] = delivery_address["name"]
            invoice_address = {
                "invoice_phone": shipping_info["phone"],
                "invoice_name": delivery_address["name"],
                "invoice_partner_id": data.get("customerEmailId") or False,
                "invoice_email": data.get("customerEmailId") or False,
                "invoice_street": delivery_address["address1"],
                "invoice_street2": delivery_address["address2"],
                "invoice_city": delivery_address["city"],
                "invoice_state_id": delivery_address["state"],
                "invoice_zip": delivery_address["postalCode"],
                "invoice_country_id": delivery_address["country"],
            }
            order_feed.update(invoice_address)
        if skus:
            product_list = []
            for object in skus:
                kw["object_id"] = object
                _list, kw = self.getTemplates(**kw)
                product_list += _list
            ProductFeed = self.env["product.feed"]
            for feed in product_list:
                feed.pop('variants', '')
                ProductFeed.create(feed).import_items()
        return order_feed

    def getOrders(self, **kw):
        order_list = []
        kw.setdefault("channel_id", self.channel_id.id)
        if kw.get("filter_type") in ["date_range", "all"]:
            if kw.get("filter_type")=="date_range":
                order_url = "orders?productInfo=true&createdStartDate=%s" %(kw.get("created_at_min"))
                if kw.get("created_at_max"):
                    order_url += "&createdEndDate%s" %(kw.get("created_at_max"))
                order_url += "&limit=%s&nextCursor=%s" % (kw.get("page_size"), kw.get("nextCursor","*"))
            else:
                order_url = "orders?productInfo=true&nextCursor=%s&limit=%s" % (kw.get('nextCursor', "*"), kw.get("page_size"))

            result = self.getResponse(order_url)
            if result["data"]:
                orders_data = result["data"].get("list", {}).get(
                    "elements", {}).get("order", [])
                meta_data = result["data"].get("list", {}).get("meta", {})
                for order_val in orders_data:
                    order_val["channel_id"] = kw.get("channel_id")
                    order_feed = self._parse_order_data(order_val)
                    order_list.append(order_feed)
                if 'nextCursor' in meta_data:
                    kw['nextCursor'] = meta_data["nextCursor"]
                if kw.get("from_cron") and order_feed:
                    self.channel_id.import_order_date = order_feed["date_order"]
        elif kw.get('filter_type') == 'id':
            # Fixed: order import by id
            # result = self.getResponse(
            #     f"orders?productInfo=true&purchaseOrderId={kw.get('object_id')}")
            result = self.getResponse(
                f"orders/{kw.get('object_id')}?productInfo=true")
            if result["data"]:
                # orders_data = result["data"].get("list", {}).get(
                #     "elements", {}).get("order", [])[0]
                orders_data = result["data"].get('order')
                if isinstance(orders_data, list):
                    orders_data = orders_data[0]
                orders_data["channel_id"] = kw.get("channel_id")
                order_feed = self._parse_order_data(orders_data)
                order_list.append(order_feed)

        return order_list, kw

    def getShippingMethods(self, **kw):
        channel_id = self.channel_id
        shipping_methods = []

        if kw.get("filter_type") == "all":
            result = self.getResponse(
                "settings/shipping/carriers")
            if result["data"]:
                for shipping_method in result["data"]:
                    shipping_methods.append({
                        "name": shipping_method["carrierMethodName"],
                        "store_id": shipping_method["carrierMethodId"],
                        "shipping_carrier": shipping_method["carrierMethodName"],
                        "channel_id": channel_id.id,
                        "channel": channel_id.channel,
                        "description": shipping_method["carrierMethodDescription"]
                        }
                    )
        return shipping_methods, kw

    # Export Operation

    def _post_product_header(self):
        '''<requestId>HP_REQUEST</requestId>
        <requestBatchId>HP_REQUEST_BATCH</requestBatchId>
        <feedDate>2017-10-25T23:36:28</feedDate>'''
        header = '''
		<?xml version="1.0" encoding="UTF-8"?>
		<MPItemFeed xmlns="http://walmart.com/">
		<MPItemFeedHeader>
			<version>3.2</version>
			<mart>{0}</mart>
		</MPItemFeedHeader>
		{1}
		</MPItemFeed>
		'''
        return header

    def _ensure_sku(self, template):
        sku = template.default_code
        if not sku:
            sku = self.channel_id.sku_sequence_id.next_by_id()
            template.default_code = sku
        return sku

    def _create_image_url(self, product):
        full_image_url = ""
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        image_url = '/channel/image/product.product/%s/image_1920/492x492.png' % (
            product.id)
        full_image_url = '%s' % urlparse.urljoin(base_url, image_url)
        return full_image_url

    def _prepare_category_specific_data(self, template, **kwargs):
        data = {}
        odoo_catg = kwargs.get("default_category")
        categ_name = odoo_catg.name.replace('&', 'And').replace(" ", "")

        parent_categ = odoo_catg.parent_id.channel_mapping_ids.filtered(
            lambda map: map.channel_id == kwargs.get("channel_id")).store_id

        data[parent_categ] = {
            categ_name: {
                "shortDescription": template.description_sale or "",
                "mainImageUrl": self._create_image_url(template)
            }
        }
        if template.product_variant_ids:
            variants = data[parent_categ][categ_name]["VariantAttributeNames"]
            for variant in template.product_variant_ids:
                sku = self._ensure_sku(variant)
                variants["productGroupId"] = template.default_code
        data["isPrimaryVariant"] = "Yes"
        return data

    def _category_specific_values(self, template, parent_categ, child_categ):
        path = f"data/us/{parent_categ}.xsd" if self.marketplace in ["US", "CN"] else f"data/mx/{parent_categ}.xsd"
        for xsd_nodes, _ in self._read_or_write_file_from_path(path):
            # nodes = xsd_nodes.findall(f'//complexType[@name="{child_categ}"]')
            nodes = list(filter(lambda node: node.get('name')==f"{child_categ}",
                xsd_nodes.findall('{http://www.w3.org/2001/XMLSchema}complexType')))

            xml = ''
            all_name_node = nodes[0].getchildren()[0] # Get <xsd:all>
            for ele in all_name_node.iterchildren():
                if ele.get('maxOccurs') == '1' and ele.get('minOccurs') == '1':
                    for _ in ele.iterchildren('{http://www.w3.org/2001/XMLSchema}simpleType'):
                        field_name = f'x_{ele.get("name")}'
                        field_value = template.read([field_name])[0] or ' '
                        xml += f'''
<{ele.get("name")}>
\t\t\t\t{field_value}
</{ele.get("name")}>
'''
                        break
            return xml

    def _get_product_export_vals(self, product, **kwargs):
        channel_id = kwargs.get('channel_id').id
        # template = product if product._name=="product.template" else product.product_tmpl_id
        odoo_catgs = product.channel_category_ids.filtered_domain(
            [('instance_id', '=', channel_id)]).mapped("extra_category_ids").filtered("parent_id")
        if not odoo_catgs:
            odoo_catgs = product.product_tmpl_id.channel_category_ids.filtered_domain(
                [('instance_id', '=', channel_id)]).mapped("extra_category_ids").filtered("parent_id")
            if not odoo_catgs:
                raise UserError(
                    "Walmart category not mentioned!!")
        odoo_catg = odoo_catgs[0]
        categ_name = odoo_catg.channel_mapping_ids.filtered_domain(
            [('channel_id', '=', channel_id)]).store_category_id
        parent_categ = odoo_catg.parent_id.channel_mapping_ids.filtered_domain(
            [('channel_id', '=', channel_id)]).store_category_id
        categ_specifics = self._category_specific_values(product.product_tmpl_id, parent_categ, categ_name)
        if product.barcode:
            ean = product.barcode.strip('0')
        else:
            ean = ""
        data = {
            "sku": self._ensure_sku(product),
            "type": ProductType[product.wk_product_id_type] or kwargs.get("product_type"),
            "ean": ean,
            # "price": float_round(product.with_context(pricelist=kwargs.get("pricelist_id")).price, 2),
            "price": float_round(channel_id.pricelist_name._get_product_price(product, quantity=1), 2),
            "cost_price": float_round(product.standard_price, 2),
            "name": product.name or "",
            "main_category": parent_categ,
            "child_category": categ_name,
            "image_url": self._create_image_url(product),
            "short_desc": product.description_sale or "",
            "size": product.weight if product.dimensions_uom_id.name == "lbs" else product.weight*2.20462,
            "brand_name": product.wk_brand_name or "",
            "tax_code": kwargs.get("tax_code"),
            "attribute_specific": '',
            "category_specific": categ_specifics,
        }
        return data

    def _create_product_xml(self, template, **kwargs):
        product_xml = ''
        channel_domain = [('channel_id', '=', kwargs.get('channel_id').id)]

        variants = template.product_variant_ids if template._name == "product.template" else template
        variant_group_id = template.default_code
        header = self._post_product_header()
        for product in variants:
            product_val = self._get_product_export_vals(product, **kwargs)
            attributes = product.product_template_attribute_value_ids
            # if not product.channel_mapping_ids.filtered_domain(channel_domain):
            attribute_specific = ''
            variant_group_id = ""

            '''
			<isDrugFactsLabelRequired>
				Yes
			</isDrugFactsLabelRequired>
			'''
            # <shortDescription>{short_desc}</shortDescription>
            # <brand>{brand_name}</brand>
            # <mainImageUrl>{image_url}</mainImageUrl>
            product_xml += '''
			<MPItem>
			<processMode>CREATE</processMode>
			<sku>{sku}</sku>
			<productIdentifiers>
				<productIdentifier>
					<productIdType>{type}</productIdType>
					<productId>{ean}</productId>
				</productIdentifier>
			</productIdentifiers>
			<MPProduct>
				<msrp>{cost_price}</msrp>
				<productName>{name}</productName>
				<category>
				<{main_category}>
					<{child_category}>
                        {category_specific}
						{attribute_specific}
					</{child_category}>
				</{main_category}>
				</category>
			</MPProduct>
			<MPOffer>
				<price>{price}</price>
				<ShippingWeight>
					<measure>
					{size}
					</measure>
					<unit>lb</unit>
				</ShippingWeight>
				<ProductTaxCode>{tax_code}</ProductTaxCode>
			</MPOffer>
			</MPItem>'''
            tmpl_variant_id = product.product_variant_id.mapped(
                'channel_mapping_ids').filtered_domain(channel_domain)
            variant_sku = ""
            if tmpl_variant_id:
                variant_sku = tmpl_variant_id.default_code
            else:
                variant_sku = product.product_variant_id.default_code
                if not variant_sku:
                    variant_sku = self._ensure_sku(product.product_variant_id)
            variant_group_id = '''
					<variantGroupId>{0}</variantGroupId>
				'''.format(variant_sku or "")
            if product != product.product_variant_id:
                is_primary = 'No'
            else:
                is_primary = 'Yes'

            if attributes:
                attrib_name = ''
                attribute_specific = ''
                if is_primary:
                    attribute_specific = '''
					<variantAttributeNames>
					{0}
					</variantAttributeNames>
					'''
                AttributeMapping = self.env["channel.attribute.mappings"]
                other_info = ""
                for attrib in attributes:
                    # wm_attrib = AttributeMapping.search(
                    #     channel_domain+[('attribute_name', '=', attrib.attribute_id.id)]).store_attribute_id
                    # wm_attrib = attrib.attribute_id.channel_mappings_ids.filtered_domain(channel_domain).store_attribute_id
                    # wm_attrib_val = attrib.product_attribute_value_id.channel_mapping_ids.filtered_domain(channel_domain).store_attribute_value_id
                    # # wm_attrib_val = attrib.product_attribute_value_id.name
                    wm_attrib = escape(attrib.attribute_id.name.title())
                    wm_attrib_val = escape(attrib.name.title())
                    wm_attrib = attrib.attribute_id.name.title()
                    wm_attrib_val = attrib.name.title()
                    if is_primary:
                        attrib_name += f'''
						<variantAttributeName>
							{wm_attrib}
						</variantAttributeName>'''
                    other_info += f'''<{wm_attrib}>
									{wm_attrib_val}
								</{wm_attrib}>'''
                attribute_specific = attribute_specific.format(
                    attrib_name)+other_info
            if attribute_specific:
                attribute_specific += f'''
					{variant_group_id}
					<isPrimaryVariant>{is_primary}</isPrimaryVariant>
				'''
            product_val["attribute_specific"] = attribute_specific
            product_xml = product_xml.format(**product_val)
        # if not "has_header" in kwargs:
        product_xml = header.format(kwargs.get('marketplace'), product_xml)
        return product_xml

    def _update_product_xml(self, template, **kwargs):
        product_xml = ''
        channel_domain = [('channel_id', '=', kwargs.get('channel_id').id)]

        variants = template.product_variant_ids if template._name == "product.template" else template
        variant_group_id = template.default_code
        header = self._post_product_header()
        for product in variants:
            if product.channel_mapping_ids.filtered_domain(channel_domain):
                # kwargs["has_header"] = True
                # product_xml += self.create_product_xml(template,**kwargs)

                # else:
                product_val = self._get_product_export_vals(product, **kwargs)
                attributes = product.product_template_attribute_value_ids
                product_val['sku_update'], product_val['barcode_update'] = 'No', 'No'

                key_val = eval(template.wk_ean_sku_updated) if product.product_variant_id == product and eval(
                    template.wk_ean_sku_updated) else eval(product.wk_ean_sku_updated)
                if key_val:
                    if key_val.get('sku'):
                        product_val["sku_update"] = 'Yes'
                    if key_val.get('barcode'):
                        product_val["barcode_update"] = 'Yes'
                attribute_specific = ''
                variant_group_id = ""
                '''
				<MPOffer>
					<price>{price}</price>
					<ShippingWeight>
						<measure>
						{size}
						</measure>
						<unit>lb</unit>
					</ShippingWeight>
					<ProductTaxCode>{tax_code}</ProductTaxCode>
				</MPOffer>
				'''
                '''
				<isDrugFactsLabelRequired>
					Yes
				</isDrugFactsLabelRequired>
				'''
                product_xml += '''
				<MPItem>
				<processMode>REPLACE_ALL</processMode>
				<sku>{sku}</sku>
				<productIdentifiers>
					<productIdentifier>
						<productIdType>{type}</productIdType>
						<productId>{ean}</productId>
					</productIdentifier>
				</productIdentifiers>
				<MPProduct>
					<msrp>{cost_price}</msrp>
					<SkuUpdate>{sku_update}</SkuUpdate>
					<ProductIdUpdate>{barcode_update}</ProductIdUpdate>
					<productName>{name}</productName>
					<category>
					<{main_category}>
						<{child_category}>
						<shortDescription>{short_desc}</shortDescription>
						<brand>{brand_name}</brand>
						<mainImageUrl>{image_url}</mainImageUrl>
							{attribute_specific}
						</{child_category}>
					</{main_category}>
					</category>
				</MPProduct>

				</MPItem>'''
                variant_group_id = '''
						<variantGroupId>{0}</variantGroupId>
					'''.format(product.product_variant_id.default_code or "")
                if product != product.product_variant_id:
                    is_primary = 'No'
                else:
                    is_primary = 'Yes'

                if attributes:
                    attrib_name = ''
                    attribute_specific = ''
                    if is_primary:
                        attribute_specific = '''
						<variantAttributeNames>
						{0}
						</variantAttributeNames>
						'''
                    AttributeMapping = self.env["channel.attribute.mappings"]
                    other_info = ""
                    for attrib in attributes:
                        wm_attrib = AttributeMapping.search(
                            channel_domain+[('attribute_name', '=', attrib.attribute_id.id)]).store_attribute_id
                        # wm_attrib = attrib.attribute_id.channel_mappings_ids.filtered_domain(channel_domain).store_attribute_id
                        # wm_attrib_val = attrib.product_attribute_value_id.channel_mapping_ids.filtered_domain(channel_domain).store_attribute_value_id
                        wm_attrib_val = attrib.product_attribute_value_id.name
                        if is_primary:
                            attrib_name += f'''
							<variantAttributeName>
								{wm_attrib}
							</variantAttributeName>'''
                        other_info += f'''<{wm_attrib}>
										{wm_attrib_val}
									</{wm_attrib}>'''
                    attribute_specific = attribute_specific.format(
                        attrib_name)+other_info
                if attribute_specific:
                    attribute_specific += f'''
						{variant_group_id}
						<isPrimaryVariant>{is_primary}</isPrimaryVariant>
					'''
                product_val["attribute_specific"] = attribute_specific
                product_xml = product_xml.format(**product_val)

        product_xml = header.format(kwargs.get('marketplace'), product_xml)
        return product_xml

    def _call_feeds_api(self, resource_id="", method="get", params={}, data=None, **kwargs):
        url = f"feeds/{resource_id}"
        if params:
            url += '?' + urlparse.urlencode(params)
        result = self.getResponse(url, method, post_data=data, **kwargs)
        return result

    def postTemplate(self, record):
        channel = self.channel_id
        exported = False
        mapping_obj = dict()
        kwargs = {}
        kwargs.update({
            "tax_code": channel.walmart_default_tax_code,
            "default_category": channel.default_category_id,
            "marketplace": MARTKETPLACE_MAP[channel.walmart_marketplace],
            "channel_id": channel,
            "pricelist_id": channel.pricelist_name.id,
        })

        xml_data = self._create_product_xml(record, **kwargs)
        channel_domain = [('channel_id', '=', channel.id)]
        if xml_data:
            additional_header = {
                "extra_header": {
                    "Content-Type": "application/xml",
                }
            }

            xml_data = xml_data.replace("\n", "").replace("\t", "")
            result = self._call_feeds_api(method="post", params={"feedType":"item"},
                                            data=xml_data,
                                            **additional_header)
            if result["data"]:
                if "results" in result["data"]:
                    feed_id = result["data"]["results"]["feed"][0]["feedId"]
                else:
                    feed_id = result["data"]["feedId"]
                exported = True
                mapping_obj["id"] = feed_id
                if record._name == "product.template":
                    non_mapped_variants = record.product_variant_ids.filtered(lambda variant:  variant.channel_mapping_ids.filtered_domain(
                        [('channel_id', '!=', channel.id)]) or not variant.channel_mapping_ids
                    )
                    tmpl = record
                else:
                    non_mapped_variants = record
                    tmpl = record.product_tmpl_id
                template_mapped = tmpl.mapped(
                    "channel_mapping_ids").filtered_domain(channel_domain)
                if non_mapped_variants and not template_mapped:
                    variants = []
                    for variant in non_mapped_variants:
                        variant_id = ",".join(
                            [attrib.product_attribute_value_id.name for attrib in variant.product_template_attribute_value_ids])
                        if not variant_id:
                            variant_id = 'No Variants'
                        variants.append(dict(id=variant_id))
                    mapping_obj["variants"] = variants
        return exported, mapping_obj

    def _update_product_price(self, template, **kwargs):
        res = False
        data = {
            "currency": kwargs.get("currency"),
        }
        channel_domain = [('channel_id', '=', kwargs.get('channel_id').id)]
        if len(template.product_variant_ids) == 1:
            data["sku"] = template.default_code
            # data["price"] = template.with_context(
            #     pricelist=kwargs.get("pricelist_id")).price
            data["price"] = kwargs.get('channel_id').pricelist_name._get_product_price(template, quantity=1)
            post_data = '''
				<Price>
					<itemIdentifier>
					<sku>{sku}</sku>
					</itemIdentifier>
					<pricingList>
					<pricing>
						<currentPrice>
						<value currency={currency} amount={price}/>
						</currentPrice>
					</pricing>
					</pricingList>
				</Price>
			'''.format(**data)
            result = self.getResponse(
                "price",  "put", kwargs.get("extra_header"), post_data)
            if result["data"]:
                res = True
        else:
            xml_format = '''
				<Price>
					<itemIdentifier>
					<sku>{sku}</sku>
					</itemIdentifier>
					<pricingList>
					<pricing>
						<currentPrice>
						<value currency={currency} amount={price}/>
						</currentPrice>
					</pricing>
					</pricingList>
				</Price>
			'''
            xml_data = ""
            # variants = template.product_variant_ids.filtered("channel_mapping_ids")
            variants = template.product_variant_ids.filtered(
                lambda variant:  variant.channel_mapping_ids.filtered_domain(channel_domain))
            for product in variants:
                data["sku"] = product.default_code
                # data["price"] = product.with_context(
                #     pricelist=kwargs.get("pricelist_id")).price
                data["price"] = kwargs.get('channel_id').pricelist_name._get_product_price(product, quantity=1)
                xml_data += xml_format.format(**data)
            post_data = f'''
				<?xml version="1.0" encoding="UTF-8"?>
				<PriceFeed xmlns="http://walmart.com/">
				<PriceHeader>
					<version>1.5.1</version>
				</PriceHeader>
				{xml_data}
				</PriceFeed>
			'''
            kwargs["post_data"] = post_data
            result = self._call_feeds_api(method="post", **kwargs)
            if result["data"]:
                res = result["data"]["feedId"]
        return res

    def syncQuantity(self, mapping, qty):
        channel_id = self.channel_id
        kwargs = {
            "location_id": channel_id.location_id.id,
            "stock_move": True,
            "move_qty": qty,
            "channel_id": channel_id.id
        }
        sync = self._update_product_quantity(mapping, **kwargs)
        return sync

    def _update_product_quantity(self, mapping, **kwargs):
        res = False
        data = {}
        channel_domain = [('channel_id', '=', kwargs.get('channel_id'))]

        data["sku"] = mapping.product_name.default_code
        if kwargs.get('qty_available'):
            wm_stock = mapping.product_name.with_context(
                {'location': kwargs.get('location_id')}).qty_available
        if kwargs.get('stock_move'):
            product_api_url = "inventory?sku="+urlparse.quote_plus(data["sku"])
            result = self.getResponse(product_api_url, **kwargs)
            if result["data"]:
                qty_data = result["data"].get("quantity", {})
                wm_stock = qty_data["amount"] + int(kwargs.get('move_qty'))
        post_data = f'''
		<?xml version="1.0" encoding="UTF-8"?>
		<inventory xmlns="http://walmart.com/">
			<sku>{data['sku']}</sku>
			<quantity>
				<unit>EACH</unit>
				<amount>{wm_stock}</amount>
			</quantity>
		</inventory>
		'''
        kwargs["extra_header"]["Content-Type"] = "application/xml"
        kwargs["post_data"] = post_data.replace(
            "\t", "").replace("\n", "")
        response = self.getResponse(
            product_api_url, "put", **kwargs)
        if response["data"]:
            res = True
        else:
            pass
        return res

    def updateTemplate(self, record):
        channel_id = self.channel_id
        updated = False
        msg = ''
        create_ids = []
        mapping_obj = dict()
        msg = ""
        kwargs = {
            "tax_code": channel_id.walmart_default_tax_code,
            "channel_id": channel_id,
            "pricelist_id": channel_id.pricelist_name.id,
            "currency": channel_id.pricelist_name.currency_id.name,
            "location_id": channel_id.location_id.id,
            "marketplace": MARTKETPLACE_MAP[channel_id.walmart_marketplace],
            "stock_move": True
        }

        xml_data = self._update_product_xml(record, **kwargs)
        if xml_data:
            xml_data = xml_data.replace("\n", "").replace("\t", "")
            kwargs["extra_header"] = {'Content-Type': 'application/xml'}
            result = self._call_feeds_api(method="post",
                            params={"feedType":"item"},
                            data=xml_data,
                            **kwargs)
            if result["data"]:
                if "results" in result["data"]:
                    feed_id = result["data"]["results"]["feed"][0]["feedId"]
                    updated = True
                    msg += "\n"+feed_id
                else:
                    feed_id = result["data"]["feedId"]
                    updated = True
                    msg += "\n"+feed_id

                if feed_id:
                    template = record if record._name == "product.template" else record.product_tmpl_id
                    template.wk_ean_sku_updated = "{}"
                    mapped_variants = template.product_variant_ids.filtered(
                        lambda variant:  variant.channel_mapping_ids.filtered_domain([('channel_id', '=', channel_id.id)]))
                    for variant in mapped_variants:
                        variant.wk_ean_sku_updated = "{}"

        price_updated = self._update_product_price(record, **kwargs)
        qty_updated = self._update_product_quantity(record, **kwargs)
        updated = price_updated and qty_updated and updated
        if isinstance(price_updated, str):
            msg += price_updated
        if isinstance(qty_updated, str):
            msg += '\n'+qty_updated
        return updated, msg

    def testRealtimeOrderSync(self):
        res = False
        eventUrl = '%s' % urlparse.urljoin(self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url') , "/channel/walmart/%s/realtime_ok"%(self.channel_id.id))
        response = self.getResponse("webhooks/test", method="post", post_data=json.dumps({
            "eventType": "PO_CREATED",
            "eventVersion": "V1",
            "resourceName": "ORDER",
            "eventUrl": eventUrl,
        }))
        if response["data"]:
            res = True
        return res

    def registerRealtimeOrderHook(self):
        res = False
        eventUrl = '%s' % urlparse.urljoin(self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url') , "/channel/walmart/%s/realtime_ok"%(self.channel_id.id))
        response = self.getResponse("webhooks/subscriptions", method="post", post_data=json.dumps({
            "eventType": "PO_CREATED",
            "eventVersion": "V1",
            "resourceName": "ORDER",
            "eventUrl": eventUrl,
            "status" : "ACTIVE"
        }))
        if response["data"]:
            res = True
        return res

    def deregisterRealtimeOrderHook(self):
        res = False
        eventUrl = '%s' % urlparse.urljoin(self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url') , "/channel/walmart/%s/realtime_ok"%(self.channel_id.id))
        response = self.getResponse("webhooks/subscriptions", post_data=json.dumps({
            "eventType": "PO_CREATED",
            "eventVersion": "V1",
            "resourceName": "ORDER",
            "eventUrl": eventUrl,
            "status" : "INACTIVE"
        }))
        if response["data"]:
            res = True
        return res
