# -*- coding: utf-8 -*-
#################################################################################
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models

LABEL_FORMAT = [
    ('pdf', 'PDF'),
    ('png', 'PNG'),
    ('zpl203', 'ZPL203DPI'),
    ('zpl300', 'ZPL300DPI'),
]
CONTENT_TYPE = [
    ('NDX', 'NDX - Non Documents'),
    ('DOX', 'DOX - Documents'),
    ('HV', 'HV - Non Documents of High Value'),
]
INCOTERMS = [
    ('DDU', 'DDU'),
    ('DDP', 'DDP'),
    ('DAP', 'DAP'),
    ('DAT', 'DAT'),
]
REASON_FOR_EXPORT = [
    ('Gift', 'Gift'),
    ('Commercial Sample', 'Commercial Sample'),
    ('Documents', 'Documents'),
    ('Sale of Goods', 'Sale of Goods'),
    ('Return of Goods', 'Return of Goods'),
    ('Mixed Content', 'Mixed Content'),
    ('Other', 'Other'),
]

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    
    delivery_type = fields.Selection(
        selection_add=[('royal_mail_pro', 'Royal Mail Proshipping')], ondelete={'royal_mail_pro': 'cascade'}
    )

    royal_pro_client_id = fields.Char(string="Client ID")
    royal_pro_client_secret = fields.Char(string="Client Secret")
    royal_pro_grant_type = fields.Char(string="Grant Type", default="client_credentials")
    royal_pro_eori_number = fields.Char(string="EORI Number")
    royal_pro_ShippingAccountId = fields.Char(string="Shipping Account ID")
    royal_pro_ShippingLocationId = fields.Char(string="Shipping Location ID")
    royal_pro_DescriptionOfGoods = fields.Char(string="Description Of Goods", help="Eg: Clothes")

    royal_pro_service_type_id = fields.Many2one(comodel_name='delivery.royal_mail_pro.service', string="Royal Mail Proshipping Service")
    royal_pro_fixed_price = fields.Integer(string="Fixed Price", default=0.0)
    royal_pro_labelformat = fields.Selection(selection=LABEL_FORMAT, string="Label Format", default="pdf")
    is_royal_pro_use_account_address = fields.Boolean(string="Use Shipper Address from Royal Mail Account", default=False)

class ProductPackage(models.Model):
    _inherit = 'product.package'

    delivery_type = fields.Selection(
        selection_add=[('royal_mail_pro', 'Royal Mail Proshipping')], ondelete={'royal_mail_pro': 'cascade'}
    )

class ProductPackage(models.Model):
    _inherit = 'product.package'

    delivery_type = fields.Selection(
        selection_add=[('royal_mail_pro', 'Royal Mail Proshipping')]
    )


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(
        selection_add=[('royal_mail_pro', 'Royal Mail Proshipping')]
    )

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_all_wk_carriers(self):
        res = super(StockPicking, self).get_all_wk_carriers()
        res.append('royal_mail_pro')
        return res
    
class ProshippingShippingService(models.Model):
    _name = "delivery.royal_mail_pro.service"
    _description = "Delivery Carrier Royal mail Pro Service"

    name = fields.Char(string="Name", required=True)
    content_type = fields.Selection(selection=CONTENT_TYPE, string="Content Type", default="NDX", required=True)
    product_id = fields.Many2one("delivery.royal_mail_pro.product", string="Service Code", required=True)
    is_international = fields.Boolean(string="Is International")
    reason_for_export = fields.Selection(selection=REASON_FOR_EXPORT, string="Reason For Export", default="Sale of Goods", required=True)
    incoterms = fields.Selection(selection=INCOTERMS, string="Incoterms", default="DDU", required=True)

class ProshippingServiceProducts(models.Model):
    _name = "delivery.royal_mail_pro.product"
    _description = "Delivery Carrier Deutsche Post Product"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
