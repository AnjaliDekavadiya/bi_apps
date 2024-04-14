from odoo import _, api, fields, models


class AmazonAccount(models.Model):
    _inherit = 'amazon.account'

    def _generate_stock_moves(self, order):
        """ Generate a stock move for each product of the provided sales order.

        :param recordset order: The sales order to generate the stock moves for, as a `sale.order`
                                record.
        :return: The generated stock moves.
        :rtype: recordset of `stock.move`
        """
        carrier_env = self.env["delivery.carrier"]
        customers_location = self.env.ref('stock.stock_location_customers')
        sync_log_env = self.env["amazon.synchronization.log"]
        fba_warehouses = self.env['stock.warehouse'].search([
            ("is_fba_wh", "=", True),
        ])
        move_env = self.env['stock.move']
        lines_to_create_moves = order.order_line.filtered(
            lambda l: l.product_id.detailed_type != 'service'
                and not l.display_type
                and l.amz_shipment_id
                and l.ship_from_country_id
                and not l.move_ids
        )
        picking_dict = {}
        for order_line in lines_to_create_moves:
            ship_from_wh = fba_warehouses.filtered(
                lambda wh: wh.partner_id.country_id == order_line.ship_from_country_id
            )
            if not ship_from_wh:
                sync_log_env.create({
                    'account_id': self.id,
                    'operation_type': 'import_order',
                    'action_type': 'skip_line',
                    'log_type': 'not_found',
                    'message': "Please create FBA Warehouse for country %s" % (
                        order_line.ship_from_country_id.name),
                    'user_id': self.env.user.id,
                    "amazon_order_ref": "%s | %s" % (order.amazon_order_ref, order_line.amazon_item_ref),
                })
                continue
            else:
                ship_from_wh = ship_from_wh[0]
            if ship_from_wh.id not in picking_dict:
                group = self.env['procurement.group'].create({
                    'name': order.name,
                    'move_type': order.picking_policy,
                    'sale_id': order.id,
                    'partner_id': order.partner_shipping_id.id,
                })
                picking_vals = {
                    "origin": order.name,
                    "partner_id": order.partner_shipping_id.id,
                    "picking_type_id": ship_from_wh.out_type_id.id,
                    "location_id": ship_from_wh.lot_stock_id.id,
                    "location_dest_id": customers_location.id,
                    "amazon_shipment_id": order_line.amz_shipment_id,
                    "date_done": order_line.amz_shipment_date,
                }
                if order.is_amz_outbound_order:
                    picking_vals["carrier_tracking_ref"] = order_line.amz_transaction_inv_id
                    carrier = carrier_env.search([("name", "=", order_line.ship_from_address)])
                    if not carrier:
                        carrier = carrier_env.create({
                            "name": order_line.ship_from_address,
                            "product_id": self.env.ref("delivery.product_product_delivery").id,
                        })
                    picking_vals["carrier_id"] = carrier.id
                picking = self.env["stock.picking"].create(picking_vals)
                picking_dict[ship_from_wh.id] = (picking.id, group.id)

            stock_move = move_env.create({
                'name': _('Amazon move : %s', order.name),
                'origin': order.name,
                'company_id': self.company_id.id,
                'product_id': order_line.product_id.id,
                'product_uom_qty': order_line.product_uom_qty,
                'product_uom': order_line.product_uom.id,
                'location_id': ship_from_wh.lot_stock_id.id,
                'location_dest_id': customers_location.id,
                'state': 'confirmed',
                'sale_line_id': order_line.id,
                # 'fba_warehouse_id': ship_from_wh.id,
                "picking_id": picking_dict[ship_from_wh.id][0],
                "group_id": picking_dict[ship_from_wh.id][1],
            })
            stock_move._action_assign()
            stock_move._set_quantity_done(order_line.product_uom_qty)
            stock_move._action_done()
