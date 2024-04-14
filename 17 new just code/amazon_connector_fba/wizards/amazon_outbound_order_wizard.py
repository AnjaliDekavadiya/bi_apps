import time
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.sale_amazon import utils as amazon_utils


class AmazonOutboundOrderWizard(models.TransientModel):
    _name = "amazon.outbound.order.wizard"

    help_fulfillment_action = """
        Ship - The fulfillment order ships now
        Hold - An order hold is put on the fulfillment order.

        Default: Ship in Create Fulfillment
        Default: Hold in Update Fulfillment
    """

    help_fulfillment_policy = """
        FillOrKill - If an item in a fulfillment order is determined to be unfulfillable before any
                    shipment in the order moves to the Pending status (the process of picking units
                    from inventory has begun), then the entire order is considered unfulfillable.
                    However, if an item in a fulfillment order is determined to be unfulfillable
                    after a shipment in the order moves to the Pending status, Amazon cancels as
                    much of the fulfillment order as possible

        FillAll - All fulfillable items in the fulfillment order are shipped.
                The fulfillment order remains in a processing state until all items are either
                shipped by Amazon or cancelled by the seller

        FillAllAvailable - All fulfillable items in the fulfillment order are shipped.
            All unfulfillable items in the order are cancelled by Amazon.

        Default: FillOrKill
    """

    account_id = fields.Many2one('amazon.account', string='Account', required=True)
    marketplace_id = fields.Many2one("amazon.marketplace", string="Amazon Marketplace")
    # fba_warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="wizard_amazon_outbound_sale_order_rel",
        column1="wizard_id", column2="sale_id",
        string="Sales Orders")
    fulfillment_action = fields.Selection([
            ('Ship', 'Ship'),
            ('Hold', 'Hold')
        ], string="Fulfillment Action",
        default="Ship", help=help_fulfillment_action
    )
    displayable_order_date = fields.Date(
        "Displayable Order Date", help="Display Date in package")
    fulfillment_policy = fields.Selection([
            ('FillOrKill', 'FillOrKill'),
            ('FillAll', 'FillAll'),
            ('FillAllAvailable', 'FillAllAvailable')
        ], string="Fulfillment Policy", default="FillOrKill", required=True,
        help=help_fulfillment_policy)
    shipment_service_level_category = fields.Selection([
            ('Standard', 'Standard'),
            ('Expedited', 'Expedited'),
            ('Priority', 'Priority'),
            ('ScheduledDelivery', 'ScheduledDelivery')
        ], string="Shipment Category", default='Standard',
        help="ScheduledDelivery used only for Japan")
    delivery_start_time = fields.Datetime(
        "Delivery Start Time", help="Delivery Estimated Start Time")
    delivery_end_time = fields.Datetime(
        "Delivery End Time", help="Delivery Estimated End Time")
    query_start_date_time = fields.Datetime(
        "Query Start Date Time",
        help="If you not specified start time then system will take -36 hours")
    notify_by_email = fields.Boolean(
        "Notify By Email", help="If true then system will notify by email to followers")
    is_displayable_order_date_required = fields.Boolean("Displayable Date Requied?", default=True)
    note = fields.Text("Note", help="To set note in outbound order")

    """
    @api.onchange("marketplace_id", "is_displayable_order_date_required")
    def on_change_sale_orders(self):
        sale_env = self.env['sale.order']
        warehouse_id = self.marketplace_id.fba_warehouse_id.id
        if not self.is_displayable_order_date_required:
            self.displayable_order_date = False
        self.fba_warehouse_id = warehouse_id
        res = {}
        domain = {}
        sales_orders = sale_env.search(
            [('state', '=', 'draft'), ('warehouse_id', '=', warehouse_id),
             ('amz_instance_id', '=', False)])
        domain.update({'sale_order_ids': [('id', 'in', sales_orders.ids)]})
        res.update({'domain': domain})
        return res"""

    def create_order(self):
        marketplace = self.marketplace_id
        fulfillment_action = self.fulfillment_action
        displayable_order_date = self.displayable_order_date or False
        fulfillment_policy = self.fulfillment_policy
        shipment_service_level_category = self.shipment_service_level_category
        amazon_sale_order_ids = []
        amazon_product_env = self.env['amazon.offer']
        for sale_order in self.sale_order_ids:
            if not sale_order.order_line:
                continue
            amazon_order = sale_order

            amazon_order.write({
                'amz_account_id': self.account_id.id,
                # 'amz_marketplace_id': marketplace.id,
                'amazon_channel': 'fba',
                'amz_fulfillment_action': fulfillment_action,
                'warehouse_id': marketplace.fba_warehouse_id.id,
                # 'pricelist_id': marketplace.pricelist_id.id,
                'amz_displayable_order_date': displayable_order_date or
                                                sale_order.date_order,
                'amz_fulfillment_policy': fulfillment_policy,
                'amz_shipment_service_level_category': shipment_service_level_category,
                'is_amz_outbound_order': True,
                'notify_by_email': self.notify_by_email,
                'amazon_order_ref': sale_order.name,
                'note': str(self.note),
            })
            for line in amazon_order.order_line:
                if line.product_id.detailed_type == 'service':
                    continue
                if line.product_id:
                    amz_product = amazon_product_env.search([
                            ('product_id', '=', line.product_id.id),
                            ('marketplace_id', '=', marketplace.id),
                            ('is_afn', '=', True)
                        ], limit=1)
                    if not amz_product:
                        raise UserError("Product %s not found in %s" % (line.product_id.display_name, marketplace.name))
                    line.write({'amazon_product_id': amz_product.id})
            amazon_sale_order_ids.append(amazon_order.id)
        self.with_context(active_ids=amazon_sale_order_ids).create_fulfillment()
        return amazon_sale_order_ids

    def create_fulfillment(self):
        active_ids = self._context.get('active_ids')
        draft_orders = self.env['sale.order'].search([
             ('id', 'in', active_ids),
             ('is_amz_outbound_order', '=', True),
             ('state', 'in', ['draft', 'sent']),
             ('is_amz_outbound_exported', '=', False)])
        if not draft_orders:
            return True
        for order in draft_orders:
            if not order.amz_shipment_service_level_category:
                raise UserError(
                    "Required field Shipment Category is not set for order %s" % (order.name)
                )
            if not order.note:
                raise UserError(
                    "Required field Displayable Order Comment is not set for order %s" % (order.name)
                )
            if not order.amz_fulfillment_action:
                raise UserError(
                    "Required field Order Fulfillment Action is not set for order %s" % (order.name)
                )
            if not order.amz_displayable_order_date:
                raise UserError("Required field Order Fulfillment Action is not set for order %s" % (order.name)
                )
            if not order.amz_fulfillment_policy:
                raise UserError(
                    "Required field Fulfillment Policy is not set for order %s" % (order.name)
                )
            self.export_amz_outbound_order(order)
        return True
    """
    def update_fulfillment(self):
        active_ids = self._context.get('active_ids')
        amazon_instance_obj = self.env['amazon.instance.ept']
        progress_orders = self.env['sale.order'].search(
            [('id', 'in', active_ids), ('amz_is_outbound_order', '=', True),
             ('state', '=', 'draft'),
             ('is_amz_outbound_exported', '=', True)])
        if not progress_orders:
            return True
        for instance in amazon_instance_obj.search([('fba_warehouse_id', '!=', False)]):
            mws_obj = OutboundShipments_Extend(
                access_key=instance.access_key and str(instance.access_key) or False,
                secret_key=instance.secret_key and str(instance.secret_key) or False,
                account_id=instance.merchant_id and str(instance.merchant_id) or False,
                region=instance.country_id.amazon_marketplace_code or instance.country_id.code,
                auth_token=instance.auth_token and str(instance.auth_token) or False)
            for order in progress_orders:
                if order.amz_instance_id.id != instance.id:
                    continue
                try:
                    mws_obj.UpdateFulfillmentOrder(order)
                    self._cr.commit()
                except Exception as e:
                    raise UserError(str(e))
        return True

    def get_fulfillment_by_instance(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        marketplace_id = self._context.get('active_id')
        instance = amazon_instance_obj.search(
            [('id', '=', marketplace_id), ('fba_warehouse_id', '!=', False)])
        orders = self.env['sale.order'].search(
            [('state', 'in', ['progress', 'manual']),
             ('amz_fulfillment_order_status', 'not in', ['COMPLETE', 'CANCELLED']),
             ('amz_instance_id', '=', marketplace_id), ('is_amz_outbound_exported', '=', True)])
        mws_obj = OutboundShipments_Extend(
            access_key=instance.access_key and str(instance.access_key) or False,
            secret_key=instance.secret_key and str(instance.secret_key) or False,
            account_id=instance.merchant_id and str(instance.merchant_id) or False,
            region=instance.country_id.amazon_marketplace_code or instance.country_id.code,
            auth_token=instance.auth_token and str(instance.auth_token) or False)
        for order in orders:
            try:
                result = mws_obj.GetFullfillmentOrder(order)
                self.env['stock.picking'].create_shipment(order, result)
            except Exception as e:
                raise UserError(str(e))

        return True

    def get_fulfillment_order(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        active_ids = self._context.get('active_ids')
        orders = self.env['sale.order'].search(
            [ # ('state', 'in', ['progress', 'manual']),
             ('amz_fulfillment_order_status', 'not in', ['COMPLETE', 'CANCELLED']),
             ('id', 'in', active_ids), ('is_amz_outbound_exported', '=', True)])
        for instance in amazon_instance_obj.search([('fba_warehouse_id', '!=', False)]):
            mws_obj = OutboundShipments_Extend(
                access_key=instance.access_key and str(instance.access_key) or False,
                secret_key=instance.secret_key and str(instance.secret_key) or False,
                account_id=instance.merchant_id and str(instance.merchant_id) or False,
                region=instance.country_id.amazon_marketplace_code or instance.country_id.code,
                auth_token=instance.auth_token and str(instance.auth_token) or False)
            for order in orders:
                if order.amz_instance_id.id != instance.id:
                    continue
                try:
                    result = mws_obj.GetFullfillmentOrder(order)
                    self.env['stock.picking'].create_shipment(order, result)
                except Exception as e:
                    raise UserError(str(e))
        return True

    def list_fulfillment_orders(self):
        amazon_instance_obj = self.env['amazon.instance.ept']
        marketplace_id = self._context.get('active_id')
        instance = amazon_instance_obj.search(
            [('id', '=', marketplace_id), ('fba_warehouse_id', '!=', False)])
        sale_env = self.env['sale.order']
        import_time = False
        if self.query_start_date_time:
            import_time = time.strptime(self.query_start_date_time, "%Y-%m-%d %H:%M:%S")
            import_time = time.strftime("%Y-%m-%dT%H:%M:%S", import_time)
            import_time = time.strftime("%Y-%m-%dT%H:%M:%S",
                                        time.gmtime(time.mktime(
                                            time.strptime(import_time, "%Y-%m-%dT%H:%M:%S"))))
            import_time = str(import_time) + 'Z'

        mws_obj = OutboundShipments_Extend(
            access_key=instance.access_key and str(instance.access_key) or False,
            secret_key=instance.secret_key and str(instance.secret_key) or False,
            account_id=instance.merchant_id and str(instance.merchant_id) or False,
            region=instance.country_id.amazon_marketplace_code or instance.country_id.code,
            auth_token=instance.auth_token and str(instance.auth_token) or False)
        list_wrapper = []
        try:
            result = mws_obj.ListAllFulfillmentOrders(import_time)
        except Exception as e:
            raise UserError(str(e))
        next_token = result.parsed.get('NextToken', {}).get('value')
        list_wrapper.append(result)
        while next_token:
            try:
                result = mws_obj.list_orders_by_next_token(next_token)
            except Exception as e:
                raise UserError(str(e))
            next_token = result.parsed.get('NextToken', {}).get('value')
            list_wrapper.append(result)

        for wrapper in list_wrapper:
            for member in wrapper.parsed.get('FulfillmentOrders', {}):
                order_name = member.get('SellerFulfillmentOrderId', {}).get('value', False)
                status = member.get('FulfillmentOrderStatus', {}).get('value', False)
                order = sale_env.search({'name': order_name})
                order and order.write({'amz_fulfillment_order_status': status})
        return True"""

    def cancel_fulfillment(self):
        active_ids = self._context.get('active_ids')
        amazon_instance_obj = self.env['amazon.instance.ept']
        progress_orders = self.env['sale.order'].search(
            [('id', 'in', active_ids), ('amz_is_outbound_order', '=', True),
             ('state', '=', 'cancel'),
             ('is_amz_outbound_exported', '=', True)])
        if not progress_orders:
            return True
        for instance in amazon_instance_obj.search([('fba_warehouse_id', '!=', False)]):
            mws_obj = OutboundShipments_Extend(
                access_key=instance.access_key and str(instance.access_key) or False,
                secret_key=instance.secret_key and str(instance.secret_key) or False,
                account_id=instance.merchant_id and str(instance.merchant_id) or False,
                region=instance.country_id.amazon_marketplace_code or instance.country_id.code,
                auth_token=instance.auth_token and str(instance.auth_token) or False)
            for order in progress_orders:
                if order.amz_instance_id.id != instance.id:
                    continue
                try:
                    mws_obj.CancelFulfillmentOrder(order)
                    self._cr.commit()
                except Exception as e:
                    raise UserError(str(e))
        return True

    def wizard_view(self, created_id):
        view = self.env.ref('amazon_connector_fba.amazon_outbound_order_wizard')
        return {
            'name': _('Amazon Outbound Orders'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amazon.outbound.order.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': created_id and created_id.id or False,
            'context': self._context,
        }

    def export_amz_outbound_order(self, order):
        amazon_utils.refresh_aws_credentials(order.amz_account_id)
        amazon_utils.ensure_account_is_set_up(order.amz_account_id)
        data = order.generate_amz_outbound_order_data()
        result = amazon_utils.make_sp_api_request(
            order.amz_account_id,
            operation='createFulfillmentOrder',
            payload=data,
            method='POST'
        )
        if order.amz_fulfillment_action == 'Ship':
            order.write({'is_amz_outbound_exported': True})
        return result

    def UpdateFulfillmentOrder(self, order):
        partner = order.partner_shipping_id
        currency_code = partner and partner.company_id and partner.company_id.currency_id.name or False
        currency_code = not currency_code and order.amz_instance_id.company_id.currency_id.name
        data = self.get_data(order)
        data.update({
            'Action': 'UpdateFulfillmentOrder',
        })
        return self.make_request(data)
