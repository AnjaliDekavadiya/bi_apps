# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import models, api, fields
from odoo.exceptions import UserError
from odoo.addons.walmart_odoo_connector.walmart_api import WalmartConnect
from odoo.tools import frozendict
from odoo.addons.odoo_multi_channel_sale.tools import parse_float, extract_list as EL

import logging
_logger = logging.getLogger(__name__)

WalmartCateogryBasedAttributeMap = frozendict({
    "Animal": ['color', 'size', 'countPerPack', 'count', 'flavor', 'assembledProductLength',
               'assembledProductWidth', 'assembledProductHeight', 'scent', 'capacity', 'shape', 'sportsTeam', 'character'],
    "ArtAndCraftCategory": ['color', 'shape', 'material', 'finish', 'scent', 'size', 'countPerPack', 'count', 'assembledProductLength', 'assembledProductWidth', 'assembledProductHeight', 'capacity', 'diameter', 'sportsTeam', 'character'],
    "Baby": ['color', 'finish', 'babyClothingSize', 'shoeSize', 'size', 'pattern', 'countPerPack', 'count', 'scent',
             'flavor', 'sportsTeam', 'diaperSize', 'character'],
    "CarriersAndAccessoriesCategory": ['color', 'assembledProductLength', 'assembledProductWidth', 'assembledProductHeight', 'material', 'pattern', 'size', 'bagStyle', 'capacity', 'countPerPack', 'count', 'shape', 'sportsTeam', 'character', 'monogramLetter'],
    "OtherCategory": ['countPerPack', 'size', 'scent', 'color', 'finish', 'capacity', 'shape', 'baseFinish', 'sportsTeam', 'giftCardAmount'],
    "ClothingCategory": ['color', 'clothingSize', 'clothingFit', 'pattern', 'material', 'inseam', 'waistSize', 'neckSize', 'hatSize',
                         'pantySize', 'sockSize', 'countPerPack', 'count', 'braSize', 'braBandSize', 'academicInstitution', 'accentColor', 'sportsTeam', 'character'],
    "Electronics": ['color', 'screenSize', 'resolution', 'ramMemory', 'hardDriveCapacity', 'cableLength', 'digitalFileFormat',
                    'physicalMediaFormat', 'platform', 'edition', 'mountType', 'sportsTeam', 'count', 'countPerPack', 'size'],
    "FoodAndBeverageCategory": ['flavor', 'size', 'sportsTeam', 'countPerPack', 'count'],
    "FootwearCategory": ['color', 'pattern', 'material', 'shoeWidth', 'shoeSize',
                         'heelHeight', 'sportsTeam', 'countPerPack', 'count', 'size'],
    "FurnitureCategory": ['color', 'material', 'bedSize', 'finish', 'pattern', 'frameColor', 'cushionColor',
                          'shape', 'diameter', 'mountType', 'baseColor', 'baseFinish', 'sportsTeam', 'countPerPack', 'count', 'character', 'assembledProductWidth', 'size'],
    "GardenAndPatioCategory": ['size', 'color', 'material', 'finish', 'pattern', 'assembledProductLength', 'assembledProductWidth', 'assembledProductHeight', 'capacity',
                               'shape', 'diameter', 'sportsTeam', 'countPerPack', 'count', 'homeDecorStyle'],
    "HealthAndBeauty": ['color', 'size', 'countPerPack', 'count', 'scent', 'flavor', 'shape', 'diameter', 'sportsTeam'],
    "Home": ['color', 'size', 'material', 'pattern', 'capacity', 'homeDecorStyle', 'bedSize', 'scent', 'countPerPack', 'count', 'academicInstitution',
             'fabricColor', 'shape', 'accentColor', 'diameter', 'fabricMaterialName', 'baseColor', 'baseFinish', 'sportsTeam', 'character', 'finish', 'monogramLetter', 'threadCount'],
    "MediaCategory": ['bookFormat', 'physicalMediaFormat', 'edition', 'sportsTeam', 'countPerPack', 'count'],
    "MusicalInstrumentCategory": ['color', 'pattern', 'material', 'finish', 'audioPowerOutput', 'shape', 'sportsTeam', 'countPerPack', 'count'],
    "OccasionAndSeasonalCategory": ['color', 'clothingSize', 'pattern', 'material', 'countPerPack', 'count', 'theme',
                                    'occasion', 'shape', 'diameter', 'lightBulbType', 'sportsTeam', 'character', 'size'],
    "OfficeCategory": ['color', 'paperSize', 'material', 'countPerPack', 'count', 'numberOfSheets', 'envelopeSize', 'capacity', 'shape',
                       'sportsTeam', 'size'],
    "PhotographyCategory": ['color', 'material', 'finish', 'focalLength', 'displayResolution', 'capacity', 'shape', 'diameter', 		'sportsTeam', 'count', 'size'],
    "ToolsAndHardwareCategory": ['color', 'finish', 'grade', 'countPerPack', 'count', 'volts', 'amps', 'watts', 'workingLoadLimit', 'gallonsPerMinute', 'size',
                                 'assembledProductLength', 'assembledProductWidth', 'assembledProductHeight', 'shape', 'lightBulbType', 'mountType', 'baseColor', 'baseFinish', 'sportsTeam', ],

    "SportAndRecreationCategory": ['color', 'size', 'assembledProductWeight', 'material', 'shoeSize', 'clothingSize', 'sportsTeam',
                                   'sportsLeague', 'compatibleDevices', 'dexterity', 'capacity', 'shape', 'countPerPack', 'count', 'caliber'],
    "ToysCategory": ['color', 'size', 'countPerPack', 'count', 'flavor', 'capacity', 'shape', 'sportsTeam', 'character'],
    "VehicleCategory": ['color', 'finishh', 'vehicalYear', 'vehicalModel', 'engineModel', 'shape', 'diameter', 'sportsTeam', 'count', 'size'],
    "WatchesCategory": ['color', 'material', 'watchBandMaterial', 'plating', 'watchStyle', 'shape', 'sportsTeam', 'countPerPack', 'count'],
})

class ProductProduct(models.Model):
    _inherit = "product.product"

    wk_ean_sku_updated = fields.Char('SKU/Barcode Updated', default="{}")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    wk_walmart_ok = fields.Boolean('Walmart Sale Ok')
    wk_brand_name = fields.Char('Brand Name')
    wk_ean_sku_updated = fields.Char('SKU/Barcode Updated', default="{}")


class ChannelTemplateMappings(models.Model):
    _inherit = 'channel.template.mappings'

    active = fields.Boolean('Active', default=True)


class ChannelProductMappings(models.Model):
    _inherit = 'channel.product.mappings'

    active = fields.Boolean('Active', default=True)

class ProductAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.onchange("product_tmpl_id", "attribute_id")
    def _onchange_product_tmpl_id(self):
        res = {}
        if self.product_tmpl_id.wk_walmart_ok:
            extra_categ_ids = self.product_tmpl_id.channel_category_ids.filtered_domain(
                [('instance_id.channel', '=', 'walmart'), ('extra_category_ids', '!=', False)])
            if extra_categ_ids:
                extra_categ_id = extra_categ_ids[0]
                instance_id = extra_categ_id.instance_id
                main_categ_store_id = False

                categ = extra_categ_id.extra_category_ids[0]
                main_categ_store_id = categ.parent_id.channel_mapping_ids.filtered(
                    lambda map: map.channel_id == instance_id).store_category_id
                attribute_ids = []
                if main_categ_store_id:
                    categ_based_attributes = WalmartCateogryBasedAttributeMap.get(
                        main_categ_store_id)
                    attribute_ids = self.env['channel.attribute.mappings'].search(
                        [('channel_id', '=', instance_id.id), ('store_attribute_id', 'in', categ_based_attributes)]).attribute_name.ids

                res['domain'] = {'attribute_id': [
                    ('id', 'in', attribute_ids)]}
        return res


class ExtraCategories(models.Model):
    _inherit = 'extra.categories'

    @api.model
    def get_category_list(self):
        mapping_ids = self.env['channel.category.mappings'].search(
            [('channel_id', '=', self.instance_id.id)]
        )
        if self.instance_id.channel == "walmart":
            mapping_ids = mapping_ids.filtered("leaf_category")
        if mapping_ids:
            return [i.odoo_category_id for i in mapping_ids]
        return []


class ProductFeed(models.Model):
    _inherit = "product.feed"

    def import_product(self, channel_id):
        self.ensure_one()
        if self.channel!='walmart':
            return super().import_product(channel_id)
        message = ""
        create_id = None
        update_id = None
        context = dict(self._context)
        context.update({
            'pricelist': channel_id.pricelist_name.id,
            'lang': channel_id.language_id.code,
        })
        vals = EL(self.read([
            'name',
            'store_id',
            'list_price',
            'default_code',
            'barcode',
            'wk_product_id_type',
            'standard_price',
            'qty_available',
        ]))
        store_id = vals.pop('store_id')
        state = 'done'
        if not vals.get('name'):
            message += "<br/>Product without name can't evaluated"
            state = 'error'
        if not store_id:
            message += "<br/>Product without store ID can't evaluated"
            state = 'error'
        categ_id = channel_id.default_category_id.id
        if categ_id:
            vals['categ_id'] = categ_id
        if not vals.pop('wk_product_id_type'):
            vals['wk_product_id_type'] = 'wk_upc'
        qty_available = vals.pop('qty_available')
        list_price = vals.get('list_price')
        list_price = list_price and parse_float(list_price) or 0
        location_id = channel_id.location_id
        if not vals.get('default_code'):
            vals['default_code'] = False
        if not vals.get('barcode'):
            vals['barcode'] = False

        match = channel_id.match_template_mappings(store_id, **vals)
        template_exists_odoo = channel_id.match_odoo_template(
            vals, variant_lines=[])
        vals.pop('website_message_ids', '')
        vals.pop('message_follower_ids', '')

        if state == 'done':
            if match:
                if not template_exists_odoo:
                    template_id = match.template_name
                    template_id.with_context(context).write(vals)
                else:
                    template_exists_odoo.with_context(context).write(vals)
                    template_id = template_exists_odoo
                match.write({'default_code': vals.get(
                    'default_code'), 'barcode': vals.get('barcode')})

                for variant_id in template_id.product_variant_ids:
                    variant_vals = variant_id.read(
                        ['default_code', 'barcode'])[0]
                    self.wk_change_product_price(
                        product_id=variant_id,
                        price=list_price,
                        channel_id=channel_id
                    )
                    # if qty_available and eval(qty_available) > 0:
                    #     self.wk_change_product_qty(
                    #         variant_id,qty_available,location_id)
                    if variant_vals.get("barcode") == self.barcode:
                        match_product = channel_id.match_product_mappings(
                            store_id, 'No Variants', default_code=variant_vals.get('default_code'), barcode=variant_vals.get('barcode'))

                        if not match_product:
                            channel_id.create_product_mapping(
                                template_id, variant_id, store_id, 'No Variants',
                                {'default_code': variant_vals.get('default_code'),
                                    'barcode': variant_vals.get('barcode')})

                update_id = match
            else:
                template_id = None
                try:
                    vals['taxes_id'] = None
                    vals['supplier_taxes_id'] = None
                    if not template_exists_odoo:
                        template_id = self.env['product.template'].with_context(
                            context).create(vals)
                    else:
                        template_id = template_exists_odoo

                    if template_id:
                        for variant_id in template_id.product_variant_ids:
                            variant_vals = variant_id.read(
                                ['default_code', 'barcode'])[0]
                            self.wk_change_product_price(
                                product_id=variant_id,
                                price=list_price,
                                channel_id=channel_id
                            )
                            if qty_available and eval(qty_available) > 0:
                                self.wk_change_product_qty(
                                    variant_id, qty_available, location_id)
                            if variant_vals.get("barcode") == self.barcode:
                                match = channel_id.match_product_mappings(
                                    store_id, 'No Variants', default_code=variant_vals.get('default_code'), barcode=variant_vals.get('barcode'))
                                if not match:
                                    channel_id.create_product_mapping(
                                        template_id, variant_id, store_id, 'No Variants',
                                        {'default_code': variant_vals.get('default_code'),
                                            'barcode': variant_vals.get('barcode')})
                except Exception as e:
                    _logger.error('----------Exception------------%r', e)
                    message += '<br/>Error in variants %s' % (e)
                    state = 'error'
                if state == 'done':
                    template_id = template_id and template_id or template_exists_odoo
                    if template_id:
                        create_id = channel_id.create_template_mapping(
                            template_id, store_id,
                            {'default_code': vals.get('default_code'), 'barcode': vals.get('barcode')})

            if state == 'done':
                message += '<br/> Product %s Successfully Evaluate' % (
                    vals.get('name', ''))
        self.set_feed_state(state=state)
        self.message = "%s <br/> %s" % (self.message, message)
        return dict(
            update_id=update_id,
            create_id=create_id,
            message=message
        )
