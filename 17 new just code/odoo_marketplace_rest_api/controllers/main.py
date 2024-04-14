# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import json
import xml.etree.ElementTree as ET
import werkzeug
from odoo.http import request, Controller, route
import logging
_logger = logging.getLogger(__name__)
from functools import wraps
from ast import literal_eval
from odoo.service.model import execute_kw
from odoo.addons.odoo_rest.controllers.main import RestWebServices,_fetch_coloumn_names,_fetchAllFieldData,_fetchColoumnData,_fetchModelData,_updateModelData,_deleteModelData,_createModelData,_fetchModelSchema


NON_RELATIONAL_FIELDS = ['boolean','char','float','html','integer','monetary','text','selection',
# 'date','datetime'
]

class MpWebServices(RestWebServices):

    def __authenticate(func):
        @wraps(func)
        def wrapped(inst, **kwargs):
            _logger.info("***********authenticate**********")
            inst._mData = request.httprequest.data and json.loads(request.httprequest.data.decode('utf-8')) or {}
            inst.ctype = request.httprequest.headers.get('Content-Type') == 'text/xml' and 'text/xml' or 'json'
            inst._auth = inst._authenticate(**kwargs)
            return func(inst, **kwargs)
        return wrapped

    def _available_api(self):
        apis = super(MpWebServices, self)._available_api()
        return apis

    def _get_seller_domain(self):
        domian = [('seller','=',True)]
        return domian

    def _get_allowed_fields(self,model):
        if hasattr(model,'_get_allowed_fields'):
            return model._get_allowed_fields()
        return ['id','name']

    # def _check_and_validate_seller_schema(self, data):
    #     check all required field over here and then validate the schema data
    #     return self._validate_seller_schema(data)

    # def _validate_schema(self, data):
    #     _logger.info("---------data-----%r-------",data)
    #     validate schema
    #     {
    #         *'name',
    #         *'email',
    #         'password',#encrpt
    #         *'url_handler',
    #         *'address':{*'street','street2',*'city',*'state_code',*'zip',*'country_code'},
    #         'website',
    #         'phone',
    #         'mobile',
    #         'title',
    #         'return policy',
    #         'shipping policy',
    #         'profile':{
    #             'image',
    #             'banner',
    #             'message'
    #         }
    #         'social web info':{
    #             'name',
    #             'id',
    #             'url'
    #         }
    #     }
    #     return True

    def _check_and_validate_schema(self, model, data, type):
        """
        data: comming from the api request.
        type: PUT, POST
        1. First we check all required fields in the schema.
        2. Validate the schema.
        return
        dict -> {'sucess':(True/False),'error':'custom_error'}"""
        # We have to define a method in each module which provide the required fields and also provide a check for validating a schema
        if hasattr(model,"_check_and_validate_schema"):
            return model._check_and_validate_schema(data)
        return {"success":True,"Error":""}

    # Seller API's

    @route(['/api/mp/sellers'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getSellersData(self, **kwargs):
        """Get all marketplace seller data"""
        object_name = "res.partner"
        response = self._auth

        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._get_sellers_data(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getSellerRecordData(self, record_id, **kwargs):
        """Get all data of a particular seller.
        record_id: Seller ID"""
        object_name = "res.partner"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getsellerrecorddata(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/seller/<int:record_id>'], type='http', auth="none", methods=['PUT'], csrf=False)
    @__authenticate
    def updateSellerRecordData(self, record_id, **kwargs):
        """Write some data for a particular seller with ID as a record_id.
        record_id: Seller ID"""
        object_name = "res.partner"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('write'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._updateSellerRecordData(record_id,response,data)
                else:
                    response['message'] = "You don't have write permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)



    # def get_required_field(self, model, data):
    #     """Method to Check a required fields for model."""
    #     required_fields = model.fields_get(attributes=["required"])
    #     need_fields = [i for i in required_fields if required_fields[i].get("required") and i not in data ]
    #     _logger.info("-----------get_required_field------------%r",request.env["product.template"].fields_get(allfields=["categ_id"]))
    #     if need_fields:
    #         return {'Missing_fields':need_fields,'message':"Please provide the these fields value .These fields are required for model {}".format(model._name)}
    #     else:
    #         return True


    @route(['/api/mp/seller/create'], type='http', auth="public", csrf=False, methods=['POST'])
    @__authenticate
    def createSellerData(self, **kwargs):
        """Create Seller With Required Fields"""
        object_name = "res.partner"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('create'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    # Need to implement the validation bases response
                    # res = self.get_required_field(modelObjData,data)
                    # if not res :
                    response = modelObjData._createSellerData(response,data)
                else:
                    response['message'] = "You don't have create permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    # Seller Shop's API's

    @route(['/api/mp/shops'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getAllMpShopsData(self, **kwargs):
        """Get all marketplace shops"""
        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getAllMpShopsData(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                # pass
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>/shops'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getSellerShopsData(self, record_id, **kwargs):
        """Get all shops for a particular seller.
        record_id: Seller ID"""
        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getSellerShopsData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/shop/<int:record_id>'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getShopData(self, record_id, **kwargs):
        """Get shop data for a particular shop with an ID.
        record_id: Shop ID"""
        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getShopData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/shop/<int:record_id>'], type='http', auth="none", methods=['PUT'], csrf=False)
    @__authenticate
    def updateShopRecordData(self, record_id, **kwargs):
        """Write data in a particular shop record.
        record_id: Shop ID"""
        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('write'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._updateShopRecordData(record_id,response,data,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have write permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/shop/create'], type='http', auth="public", csrf=False, methods=['POST'])
    @__authenticate
    def createShopData(self, **kwargs):
        """Create a shop record with data."""

        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('create'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._createShopData(response,data)
                else:
                    response['message'] = "You don't have create permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/shop/<int:record_id>'], type='http', auth="none", methods=['DELETE'], csrf=False)
    @__authenticate
    def deleteShopData(self, record_id, **kwargs):
        """Delete a particular shop with record id.
        record_id: Shop ID"""
        object_name = "seller.shop"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('delete'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._deleteShopData(record_id,response)
                else:
                    response['message'] = "You don't have delete permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    # Seller Order's API's

    @route(['/api/mp/order/lines'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getAllMpOrderLinesData(self, **kwargs):
        """Get all marketplace sale order lines."""
        object_name = "sale.order.line"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getAllMpOrderLinesData(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                # pass
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>/order/lines'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getSellerAllOrderLinesData(self, record_id, **kwargs):
        """Get all order lines for a particular seller.
        record_id: Seller ID"""
        object_name = "sale.order.line"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getSellerAllOrderLinesData(record_id,response,values = request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    # Seller Products

    @route(['/api/mp/products'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getAllMpProductsData(self, **kwargs):
        """Get all marketplace products."""
        object_name = "product.template"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    # domain = request.httprequest.values.get('domain') and literal_eval(request.httprequest.values.get('domain')) or []
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getAllMpProductsData(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                # pass
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>/products'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getSellerProductsData(self, record_id, **kwargs):
        """Get all products for a particular seller.
        record_id: Seller ID"""
        object_name = "product.template"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getSellerProductsData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/product/<int:record_id>'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getProductData(self, record_id, **kwargs):
        """Get shop data for a particular shop with an ID.
        record_id: Product Template ID"""
        object_name = "product.template"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getProductData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/product/<int:record_id>'], type='http', auth="none", methods=['PUT'], csrf=False)
    @__authenticate
    def updateProductRecordData(self, record_id, **kwargs):
        """Write data in a particular product record.
        record_id: Product Template ID"""
        object_name = "product.template"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('write'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._updateProductRecordData(record_id,response,data)
                else:
                    response['message'] = "You don't have write permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/product/create'], type='http', auth="public", csrf=False, methods=['POST'])
    @__authenticate
    def createProductData(self, **kwargs):
        """Create a product record with data."""
        object_name = "product.template"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('create'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._createProductData(response,data)
                    # Need to implement the validation bases response

                else:
                    response['message'] = "You don't have create permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    # Product Variants

    @route(['/api/mp/product/variants'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getAllMpProductVariantsData(self, **kwargs):
        """Get all marketplace product variants."""
        object_name = "product.product"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getAllMpProductVariantsData(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                # pass
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>/product/variants'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getSellerProductVariantsData(self, record_id, **kwargs):
        """Get all products for a particular seller.
        record_id: Seller ID"""
        object_name = "product.product"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getSellerProductVariantsData(record_id,response)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/product/variant/<int:record_id>'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getProductVariantData(self, record_id, **kwargs):
        """Get shop data for a particular shop with an ID.
        record_id: Product Variant ID"""
        object_name = "product.product"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getProductVariantData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/product/variant/<int:record_id>'], type='http', auth="none", methods=['PUT'], csrf=False)
    @__authenticate
    def updateProductVariantRecordData(self, record_id, **kwargs):
        """Write data in a particular product record.
        record_id: Product Variant ID"""
        object_name = "product.product"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('write'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._updateProductVariantRecordData(record_id,response,data)
                else:
                    response['message'] = "You don't have write permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    # Seller Inventory

    @route(['/api/mp/product/stock'], type='http', auth="none", csrf=False, methods=['GET'])
    @__authenticate
    def getAllMpProductStockData(self, **kwargs):
        """Get all marketplace product stocks."""
        object_name = "marketplace.stock"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    # domain = request.httprequest.values.get('domain') and literal_eval(request.httprequest.values.get('domain')) or []
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getAllMpProductStockData(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                # pass
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/product/stock/<int:record_id>'], type='http', auth="none",methods=['GET'], csrf=False)
    @__authenticate
    def getMpProductStockData(self, record_id, **kwargs):
        """Get shop data for a particular shop with an ID.
        record_id: Marketplace Stock ID"""
        object_name = "marketplace.stock"
        response = self._auth
        if response.get('success'):
            try:
            # if True:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpProductStockData(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r"%e
                response['success'] = False
        return self._response(object_name, response,self.ctype)

    @route(['/api/mp/product/stock/<int:record_id>'], type='http', auth="none", methods=['PUT'], csrf=False)
    @__authenticate
    def updateMpProductStockRecordData(self, record_id, **kwargs):
        """Write data in a particular marketplace stock record.
        record_id: Marketplace Stock ID"""
        object_name = "marketplace.stock"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('write'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._updateMpProductStockRecordData(record_id,response,data)
                else:
                    response['message'] = "You don't have write permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r" % e
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/product/stock/create'], type='http', auth="public", csrf=False, methods=['POST'])
    @__authenticate
    def createMpProductStockData(self, **kwargs):
        """Create a marketplace stock record with data."""
        object_name = "marketplace.stock"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('create'):
                    data = self._mData
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._createMpProductStockData(response,data)
                else:
                    response['message'] = "You don't have create permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)


    @route(['/api/mp/order/<int:record_id>/deliveries'], type='http', auth="none", csrf=False, methods=['Get'])
    @__authenticate
    def getMpOrderDeliveries(self, record_id, **kwargs):
        """Get all deliveries of marketplace with order ID."""
        object_name = "stock.picking"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData.getMpOrderDeliveries(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/deliveries'], type='http', auth="none", csrf=False, methods=['Get'])
    @__authenticate
    def getMpDeliveries(self, **kwargs):
        """Get all marketplace Deliveries."""
        object_name = "stock.picking"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpDeliveries(response,values=request.httprequest.values)

                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/seller/<int:record_id>/deliveries'], type='http', auth="none", csrf=False, methods=['Get'])
    @__authenticate
    def getMpSellerDeliveries(self, record_id, **kwargs):
        """Get all deliveries of a seller with seller ID"""
        object_name = "stock.picking"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpSellerDeliveries(record_id,response,values=request.httprequest.values)

                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/delivery/<int:record_id>'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getMpDelivery(self, record_id, **kwargs):
        """Get a Marketplace Delivery Data With Delivery ID"""
        object_name = "stock.picking"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpDelivery(record_id,response,values=request.httprequest.values)

                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/payments'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getMpPayments(self, **kwargs):
        """Get a Marketplace Delivery Data With Delivery ID"""
        object_name = "seller.payment"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpPayments(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)


    @route(['/api/mp/seller/<int:record_id>/payments'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getMpSellerPayments(self, record_id,**kwargs):
        """Get a Marketplace Seller Payments Data With Seller Id"""
        object_name = "seller.payment"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpSellerPayments(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)

    @route(['/api/mp/payment/<int:record_id>'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getMpPayment(self, record_id,**kwargs):
        """Get a Marketplace Seller Payments Data With Id"""
        object_name = "seller.payment"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpPayment(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)


    @route(['/api/mp/invoices'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getInvoice(self,**kwargs):
        """Get All Mp Invoices Data"""
        object_name = "account.move"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    respone = modelObjData._getInvoice(response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)


    @route(['/api/mp/invoice/<int:record_id>'], type='http', auth="public", csrf=False, methods=['Get'])
    @__authenticate
    def getMpSellerInvoices(self,record_id,**kwargs):
        """Get Invoice Data with Id"""
        object_name = "account.move"
        response = self._auth
        if response.get('success'):
            try:
                response.update(response['confObj']._check_permissions(object_name,response.get('user_id')))
                if response.get('success') and response.get('permissions').get('read'):
                    modelObjData = request.env[object_name].sudo()
                    response = modelObjData._getMpSellerInvoices(record_id,response,values=request.httprequest.values)
                else:
                    response['message'] = "You don't have read permission of the model '%s'" % object_name
                    response['success'] = False
            except Exception as e:
                response['message'] = "ERROR: %r %r" % (e, kwargs)
                response['success'] = False
        return self._response(object_name, response, self.ctype)
