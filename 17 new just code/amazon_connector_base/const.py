
from odoo.addons.sale_amazon import const


# Mapping of API operations to URL paths, restricted resource paths, and restricted data elements.
const.API_OPERATIONS_MAPPING.update({
    'getFeedResult': {
        'url_path': '/feeds/2021-06-30/feeds/{param}',
        'restricted_resource_path': None,
    },
    'getFeedDocumentResult': {
        'url_path': '/feeds/2021-06-30/documents/{param}',
        'restricted_resource_path': None,
    },
    'createReport': {
        'url_path': '/reports/2021-06-30/reports',
        'restricted_resource_path': None,
    },
    'getReport': {
        'url_path': '/reports/2021-06-30/reports/{param}',
        'restricted_resource_path': None,
    },
    'getReports': {
        'url_path': '/reports/2021-06-30/reports',
        'restricted_resource_path': None,
    },
    'getReportDocument': {
        'url_path': '/reports/2021-06-30/documents/{param}',
        'restricted_resource_path': None,
    },
    'getProductType': {
        'url_path': '/definitions/2020-09-01/productTypes/{param}',
        'restricted_resource_path': None,
    },
    'getProductListing': {
        'url_path': '/listings/2021-08-01/items/{param}',
        'restricted_resource_path': None,
    },
    'getOrder': {
        'url_path': '/orders/v0/orders/{param}',
        'restricted_resource_path': '/orders/v0/orders/{orderId}',
        'restricted_resource_data_elements': ['buyerInfo', 'shippingAddress'],
    },
    'createFulfillmentOrder': {
        'url_path': '/fba/outbound/2020-07-01/fulfillmentOrders',
        'restricted_resource_path': None,
    },
    'cancelFulfillmentOrder': {
        'url_path': '/fba/outbound/2020-07-01/fulfillmentOrders/{param}/cancel',
        'restricted_resource_path': None, # '/fba/outbound/2020-07-01/fulfillmentOrders/{orderId}/cancel',
    },
})
