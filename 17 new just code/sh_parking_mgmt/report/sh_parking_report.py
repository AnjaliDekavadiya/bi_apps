# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api
import base64
from io import BytesIO
try:
    import qrcode
except ImportError:
    qrcode = None


class ParkingReport(models.AbstractModel):
    _name = 'report.sh_parking_mgmt.sh_parking_report_template'

    @api.model
    def sh_qr_code_generate(self, product_url):
        qr_code = product_url
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code)
        qr.make(fit=True)

        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_code_image = base64.b64encode(temp.getvalue())
        return qr_code_image

    @api.model
    def _get_report_values(self, docids, data=None):

        company_id = data['company_id']
        sh_subslot_id = data['sh_subslot_id']
        sh_slot_id = data['sh_slot_id']
        sh_vehicle_no = data['sh_vehicle_no']
        sh_amount = data['sh_amount']
        partner_id = data['partner_id']
        qr_code_no = data['qr_code_no']
        docs = self.env['sh.parking.slot'].search(
            [
                ('id', '=', sh_slot_id[0]),
            ])
        location = docs.sh_location_id
        website = docs.company_id.website
        record = self.env['sh.parking.history'].search([
            ('name', '=', qr_code_no)
        ], limit=1)
        parking = self.sh_qr_code_generate(qr_code_no)
        vals = []

        vals.append({
            'sh_subslot_id': sh_subslot_id[1],
            'sh_slot_id': sh_slot_id[1],
            'sh_vehicle_no': sh_vehicle_no,
            'website': website,
            'location': location.complete_name,
            'sh_amount': round(sh_amount, 2),
            'partner_id': partner_id[1],
            'parking_qr': parking,
            'company_id': company_id[1],
        })

        return{
            'vals': vals,
            'record': record,
        }
