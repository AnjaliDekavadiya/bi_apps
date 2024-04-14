import base64
import json
import logging
import time
from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    # warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    ship_from_country_id = fields.Many2one(
        "res.country", string="Ship From Country")
    is_pushed_to_amz = fields.Boolean("Is Pushed to Amazon", default=False)

    def amazon_upload_pdf_invoice(self):
        feed_env = self.env['feed.submission.log']
        pushed_invoices = self.env["account.move"]
        for invoice in self:
            if (not invoice.ship_from_country_id or invoice.is_pushed_to_amz or
                invoice.state != 'posted' or
                invoice.move_type not in ['out_invoice', 'out_refund']):
                continue
            sale_lines = invoice.invoice_line_ids.mapped('sale_line_ids')
            sale_order = sale_lines.mapped('order_id')[0]
            total_tax_amount = sum(sale_lines.mapped('amz_total_tax_line_amount'))
            # if not total_tax_amount:
            #     total_tax_amount = invoice.amount_tax
            total_net_amount = sum(sale_lines.mapped('amz_total_net_line_amount'))
            # if not total_net_amount:
            #     total_net_amount = invoice.amount_untaxed
            feed_options = {
                'OrderId': sale_order.amazon_order_ref,
                'InvoiceNumber': invoice.name,
                'TotalVATAmount': round(total_tax_amount, 2),
                'TotalAmount': round(total_tax_amount + total_net_amount, 2),
                'ShippingId': ','.join(set(sale_lines.mapped("amz_shipment_id"))),
                'DocumentType': "Invoice",
            }

            if invoice.move_type == 'out_refund':
                feed_options.update({
                    'DocumentType': 'CreditNote',
                    'TransactionId': sale_lines[0].amz_transaction_refund_id,
                    'TotalVATAmount': round(invoice.amount_tax_signed, 2),
                    'TotalAmount': round(invoice.amount_total_signed, 2),
                })

            invoice_pdf = self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices", invoice.id)
            #options = ';'.join('metadata:%s=%s' % (key, val) for key, val in feed_options.items())
            options = {'metadata:%s' % key: val for key, val in feed_options.items()}
            #_logger.info('Feed Options %s' % options)

            feed_env.with_context().create({
                'account_id': sale_order.amz_account_id.id,
                'feed_message': base64.b64encode(invoice_pdf[0]),
                'feed_type': 'UPLOAD_VAT_INVOICE',
                'amz_marketplace_ids': [(6, 0, [sale_order.amz_marketplace_id.id])],
                'feed_options': json.dumps(options),
            })
            time.sleep(3)
            pushed_invoices |= invoice
            # self.env.cr.commit()

        pushed_invoices.write({'is_pushed_to_amz': True})
        return True
