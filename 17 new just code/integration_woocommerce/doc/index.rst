==========================
 Quick configuration guide
==========================

|

1. Install the Odoo WooCommerce Connector on your Odoo server – How to install in `Odoo.sh <https://youtu.be/1kZtC7S-TNA>`__.

|

2. As our connector is using queue_job from OCA, you need to make sure also to properly configure your Odoo instance. Specifically check that you have below in your odoo.conf file:

   - Make sure that number of workers is 2 and higher (e.g. ``workers = 4``).
   - Make sure queue_job module is added to server wide modules (e.g. ``server_wide_modules = web,queue_job,integration,integration_woocommerce``).
   - Add the following lines specific to queue_job to identify amount of channels that will be used for it.

    | ``workers = 2 ; set here amount of workers higher than 1``
    | ``server_wide_modules = web,queue_job,integration,integration_woocommerce ; add queue_job to server wide modules``
    | ``[queue_job]``
    | ``channels = root:1``

|

3. Special note for deploying to odoo.sh (`video <https://youtu.be/1kZtC7S-TNA>`__):

   -  Config file can be found when entering shell in the following location "/home/odoo/.config/odoo/odoo.conf". Add there the following configs:


    | ``server_wide_modules = web,queue_job,integration,integration_woocommerce``
    | ``[queue_job]``
    | ``channels = root:1``
    | ``scheme = https``
    | ``host = <your_odoo_host> (e.g. myhost.odoo.com)``
    | ``port = 443``  

   - After changing the configuration file, run ``odoosh-restart`` command in the shell.

|

4. Follow `this video guide <https://youtu.be/Ovj6YB7Bsmc>`__ to get the API key for Woocommerce and perform the initial connection between Odoo and Woocommerce.

|

5. Then continue with the Quick Configuration wizard. We do not have yet a dedicated video for Woocommerce - but all our connectors work the same way. So you can refer to the video from the Shopify connector starting from 3:30 (`watch video <https://youtu.be/BgPB4dhKEQE?t=212>`__).

|

Feedback
##########

- In case of any issues, please contact us at support@ventor.tech
- Don't forget to share your experience after you go live :)
  
  | (only person who made a purchase, can leave ratings)

|

Change Log
##########

|

* 1.6.1 (2024-01-05)
    - NEW! Added possibility to set different backorder policies for separate products. `(watch video) <https://youtu.be/ipS56C-l73Q>`__
    - NEW! On odoo.sh when the backup is restored on the staging branch, disable automatic all sales integrations, disable on integrations critical functions (export of products, order statuses, product inventory) and delete webhooks.
    - Improved logic of delivery methods synchronization.
    - Fixed issue with tax with empty rate or empty name.
    - Refactored logic of mapping products.
    - Improved orders processing: imported orders data will be marked as "require update" to make sure that the latest updates will be downloaded during Sales Order creation in Odoo.
    - Fixed an issue with stock synchronization for products with zero stock.
    - Fixed for order cancellation: orders cancelled in external e-commerce system will be automatically cancelled if they were imported to Odoo.
    - Other small fixes and improvements.

* 1.6.0 (2023-11-23)
    - NEW! Support of the `product bundles <https://woo.com/products/product-bundles/>`__ during order processing. `(watch video) <https://www.youtube.com/watch?v=pWbPsJMkeno>`__
    - NEW! Support of the `composite products <https://woo.com/products/composite-products/>`__ during order processing. `(watch video) <https://www.youtube.com/watch?v=pWbPsJMkeno>`__

* 1.5.0 (2023-11-05)
    - NEW! Added the ability to receive and record customer language values on the Contact (res.partner model). `(watch video) <https://youtu.be/WhtxQcCOcMA>`__
    - NEW! Improved import of delivery methods. `(watch video) <https://youtu.be/lMQIaxMlFns>`__
    - NEW! Added configuration to allow backorders for out-of-stock products. `(watch video) <https://youtu.be/FmWkIt4zqc0>`__
    - Improved logic of states auto-mapping.
    - Improved connectors' UI/UX.
    - Improved image naming logic for products with lengthy names or with special symbols in product names.
    - Improved calculation of discount on prices with includes taxes.
    - Added support of discounts for delivery lines in Odoo.
    - Improved detection of changes in product attributes, including images, to trigger product export.
    - Added integration settings export/import wizard.
    - Fixed issue with products serialization for export to e-commerce system when 'en_US' language is inactive in Odoo.
    - Fixed export of translatable fields with empty values.
    - Fixed issue with export of images and stock during the first-time export.
    - Fixed issue with mapping product attributes / features values.
    - Other small fixes and improvements.

* 1.4.1 (2023-09-29)
    - Fixed issue with auto-workflow not executing all tasks

* 1.4.0 (2023-09-19)
    - New!  Security improve: hide sensitive data in integration parameters.
    - NEW! Import product categories with translations.
    - NEW! Added the ability to exclude specific products from Stock Synchronization with the use of special checkbox in the E-commerce tab on the product form. `(watch video) <https://www.youtube.com/watch?v=l9Mu3eCPBds>`__
    - Fixed issue with updating translatable fields when default ERP language different to WooCommerce shop language.
    - Fixed issue with missed orders.
    - Fixed issue with exporting tracking number for pickings with product kits.
    - Fixed the issue of importing products with over 10 variants from Woocommerce to Odoo.
    - Added unit tests for testing field mapping logic within the integration module.
    - Other small improvements and fixes.

* 1.3.0 (2023-08-14)
    - NEW! Add setting for export prices via price list from Odoo to PrestaShop. Configurable based on integration. `(watch video) <https://www.youtube.com/watch?v=Q9Hh1okL3bw&ab_channel=VentorTech>`__
    - NEW! Multi-language support. Added possibility send translations from the ERP system to Woocommerce shop based on WordPress WPML plugin. Can be configured in "e-Commerce Integration - Configuration - All Product Fields". `(watch video) <https://youtu.be/0OdFM0WqKZw>`__
    - NEW! Set forcibly discount to zero to avoid affection of the price list with policy "Show public price & discount to the customer".
    - NEW! Improve automatic mapping of country states to Odoo country states.
    - Fixed issue with incorrect tax calculation for orders with fee lines.

* 1.2.0 (2023-07-19)
    - NEW! Added setting to automatically create products on SO Import in case products doesn’t exist yet in Odoo. Configurable based on integration. `(watch video) <https://www.youtube.com/watch?v=b0aBh9XCNCI&ab_channel=VentorTech>`__
    - NEW! During initial import, the connector will generate only product variants that exist in Woocommerce. This behavior is configurable on the “Product Defaults“ tab on sales integration with the checkbox “Import Attributes as Dynamic“. It is switched off by default. `(watch video) <https://youtu.be/esONyR7kZ7A>`__
    - NEW! Add new behavior on empty tax “Take from the Product“. When selected, if the downloaded sales order line will not have defined taxes, it will insert on the sales order line customer tax defined on the product. `(watch video) <https://youtu.be/bShKi6TZbtc>`__
    - NEW! Allow excluding specific product attributes to synchronize from Odoo to Woocommerce. Can be configured in “Sales - Configuration - Attributes“. `(watch video) <https://youtu.be/LZvrutgifuU>`__
    - NEW! Discount for individual products is added as a separate line on Odoo Sales Order for proper financial records. `(watch video) <https://youtu.be/OvymmCkTsi0>`__
    - In case it is configured not to download the barcode field from Woocommerce to Odoo (in Product Fields Mapping there is no barcode field defined) connector will not analyze external products for duplicated barcodes.
    - Download orders by batches to avoid timeout of “Receive Orders” job.
    - Fixed duplicated discount applied on sales order downloaded from WooCommerce.
    - Do not send inactive product variants when exporting products to Woocommerce.
    - Added to sales integration list of global fields that are monitored for changes. So when the product is updated and these fields are changed, then we also trigger the export of the product.
    - Product attributes are synchronized according to their sequence to preserve the same order as in Odoo.
    - Other small improvements and fixes.

* 1.1.3 (2023-03-23)
    - Fix issue with impossibility to cancel sales order (in some cases) or register payment.

* 1.1.2 (2023-03-16)
    - Fix quantity export after creating product in WooCommerce
    - Fix issue with switching on Order Actions on Sale Integration

* 1.1.1 (2023-03-15)
    - Fix issue with tracking number export

* 1.1.0 (2023-03-13)
    - NEW! Added “Exclude from Synchronisation” settings on the product to exclude specific products and all their variants totally from sync and all related logic (validation, auto-mapping). `(watch video) <https://youtu.be/7zO2y0Q6aS8>`__
    - NEW! Contacts that were created by the connector will have a special Tag with the name of the sales integration it was created from. That allows us to easier find all contacts created from specific integration. `(watch video) <https://youtu.be/0a0r-RDeNag>`__
    - NEW! Allow defining VAT meta field name to import VAT number for contact during SO creation using any third-party plugins. `(watch video) <https://youtu.be/ftJzsUoVkdY>`__
    - Copy “e-Commerce payment method” from Sales Order to the related Customer Invoice.
    - Sales Orders with a non-valid EU VAT number will be created. But a warning message will be added in Internal Note for the created Sales Order informing the user about this problem.
    - Convert weight on import/export of products in case UoM in Odoo is different from UoM in WooCommerce (kgs vs lbs).
    - Other small fixes and improvements.

* 1.0.0 (2023-02-17)
    - Odoo integration with WooCommerce.

|