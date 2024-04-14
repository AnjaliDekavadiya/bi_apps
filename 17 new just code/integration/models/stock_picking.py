# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

from ..tools import PickingLine, PickingSerializer, SaleTransferSerializer


PKG_CTX = dict(
    skip_sms=True,
    skip_expired=True,
    skip_immediate=True,
    skip_backorder=True,
    skip_sanity_check=False,
    skip_dispatch_to_external=True,
)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tracking_exported = fields.Boolean(
        string='Is Tracking Exported?',
        default=False,
        help='This flag allows us to define if tracking code for this picking was exported '
             'for external integration. It helps to avoid sending same tracking number twice. '
             'Basically we need this flag, cause different carriers have different type of '
             'integration. And sometimes tracking reference is added to stock picking after it '
             'is validated and not at the same moment.',
    )

    def write(self, vals):
        # if someone add `carrier_tracking_ref` after picking validation
        picking_done_ids = self.filtered(
            lambda x: x.state == 'done' and not x.carrier_tracking_ref
        )
        res = super(StockPicking, self).write(vals)

        picking_done_update_ids = picking_done_ids.filtered(
            lambda x: x.state == 'done' and x.carrier_tracking_ref
        )
        for order in picking_done_update_ids.mapped('sale_id'):
            if order.check_is_order_shipped():
                order.order_export_tracking()

        return res

    def _to_export_format(self, integration):
        self.ensure_one()

        carrier, carrier_tracking_ref, serialized_lines = str(), str(), list()

        for move_line in self.move_ids:
            sale_line = move_line.sale_line_id

            external_so_line_id = sale_line.to_external(integration)
            qty_demand = int(sale_line.qty_delivered)

            if external_so_line_id and qty_demand:
                qty_done = int(move_line.quantity)
                is_kit = False

                if getattr(move_line, 'bom_line_id', False):
                    is_kit = True
                    qty_done = qty_demand

                picking_line = PickingLine(external_so_line_id, qty_demand, qty_done, is_kit)
                serialized_lines.append(picking_line)

        if self.carrier_id:
            carrier = self.carrier_id.get_external_carrier_code(integration)
            if not carrier:
                carrier = self.carrier_id.name

        _args = (
            self.name,
            carrier,
            self.carrier_tracking_ref or carrier_tracking_ref,
            serialized_lines,
            self.id,
            bool(self.backorder_id),
            getattr(self, 'is_dropship', False),
        )
        return PickingSerializer(*_args)

    def to_export_format_multi(self, integration):
        tracking_data_list = list()

        for rec in self:
            picking_custom_entity = rec._to_export_format(integration)
            tracking_data_list.append(picking_custom_entity)

        transfer = SaleTransferSerializer(tracking_data_list)

        transfer.squash()
        tracking_data = transfer.dump()

        return tracking_data

    def _auto_validate_picking(self):
        """Set quantities automatically and validate the pickings."""
        for picking in self._pickings_to_handle():
            for move in picking.move_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')
            ):
                if (
                    float_compare(
                        move.quantity,
                        move.product_qty,
                        precision_rounding=move.product_id.uom_id.rounding,
                    )
                    == -1
                ):
                    for move_line in move.move_line_ids:
                        move_line.quantity = move_line.quantity_product_uom

            try:
                # Let's rely on the `_sanity_check` (skip_sanity_check=False)
                # standard method to get verbose error
                picking.with_context(**PKG_CTX).button_validate()
            except UserError as ex:
                return False, f'[{picking.display_name}]: {ex.args[0]}'

        # Let's check the presence of pickings for validation,
        # as there might be a back order created.
        pickings = self.mapped('sale_id').picking_ids._pickings_to_handle()
        if pickings:
            return pickings._auto_validate_picking()

        if any(self.filtered(lambda x: x.state == 'waiting')):
            message = _('%s is not ready to be validated. Waiting another operation.') % ', '.join(
                self.filtered(lambda x: x.state == 'waiting').mapped('display_name'),
            )
            return False, message

        return True, _('[%s] validated pickings successfully.') % ', '.join(
            self.mapped('display_name')
        )

    def _pickings_to_handle(self):
        return self.filtered(lambda x: x.state in ('confirmed', 'assigned'))

    def button_validate(self):
        """
        Override button_validate method to called method, that check order is shipped or not.
        """
        res = super(StockPicking, self).button_validate()

        if res is not True:
            return res

        self._run_integration_picking_hooks()

        return res

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()

        if res is not True:
            return res

        self._run_integration_picking_hooks()

        return res

    def _run_integration_picking_hooks(self):
        # Access orders as sudo to avoid issues with missed access rights
        # Person who works with pickings can have no access to sales orders
        orders = self.sudo().mapped('sale_id')

        # If order is not from integration - do nothing
        orders = orders.filtered('integration_id')

        for order in orders:
            if not order.check_is_order_shipped():
                continue

            order._integration_shipped_order_hook()
            order.order_export_tracking()
