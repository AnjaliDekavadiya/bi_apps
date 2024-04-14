==========================
 Quick configuration guide
==========================

|

1. Install the Odoo Magento-2 Connector on your Odoo server - How to install in `Odoo.sh <https://youtu.be/JqtW4y12cm4>`__.

|

2. Our connector is using queue_job from OCA. **If you are on odoo.sh, skip this section and jump to the next one.** Below is quick summary of what you need to add at the end of your odoo.conf file. If you are interested in full documentation, check it out `here <https://apps.odoo.com/apps/modules/16.0/queue_job/>`__.

| ``workers = 2 ; set here amount of workers higher than 1``
| ``server_wide_modules = web,queue_job,integration,integration_magento2 ; add queue_job to server wide modules``
| ``[queue_job]``
| ``channels = root:1``

|

3. Special note for deploying to odoo.sh (`video <https://youtu.be/JqtW4y12cm4>`__):

   -  Config file can be found when entering shell in the following location "/home/odoo/.config/odoo/odoo.conf". Add there the following configs:

| ``server_wide_modules = web,queue_job,integration,integration_magento2``
| ``[queue_job]``
| ``channels = root:1``
| ``scheme = https``
| ``host = <your_odoo_host> (e.g. myhost.odoo.com)``
| ``port = 443``
|

   - After changing the configuration file, run ``odoosh-restart`` command in the shell.

|

4. Follow `this video guide <https://www.youtube.com/watch?v=7Gh4XKk8Fcs>`__ to get webservice API key for Magento 2 and perform the initial connection between Odoo and Magento 2.

|

5. Then continue with the Quick Configuration wizard. We do not have yet a dedicated video for Magento 2 - but all our connectors work the same way. So you can refer to the video from the Shopify connector starting from 3:30 (`watch video <https://youtu.be/BgPB4dhKEQE?t=212>`__).

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

* 1.9.2 (2024-01-05)
    - NEW! On odoo.sh when the backup is restored on the staging branch, disable automatic all sales integrations, disable on integrations critical functions (export of products, order statuses, product inventory) and delete webhooks.
    - Fixed issue with missed categories on initial import.
    - Refactored logic of mapping products.
    - Improved orders processing: imported orders data will be marked as "require update" to make sure that the latest updates will be downloaded during Sales Order creation in Odoo.
    - Fixed an issue with stock synchronization for products with zero stock.
    - Fixed for order cancellation: orders cancelled in external e-commerce system will be automatically cancelled if they were imported to Odoo.
    - Other small fixes and improvements.

* 1.9.1 (2023-11-22)
    - Fixed issue with importing new products from Magento (when selection fields presented in fields mappings).
    - Fixed tests (failed on Odoo.sh when MRP module isn't available).
    - Fixed issue with module upgrade (Odoo raised an exception while extracting translations due to icons in views).
    - Fixed issue with translation string when cancelling orders.
    - Other small fixes and improvements.

* 1.9.0 (2023-11-05)
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
    - Fixed export template flow for the Magento2: "The image content is invalid. Verify the content and try again".
    - Other small fixes and improvements.

* 1.8.1 (2023-09-29)
    - Fixed issue with auto-workflow not executing all tasks

* 1.8.0 (2023-09-19)
    - New! Custom attributes with multivalues are now synchronized by assigned keys, establishing a relation from Magento 2 with Many2One fields in Odoo. `(watch video) <https://www.youtube.com/watch?v=0s_xO_oSjDI>`__
    - NEW! Added the ability to exclude specific products from Stock Synchronization with the use of special checkbox in the E-commerce tab on the product form. `(watch video) <https://www.youtube.com/watch?v=l9Mu3eCPBds>`__
    - Fixed issue with updating translatable fields when default ERP language different to Magento 2 shop language.
    - Fixed issue with missed orders.
    - Fixed issue with exporting tracking number for pickings with product kits.
    - Fixed a small issue with Boolean field synchronization for Magento 2.
    - Fixed issue with products validation and initial import for stores with a large number of deactivated products.
    - Added unit tests for testing field mapping logic within the integration module.
    - Other small improvements and fixes.

* 1.7.0 (2023-08-14)
    - NEW! Add setting for export prices via price list from Odoo to Magento 2. Configurable based on integration. `(watch video) <https://www.youtube.com/watch?v=Q9Hh1okL3bw&ab_channel=VentorTech>`__
    - NEW! Set forcibly discount to zero to avoid affection of the price list with policy "Show public price & discount to the customer".
    - NEW! Improve automatic mapping of Magento 2 country states to Odoo country states.

* 1.6.0 (2023-07-19)
    - NEW! Added the possibility to synchronize product quantity from different Odoo Locations to different Magento 2 Locations. Can be configured in the “Inventory“ tab on sales integration. Note that Advanced MSI modules should be installed on Magento 2. `(watch video) <https://youtu.be/O5o9zxWTCTo>`__
    - NEW! Added the possibility to create dynamic filters for importing products from Magento 2. By default, the filter is configured to import products only active products. `(watch video) <https://youtu.be/-6Pf8Fc4SBg>`__
    - NEW! Added setting to automatically create products on SO Import in case products doesn’t exist yet in Odoo. Configurable based on integration. `(watch video) <https://www.youtube.com/watch?v=b0aBh9XCNCI&ab_channel=VentorTech>`__
    - NEW! During initial import, the connector will generate only product variants that exist in Magento 2. This behavior is configurable on the “Product Defaults“ tab on sales integration with the checkbox “Import Attributes as Dynamic“. It is switched off by default. `(watch video) <https://youtu.be/esONyR7kZ7A>`__
    - NEW! Add new behavior on empty tax “Take from the Product“. When selected, if the downloaded sales order line will not have defined taxes, it will insert on the sales order line customer tax defined on the product. `(watch video) <https://youtu.be/bShKi6TZbtc>`__
    - NEW! Allow excluding specific product attributes to synchronize from Odoo to Magento 2. Can be configured in “Sales - Configuration - Attributes“. `(watch video) <https://youtu.be/LZvrutgifuU>`__
    - NEW! Discount for individual products is added as a separate line on Odoo Sales Order for proper financial records. `(watch video) <https://youtu.be/OvymmCkTsi0>`__
    - NEW! Allow switching on and off validation of missing barcodes on product variants. When “Validate missing barcodes for variants“ is enabled then the connector will validate that either all variants should have barcodes, or neither of the variants should have barcodes (the mix is not allowed). Available only in Debug mode on the “Product Defaults“ tab. `(watch video) <https://youtu.be/sL4ZOO7swpg>`__
    - In case it is configured not to download the barcode field from Magento 2 to Odoo (in Product Fields Mapping there is no barcode field defined) connector will not analyze external products for duplicated barcodes.
    - Download orders by batches to avoid timeout of “Receive Orders” job.
    - Improve the validation mechanism on Magento 2. Now finding out the wrong configurations of products on Magento 2 side: (1) Simple products that belong to multiple-configurable products; (2) configurable product that belong to another configurable product.
    - Do not create redundant BOMs for Product Bundles downloaded from Magento 2.
    - Do not send inactive product variants when exporting products to Magento 2.
    - Added to sales integration list of global fields that are monitored for changes. So when the product is updated and these fields are changed, then we also trigger the export of the product.
    - Product attributes are synchronized according to their sequence to preserve the same order as in Odoo.
    - Other small improvements and fixes.

* 1.5.2 (2023-04-04)
    - Fix issue with duplicated product price for products with variants on initial product import.

* 1.5.1 (2023-03-23)
    - Fix issue with impossibility to cancel sales order (in some cases) or register payment.

* 1.5.0 (2023-03-13)
    - NEW! Added “Exclude from Synchronisation” settings on the product to exclude specific products and all their variants totally from sync and all related logic (validation, auto-mapping). `(watch video) <https://youtu.be/7zO2y0Q6aS8>`__
    - NEW! Contacts that were created by the connector will have a special Tag with the name of the sales integration it was created from. That allows us to easier find all contacts created from specific integration. `(watch video) <https://youtu.be/0a0r-RDeNag>`__
    - Copy “e-Commerce payment method” from Sales Order to the related Customer Invoice.
    - Sales Orders with a non-valid EU VAT number will be created. But a warning message will be added in Internal Note for the created Sales Order informing the user about this problem.
    - Convert weight on import/export of products in case UoM in Odoo is different from UoM in Magento 2 (kgs vs lbs).
    - Other small fixes and improvements.

* 1.4.0 (2023-02-17)
    - NEW! Reworked product import and export mechanism. Now for simple fields, no coding is required to synchronize them from/to Odoo. Fields mapping working both for initial import (Magento 2 -> Odoo) and for export (Odoo -> Magento 2). `(watch video) <https://youtu.be/VPsw1F51aYE>`__
    - NEW! Trigger products export only if fields that are marked with the “Send field for updating“ checkbox are updated. That leads to a smaller number of export product jobs. `(watch video) <https://youtu.be/ye-z8xtqKro>`__
    - NEW! Implemented initial stock levels import functionality from Magento 2 to Odoo (available on the "Initial Import" tab). `(watch video) <https://youtu.be/DP3-DhWTSy0>`__
    - NEW! Now all integration logs are available in a separate menu "Job Logs". It is possible to see everything that happened to a specific Product or Sales Order in a quick way. `(watch video) <https://youtu.be/06b1kPVFYno>`__
    - NEW! Add the possibility to define the "Orders Cut-off" date. Only orders created after this date will be synchronized. `(watch video) <https://youtu.be/AyqOlhyiFuc>`__
    - NEW! Added Cost Price field synchronization for initial import from Magento 2 to Odoo and for exporting Products from Odoo to Magento 2. `(watch video) <https://youtu.be/JblvT47VUEY>`__
    - NEW! Custom Options from the sales order line in Magento 2 are copied to the sales order line in Odoo. `(watch video) <https://youtu.be/eQ8NJGF-Zes>`__
    - Make ZIP code a non-required field for contact creation during sales order import as some countries do not require it.
    - PERFORMANCE! Overall performance improvements for the requests to Magento 2.
    - Fix Customer VAT (Registration) number import.
    - Other small fixes and improvements.

* 1.3.3 (2023-01-24)
    - Fix Customer VAT (Registration) number import.

* 1.3.2 (2023-01-06)
    - Fix issue when en_US language is deactivated.
    - Add Sale Integration in product on Import Product From External.

* 1.3.1 (2022-12-31)
    - Fixing issue that is not allowing to download orders with zero shipping cost.

* 1.3.0 (2022-12-28)
    - NEW! Add a setting to send products from Odoo on initial export in “inactive“ status, so products can be reviewed later and published manually. `(watch video) <https://youtu.be/w5AIjxhvuls>`__
    - NEW! Allow defining payment terms that will be used instead of the standard on Order synchronization depending on the payment method of the sales order. `(watch video) <https://youtu.be/gDSbEe1GEGQ>`__
    - NEW! Trigger new products export only if a product has non-empty fields that are mandatory for product export. The list of fields is defined on the integration level and by default it is “Internal Reference“ only. `(watch video) <https://youtu.be/-6ruWO7qVHE>`__
    - NEW! Send the "Paid" status to Magento 2 after the order is fully paid in Odoo or in accordance with the "Send payment status when" property on the workflow payment method. `(watch video) <https://youtu.be/NXdVqzsHmVE>`__
    - NEW! Implemented discount handling for Magento 2 "Cart Rules" to be properly synchronized into Odoo (coupon code will be added to description of the product line). `(watch video) <https://youtu.be/zFfj5U0hw0c>`__
    - NEW! Added global config to allow sending tax included OR tax excluded sales price. `(watch video) <https://youtu.be/0VbrJceXibw>`__
    - NEW! Allow defining special ZERO tax that will be used in case there are no taxes defined on the imported sales order line. `(watch video) <https://youtu.be/4Pyw_HETjaM>`__
    - NEW! Added step in configuration wizard that is allowing to define which Product Fields from Magento 2 should be attributes in Odoo. `(watch video) <https://youtu.be/uoDOObFov5w>`__
    - NEW! Added possibility to use webhooks in Magento 2 to track order status change on Magento 2 side (based on `https://github.com/mageplaza/magento-2-webhook`: Mageplaza Webhook for Magento 2 supports online store to send an API request via a webhook to a configurable destination (URL) when specific trigger events take place. Webhook a very useful and necessary tool which allows stores to update instant and real-time notifications. Magento extension).
    - Export tracking number in case it is added after Picking is moved to the "Done" state (when using some third-party connectors).
    - Improve connector to allow exporting more than 10K products.
    - Added a new field on the customer to have “Company Name” as a separate field. This field is also used when displaying customer addresses on Odoo forms and on printed PDF forms (e.g. Invoices, Pickings and etc.).
    - Set the order date in Odoo to be the same as in the Shopify order. Previously it was changed by Odoo standard mechanism during order confirmation.
    - Fix auto-workflow action “Validate Picking“ not validating pickings in case of multi-step delivery.
    - “Force Export to External“ action on products is now sending products to Magento 2 even if automatic products export from Odoo is disabled in integration settings.
    - Other small fixes and improvements.

* 1.2.7 (2022-12-14)
    - Fixed creation of mappings during the initial product import.

* 1.2.6 (2022-11-25)
    - Fixed import or products when there are duplicate product attributes.

* 1.2.5 (2022-11-11)
    - Added data-migration for external contacts.

* 1.2.4 (2022-11-11)
    - Fix for handling a Guest-customer in order.

* 1.2.3 (2022-11-07)
    - Added compatibility with partner_firstname module from OCA.

* 1.2.2 (2022-10-28)
    - Fixed Feature Value creation.
    - Fixed “Import External Records“ running for Product Variants from Jobs.
    - Fixed calculation of discount in Odoo if there are several taxes in sales order.

* 1.2.1 (2022-10-18)
    - Fix for finding external tax from mapping table.
    - Import customers functionality was not working with all queue_job module versions.

* 1.2.0 (2022-10-10)
    - NEW! Allow exporting of product quantities both in real-time and by cron. Make it configurable on the “Inventory“ tab on sales integration. `(watch video) <https://youtu.be/qpNzJk2G3Lk>`__
    - NEW! Allow defining which field should be synchronized when sending the stock to the e-Commerce system. Allowing 3 options: “Free To Use Quantity“, “On Hand Quantity” and  “Forecasted Quantity”. `(watch video) <https://youtu.be/8c7yw2QT5fY>`__
    - NEW! Implemented wizard allowing to import customers based on the last update date. `(watch video) <https://youtu.be/f__ZMptKj7A>`__
    - NEW! Added setting to allow automatic creation of Delivery Carrier and Taxes in Odoo if the existing mapping is not found (during initial import and during Sales Order Import). `(watch video) <https://youtu.be/FmKa8gu4PpM>`__
    - When an order is created with an existing partner make sure to also emulate the selection of partner on the Odoo interface so needed fields from the partner will be filled in (Payment Terms, Fiscal Positions and etc.).
    - TECHNICAL! Improve the retry mechanism for importing products and executing workflow actions to workaround concurrent update errors in some cases (e.g. sales order was not auto-confirmed and remained in draft state).
    - Do not create webhooks automatically in case integration is activated. Users need to do it manually by clicking the “Create Webhooks“ button on “Webhooks“ tab inside integration.
    - Set the proper fiscal position on automatic order import according to Fiscal Position settings.
    - When a product in Odoo with a single attribute value for EVERY attribute is exported to Magento, connector creates a Simple Product with this attribute added to the “Attributes“ section on the product page (so it is becoming searchable).
    - Before updating product in Magento, retrieve it’s current SKU from Magento 2, to use it for product update. Magento 2 allows to products records only by SKU.
    - Improved logic for handling bundle products during receiving orders from Magento 2 to Odoo.
    - Before linking shipping and billing address to imported order, make sure it have exactly same address in it as in downloaded order. Magento 2 allows to edit address in existing order from admin console (before it was imported to Odoo) and that may result in incorrect delivery address settings on Odoo side.
    - Improved manual mapping of product variants and product templates in case template has only 1 variant.

* 1.1.0 (2022-09-05)
    - NEW! Major feature. Introduced auto workflow that allows based on sales order status: to validate sales order, create and validate invoice for it and register payment on created invoice. Configuration is flexible and can be done individually for every SO status.

* 1.0.0 (2022-07-10)
    - Odoo integration with Magento 2.

|
