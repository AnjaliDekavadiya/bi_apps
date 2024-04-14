# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models,api,fields
from odoo.addons.odoo_rest.controllers.main import RestWebServices,_fetch_coloumn_names,_fetchAllFieldData,_fetchColoumnData,_fetchModelData,_updateModelData,_deleteModelData,_createModelData,_fetchModelSchema
from odoo.http import request
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)
class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}


    def _get_sellers_data(self,response,**kw):
        allowed_fields = self._get_allowed_fields()
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        domain = values.get('domain') and literal_eval(values.get('domain')) or []
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        seller_domain = [('seller','=',True)]
        modelObjData = self.search(seller_domain, offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response


    def _getsellerrecorddata(self,record_id,response,**kw):
        modelObjData = self.search([('id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id,self._name )
            response['success'] = False
        else:
            allowed_fields = self._get_allowed_fields()
            values = kw.get("values",{})
            fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _updateSellerRecordData(self,record_id,response,data,**kw):
        modelObjData = self.search([('id', '=', record_id)])
        val_res = self._check_and_validate_schema(data,'PUT')
        if (val_res and val_res.get("success")):
            if not modelObjData:
                response['message'] = "No Record found for id(%s) in given model(%s)." % (
                record_id, self._name)
                response['success'] = False
            else:
                _updateModelData(modelObjData, data, response.get('model_id'))
                response['success'] = True
        else:
            response['message'] = "Schema is not validated for id(%s) in given model(%s)." % (
            record_id, self._name)
            response['success'] = False
        return response

    def _createSellerData(self,response,data,**kw):
        val_res = self._check_and_validate_schema(data,'POST')
        if val_res and val_res.get('success'):
            id = _createModelData(self.sudo(), data, response.get('model_id'))
            response['create_id'] = id
        else:
            response['message'] = "The schema is not validated for model '%s'" % self._name
            response['success'] = False
        return response

class MpSellerShops(models.Model):

    _inherit = "seller.shop"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getAllMpShopsData(self,response,**kw):
        values = kw.get("values",{})
        domain = values.get('domain') and literal_eval(values.get('domain')) or []
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        seller_domain = domain or [(1,'=',1)]
        modelObjData = self.search(seller_domain, offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getSellerShopsData(self,record_id,response,**kw):
        allowed_fields = self._get_allowed_fields()
        values = kw.get("values",{})
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('seller_id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getShopData(self,record_id,response,**kw):
        allowed_fields = self._get_allowed_fields()
        values = kw.get("values",{})
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _updateShopRecordData(self,record_id,response,data,**kw):
        val_res = self._check_and_validate_schema(data,"PUT")
        modelObjData = self.search([('id', '=', record_id)])
        if val_res and val_res.get("success"):
            if not modelObjData:
                response['message'] = "No Record found for id(%s) in given model(%s)." % (
                record_id, self._name)
                response['success'] = False
            else:
                _updateModelData(modelObjData, data, response.get('model_id'))
                response['success'] = True
        else:
            response['message'] = "Schema is not validated for id(%s) in given model(%s)." % (
            record_id, self._name)
            response['success'] = False
        return response

    def _createShopData(self,response,data,**kw):
        val_res = self._check_and_validate_schema(data,"POST")
        if val_res and val_res.get("success"):
            id = _createModelData(self.sudo(), data, response.get('model_id'))
            response['create_id'] = id
        else:
            response['message'] = "Schema is not validated for given model(%s)." % (self._name)
            response['success'] = False
        return response

    def _deleteShopData(self,record_id,response,**kw):
        modelObjData = self.sudo().search([('id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)." % (record_id, self._name)
            response['success'] = False
        else:
            _deleteModelData(modelObjData,response.get('model_id'))
            response['success'] = True
        return response

class MpSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getAllMpOrderLinesData(self,response,**kw):
        values = kw.get("values",{})
        # domain = values.get('domain') and literal_eval(values.get('domain')) or []
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        seller_domain = [('marketplace_seller_id','!=',False)]
        modelObjData = self.search(seller_domain, offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getSellerAllOrderLinesData(self,record_id,response,**kw):
        values = kw.get("values")
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('marketplace_seller_id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response


class MpProductTemplate(models.Model):

    _inherit = "product.template"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getAllMpProductsData(self,response,**kw):
        values = kw.get("values",{})
        # domain = values.get('domain') and literal_eval(values.get('domain')) or []
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        # seller_domain = self._get_seller_domain()
        seller_domain = [('marketplace_seller_id','!=',False)]
        modelObjData = self.search(seller_domain, offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getSellerProductsData(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('marketplace_seller_id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getProductData(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _updateProductRecordData(self,record_id,response,data,**kw):
        val_res = self._check_and_validate_schema(data,'PUT')
        if val_res and val_res.get("success"):
            modelObjData = self.search([('id', '=', record_id)])
            if not modelObjData:
                response['message'] = "No Record found for id(%s) in given model(%s)." % (
                record_id, self._name)
                response['success'] = False
            else:
                _updateModelData(modelObjData, data, response.get('model_id'))
                response['success'] = True
        else:
            response['message'] = "Schema is not validated for id(%s) in given model(%s)." % (
                record_id, self._name)
            response['success'] = False
        return response
    def _createProductData(self,response,data,**kw):
        val_res = self._check_and_validate_schema(data,'POST')
        if val_res and val_res.get("success"):
            id = _createModelData(self.sudo(), data, response.get('model_id'))
            response['create_id'] = id
        else:
            response['message'] = "Schema is not validated for given model(%s)." % (self._name)
            response['success'] = False
        return response
class MpProductProduct(models.Model):

    _inherit = "product.product"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getAllMpProductVariantsData(self,response,**kw):
        # domain = values.get('domain') and literal_eval(values.get('domain')) or []
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        # seller_domain = self._get_seller_domain()
        seller_domain = [('marketplace_seller_id','!=',False)]
        modelObjData = self.search(seller_domain, offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getSellerProductVariantsData(self,record_id,response,**kw):
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('marketplace_seller_id','=',record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response
    def _getProductVariantData(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id','=',record_id)])

        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _updateProductVariantRecordData(self,record_id,response,data,**kw):
        val_res = self._check_and_validate_schema(data,"PUT")
        if val_res and val_res.get("success"):
            modelObjData = self.search([('id', '=', record_id)])
            if not modelObjData:
                response['message'] = "No Record found for id(%s) in given model(%s)." % (
                record_id, self._name)
                response['success'] = False
            else:
                _updateModelData(modelObjData, data, response.get('model_id'))
                response['success'] = True
        else:
            response['message'] = "Schema is not validated for id(%s) in given model(%s)." % (
            record_id, self._name)
            response['success'] = False
        return response

class MarketplaceStock(models.Model):

    _inherit = "marketplace.stock"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getAllMpProductStockData(self,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        seller = values.get('seller')
        offset = int(values.get('offset', 0))
        limit = int(values.get('limit', 0))
        order = values.get('order', None)
        # seller_domain = self._get_seller_domain()
        # seller_domain = [('marketplace_seller_id','=',seller and int(seller) or [])]
        modelObjData = self.search([], offset=offset, limit=limit, order=order)
        if not modelObjData:
            response['message'] = "No Record found for given criteria in model(%s)." % (self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpProductStockData(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id','=',record_id)])

        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data

        return response

    def _updateMpProductStockRecordData(self,record_id,response,data,**kw):
        val_res = self._check_and_validate_schema(data,"PUT")
        modelObjData = self.search([('id', '=', record_id)])
        if val_res and val_res.get("success"):
            if not modelObjData:
                response['message'] = "No Record found for id(%s) in given model(%s)." % (
                record_id, self._name)
                response['success'] = False
            else:
                _updateModelData(modelObjData, data, response.get('model_id'))
                response['success'] = True
        else:
            response['message'] = "Schema is not validated for id(%s) in given model(%s)." % (
            record_id, self._name)
            response['success'] = False
        return response

    def _createMpProductStockData(self,response,data,**kw):
        val_res = self._check_and_validate_schema(data,"POST")
        if val_res and val_res.get("success"):
            id = _createModelData(self.sudo(), data, response.get('model_id'))
            response['create_id'] = id
        else:
            response['message'] = "Schema is not validated for given model '%s'" % self._name
            response['success'] = False
        return response


class MpStockPicking(models.Model):

    _inherit = "stock.picking"


    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def getMpOrderDeliveries(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('sale_id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for order id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpDeliveries(self,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('marketplace_seller_id', '!=', False)])
        if not modelObjData:
            response['message'] = "No Record found for Marketplace in given model(%s)."%(self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpSellerDeliveries(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('marketplace_seller_id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for Seller id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpDelivery(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

class MpSellerPayments(models.Model):

    _inherit = "seller.payment"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getMpPayments(self,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([])
        if not modelObjData:
            response['message'] = "No Record found in given model(%s)."%(self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpSellerPayments(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('seller_id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for Seller id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpPayment(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id, self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

class MpAccountMove(models.Model):

    _inherit = "account.move"

    def _get_allowed_fields(self):
        return ['id','name']

    def _check_and_validate_schema(self, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        return {"success":True,"Error":""}

    def _getInvoice(self,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('mp_seller_bill', '=', True)])
        if not modelObjData:
            response['message'] = "No Record found for Marketplace in given model(%s)."%(self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response

    def _getMpSellerInvoices(self,record_id,response,**kw):
        values = kw.get("values",{})
        allowed_fields = self._get_allowed_fields()
        fields = allowed_fields or values.get('fields') and literal_eval(values.get('fields')) or []
        modelObjData = self.search([('id', '=', record_id)])
        if not modelObjData:
            response['message'] = "No Record found for id(%s) in given model(%s)."%(record_id,self._name)
            response['success'] = False
        else:
            data = _fetchModelData(modelObjData,fields,response.get('model_id'))
            response['data'] = data
        return response
