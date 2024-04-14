import logging
from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    """
    def create_invoices(self):
        invoice = self.with_context(origin_country_id=123)._create_invoices(self.sale_order_ids)
        if self.advance_payment_method == 'delivered':
            countries = invoice.invoice_line_ids.mapped(
                'sale_line_ids.ship_from_country_id')
            if len(countries) > 1:
                country_ids = countries.ids
                first_country = country_ids.pop(0) # First invoice will have first country
                invoice.write({"ship_from_country_id": first_country})
                country_dict = dict.fromkeys(
                    country_ids,
                    self.env["account.move.line"]
                )
                lines_to_remove = self.env["account.move.line"]
                for line in invoice.invoice_line_ids:
                    cts = line.mapped('sale_line_ids.ship_from_country_id')
                    if not cts:
                        #if line.product_id.detailed_type == "product":
                        lines_to_remove |= line
                        continue
                    if len(cts) > 1:
                        # Means a same product is delivered from multiple Countries
                        # (quantiy > 1)
                        sub_ct_dict = dict.fromkeys(cts.ids, 0.0)
                        for move in line.mapped('sale_line_ids.move_ids'):
                            sub_ct_dict[move.ship_from_country_id.id] +=\
                                move.quantity_done
                        orig_line_new_qty = sub_ct_dict.pop(first_country)
                        for ct, quantity in sub_ct_dict.items():
                            new_line = line.copy(default={
                                "quantity": quantity,
                                "tax_ids": [(6, 0, line.tax_ids.ids)],
                                "sale_line_ids": [(6, 0, line.sale_line_ids.ids)],
                            })
                            country_dict[ct] |= new_line
                        line.write({"quantity": orig_line_new_qty})
                    elif cts.id == first_country:
                        continue
                    else:
                        country_dict[cts.id] |= line

                lines_to_remove.unlink()
                for ct_id, lines in country_dict.items():
                    new_inv = invoice.copy(default={
                        "ship_from_country_id": ct_id,
                        "line_ids": [],
                    })
                    # new_inv.write({"invoice_line_ids": [(5, 0, 0)]})
                    lines.write({"move_id": new_inv.id})
                    lines._compute_tax_ids()
            else:
                lines_to_remove = self.env["account.move.line"]
                for line in invoice.invoice_line_ids:
                    cts = line.mapped('sale_line_ids.ship_from_country_id')
                    if not cts:
                        # if line.product_id.detailed_type == "product":
                        lines_to_remove |= line
                lines_to_remove.unlink()
                invoice.write({"ship_from_country_id": countries.id})

        if self.env.context.get('open_invoices'):
            return self.sale_order_ids.action_view_invoice()

        return {'type': 'ir.actions.act_window_close'}
    """

    def create_invoices(self):
        invoice = self._create_invoices(self.sale_order_ids)
        if self.advance_payment_method == 'delivered':
            shipments = list(set(invoice.invoice_line_ids.mapped(
                'sale_line_ids.amz_shipment_id')))
            if False in shipments:
                shipments.remove(False)
            lines_to_remove = self.env["account.move.line"]
            if len(shipments) > 1:
                first_shipment = shipments.pop(0) # First invoice will have first shipment
                first_country = invoice.invoice_line_ids.mapped("sale_line_ids").\
                    filtered(lambda sl: sl.amz_shipment_id == first_shipment).\
                        mapped("ship_from_country_id")
                invoice.write({
                    "ref": self.sale_order_ids.mapped("name")[0],
                    "payment_reference": self.sale_order_ids.mapped("name")[0],
                    "invoice_date": invoice.invoice_line_ids.mapped(
                    "sale_line_ids.amz_shipment_date")[0],
                    "ship_from_country_id": first_country.id,
                })
                shipment_dict = dict.fromkeys(
                    shipments,
                    self.env["account.move.line"]
                )
                # lines_to_remove = self.env["account.move.line"]
                for line in invoice.invoice_line_ids:
                    shpmnts = list(set(line.mapped('sale_line_ids.amz_shipment_id')))
                    if False in shpmnts:
                        shpmnts.remove(False)
                    if not shpmnts:
                        # if line.product_id.detailed_type == "product":
                        lines_to_remove |= line
                        continue
                    if len(shpmnts) > 1:
                        # Means a same product is delivered from multiple shipments
                        # (quantiy > 1)
                        sub_shpmnt_dict = dict.fromkeys(shpmnts, 0.0)
                        for move in line.mapped('sale_line_ids.move_ids'):
                            sub_shpmnt_dict[move.sale_line_id.amz_shipment_id.id] +=\
                                move.quantity_done
                        orig_line_new_qty = sub_shpmnt_dict.pop(first_shipment)
                        for sm, quantity in sub_shpmnt_dict.items():
                            new_line = line.copy(default={
                                "quantity": quantity,
                                "tax_ids": [(6, 0, line.tax_ids.ids)],
                                "sale_line_ids": [(6, 0, line.sale_line_ids.ids)],
                            })
                            shipment_dict[sm] |= new_line
                        line.write({"quantity": orig_line_new_qty})
                    elif shpmnts[0] == first_shipment:
                        continue
                    else:
                        # Shipment ID is 1 and different from first shipment
                        shipment_dict[shpmnts[0]] |= line

                lines_to_remove.unlink()
                for _, lines in shipment_dict.items():
                    country = lines.mapped('sale_line_ids.ship_from_country_id')
                    new_inv = invoice.with_context(origin_country_id=country.id).\
                        copy(default={
                            "ref": invoice.ref,
                            "payment_reference": invoice.payment_reference,
                            "ship_from_country_id": country.id,
                            "line_ids": [],
                            "invoice_line_ids": [(5, 0, 0)]
                        })
                    # new_inv.write({"invoice_line_ids": [(5, 0, 0)]})
                    lines.write({"move_id": new_inv.id})
                    lines._compute_tax_ids()
            elif len(shipments) == 1:
                for line in invoice.invoice_line_ids:
                    cts = line.mapped('sale_line_ids.ship_from_country_id')
                    if not cts:
                        # if line.product_id.detailed_type == "product":
                        lines_to_remove |= line
                lines_to_remove.unlink()
                invoice.write({
                    "ref": self.sale_order_ids.mapped("name")[0],
                    "payment_reference": self.sale_order_ids.mapped("name")[0],
                    "invoice_date": invoice.invoice_line_ids.mapped(
                    "sale_line_ids.amz_shipment_date")[0],
                    "ship_from_country_id": invoice.invoice_line_ids.mapped(
                        'sale_line_ids.ship_from_country_id').id
                })
            else:
                invoice.write({
                    "ref": self.sale_order_ids.mapped("name")[0],
                    "payment_reference": self.sale_order_ids.mapped("name")[0],
                    "invoice_date": fields.Date.today(),  # self.sale_order_ids[0].date_order,
                    # invoice.invoice_line_ids.mapped("sale_line_ids.amz_shipment_date")[0],
                    "ship_from_country_id": self.sale_order_ids.mapped(
                        "warehouse_id.partner_id.country_id").id,
                })
            invoice.invoice_line_ids._compute_tax_ids()
        if self.env.context.get('open_invoices'):
            return self.sale_order_ids.action_view_invoice()

        return {'type': 'ir.actions.act_window_close'}

