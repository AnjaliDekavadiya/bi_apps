# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import csv
import base64


class ImportTickets(models.TransientModel):
    _name = 'import.tickets'
    _description = "Import Tickets"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    file = fields.Binary(string='File')
    file_restrict_content = fields.Char(string='Content', default='*.csv only', readonly=True)

    def import_tickets(self):
        if not self.file:
            raise UserError("No file is uploaded")
        else:
            filename = self.generate_file()
            with open(filename, "wb") as fobj:
                data = base64.b64decode(self.file)
                fobj.write(data)

            self.process_csv(filename)

    def generate_file(self):
        basename = '/tmp/import'
        suffix = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix + ".csv"])
        return filename

    def process_csv(self, file_path):
        with open(file_path, 'r', buffering=1) as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            for row in reader:
                serial_no = row[headers[0]]
                product_code = row[headers[1]]
                product_id = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
                if product_id:
                    self.create_tickets(serial_no, product_id)
                else:
                    raise UserError(_('%s not found in the product catalog') % (product_code))

    def create_tickets(self, serial_no, product_id):
        vals = {}
        product_brand = product_id.brand_id and product_id.brand_id.id or False
        stock_production_lot = self.env['stock.lot'].search([('name', '=', serial_no), ('product_id', '=', product_id.id)])
        if stock_production_lot:
            warranty_status = stock_production_lot.warranty_periods
            vals.update({
                'serial_number': stock_production_lot.name,
                'warranty_periods': warranty_status or False,
                'product_id': stock_production_lot.product_id.id,
                'partner_id': self.partner_id.id,
                'product_brand_id': product_brand,
                'date_sold': stock_production_lot.delivery_date or False
            })

        elif not stock_production_lot and product_id:
            vals.update({
                'serial_number': serial_no,
                'product_id': product_id.id,
                'partner_id': self.partner_id.id,
                'product_brand_id': product_brand
            })

        if vals:
            self.env['crm.claim'].create(vals)
