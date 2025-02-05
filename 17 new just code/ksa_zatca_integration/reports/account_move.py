from odoo import api, fields, models, exceptions
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter
from odoo.tools import mute_logger
from odoo.http import request
from datetime import timedelta
import lxml.etree as ET
import logging
import base64
import qrcode
import io

_zatca = logging.getLogger('Zatca Debugger for account.move :')


class AccountMoveReport(models.Model):
    _inherit = 'account.move'

    def _default_currency_id(self):
        self.invoice_multi_currency_id = self.currency_id

    invoice_multi_currency_id = fields.Many2one('res.currency', string='Invoice Report Currency',
                                                compute="_default_currency_id")

    def get_tax_amount(self):
        data = 0.0
        if self.invoice_line_ids:
            for rec in self.invoice_line_ids:
                taxable_amount = rec.price_unit * rec.quantity
                data += ((rec.tax_ids[0].amount if rec.tax_ids else 0.0) * taxable_amount) / 100
        return data

    def _l10n_sa_pdf_conversion(self, collected_streams):
        is_tax_invoice = 1 if self.l10n_sa_invoice_type == 'Standard' else 0
        xml = self.zatca_hash_cleared_invoice if is_tax_invoice else self.zatca_invoice
        if not xml:
            raise exceptions.MissingError('Cleared invoice from zatca is required' if is_tax_invoice else "xml not generated.")
        if xml:
            xml_facturx = base64.b64decode(xml)
            pdf_stream = collected_streams[self.id]['stream']

            pdf_content = pdf_stream.getvalue()
            reader_buffer = io.BytesIO(pdf_content)
            reader = OdooPdfFileReader(reader_buffer, strict=False)
            writer = OdooPdfFileWriter()
            writer.cloneReaderDocumentRoot(reader)

            writer.addAttachment(self.zatca_invoice_name, xml_facturx, subtype='text/xml')

            try:
                writer.convert_to_pdfa()
            except Exception as e:
                _zatca.exception("Error while converting to PDF/A: %s", e)

            content = self.env['ir.qweb']._render('account_edi_ubl_cii.account_invoice_pdfa_3_facturx_metadata',
                {
                    'title': self.name,
                    'date': fields.Date.context_today(self),
                },
            )
            writer.add_file_metadata(content.encode())

            pdf_stream.close()
            writer_buffer = io.BytesIO()
            writer.write(writer_buffer)
            collected_streams[self.id]['stream'] = writer_buffer
            reader_buffer.close()
            # writer_buffer.close()
        return collected_streams

    def print_einv_b2b(self):
        is_tax_invoice = 1 if self.l10n_sa_invoice_type == 'Standard' else 0
        if not is_tax_invoice:
            raise exceptions.MissingError("Not a standard invoice.")
        if not self.zatca_invoice:
            raise exceptions.MissingError("Xml not created yet.")
        if not self.zatca_onboarding_status:
            raise exceptions.MissingError("Qr code can't be created with CCSID.")
        if not self.zatca_hash_cleared_invoice:
            raise exceptions.MissingError("Cleared invoice from zatca is required.")
        return self.env.ref('ksa_zatca_integration.report_e_invoicing_b2b').report_action(self)

    def print_einv_b2c(self):
        is_tax_invoice = 1 if self.l10n_sa_invoice_type == 'Standard' else 0
        if is_tax_invoice:
            raise exceptions.MissingError("Not a simplified invoice.")
        if not self.zatca_invoice:
            raise exceptions.MissingError("Xml not created yet.")
        if not self.zatca_onboarding_status:
            raise exceptions.MissingError("Qr code can't be created with CCSID.")
        return self.env.ref('ksa_zatca_integration.report_e_invoicing_b2c').report_action(self)

    def get_invoice_type_code(self):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        ksa_2 = xml_file.find("//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode").attrib.get('name', '')
        return ksa_2

    def get_bt_131(self, id):
        id = str(int(id))
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        bt_131_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(bt_131_find).getparent()
        bt_131 = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount')
        return float(bt_131.text) if float(bt_131.text) else 0

    def get_bt_136(self, id):
        id = str(int(id))
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        bt_136_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(bt_136_find).getparent()
        bg_27 = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AllowanceCharge')
        if bg_27 is None:
            return 0.0
        bt_136 = bg_27.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Amount')
        return float(bt_136.text) if float(bt_136.text) else 0

    def get_bt_146(self, id):
        id = str(int(id))
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        bt_136_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(bt_136_find).getparent()
        bg_29 = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price')
        bt_146 = bg_29.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount')
        return float(bt_146.text) if float(bt_146.text) else 0

    def get_ksa_11(self, id):
        id = str(int(id))
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        ksa_11_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(ksa_11_find).getparent()
        tax_total = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return 0.0
        ksa_11 = tax_total.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount')
        return float(ksa_11.text) if float(ksa_11.text) else 0

    def get_ksa_12(self, id):
        id = str(int(id))
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        # LineExtensionAmount
        ksa_12_find = "//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID[.='" + str(id) + "']"
        bt_126 = xml_file.find(ksa_12_find).getparent()
        tax_total = bt_126.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return 0.0
        ksa_12 = tax_total.find('{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RoundingAmount')
        return float(ksa_12.text) if float(ksa_12.text) else 0

    def get_bt_120(self):
        invoice = base64.b64decode(self.zatca_invoice).decode()
        xml_file = ET.fromstring(invoice).getroottree()
        tax_total = xml_file.find('./{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
        if tax_total is None:
            return 0.0
        bt_120 = tax_total.findall('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExemptionReason')
        if not len(bt_120):
            return ""
        bt_120_text = ''
        for x in bt_120:
            bt_120_text += x.text + ", "
        return bt_120_text[:-2]

    @mute_logger('Zatca Debugger for account.move :')
    def get_qrcode(self):
        # qr = qrcode.QRCode(version=1,
        #                    box_size=10,
        #                    border=5)
        #
        # # Adding data to the instance 'qr'
        # qr.add_data(self.l10n_sa_qr_code_str)
        #
        # qr.make(fit=True)
        # img = qr.make_image(fill_color='red',
        #                     back_color='white')
        # x = img
        if not self.zatca_invoice:
            raise exceptions.MissingError("Xml not created yet.")
        if not self.zatca_onboarding_status:
            raise exceptions.MissingError("Qr code can't be created with CCSID.")

        self._compute_qr_code_str()
        _zatca.info("l10n_sa_qr_code_str:: %s", self.l10n_sa_qr_code_str)
        qr = qrcode.make(self.l10n_sa_qr_code_str)
        from PIL import Image
        import io

        def image_to_byte_array(image: Image) -> bytes:
            # BytesIO is a fake file stored in memory
            buffered = io.BytesIO()
            # image.save expects a file as a argument, passing a bytes io ins
            image.save(buffered, format=image.format)
            # Turn the BytesIO object back into a bytes object
            imgByteArr = buffered.getvalue()
            img_str = base64.b64encode(buffered.getvalue())
            return img_str

        _zatca.info("image_to_byte_array(qr).decode():: %s",image_to_byte_array(qr).decode())
        return "data:image/png;base64," + image_to_byte_array(qr).decode()
