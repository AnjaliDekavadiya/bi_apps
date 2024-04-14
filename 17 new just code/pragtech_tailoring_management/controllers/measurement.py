from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError, ValidationError

class MeasurementController(http.Controller):

    @http.route('/store_measurements', type='http', auth="public", csrf=True, website=True, method=['POST'])
    def measurement_submit(self, **kw):
            print("kwwwwwwwwwwwwwwwwww",kw)
            # line = kw.get('line')
            # print("lineeeeeeeeeeeeeee",line)
            line_id = int(kw.get('line_id'))
            print(line_id)
            cloth_type = int(kw.get('cloth_type'))

            user = request.env.user

            sale_order = request.website.sale_get_order()
            if not sale_order:
                raise UserError(_("No active sale order found."))


            if any(kw.get(key) for key in kw if key.startswith('measurement_')):
                existing_measurement_record = request.env['tailoring.customer.measurement'].sudo().search([
                    ('cloth_type', '=', cloth_type),
                    ('state', '=', 'draft'),
                    ('customer_id', '=', user.id),
                ])

                measurement_data = []

                for field_name, value in kw.items():
                    if field_name.startswith('measurement_'):
                        measurement_name = field_name.replace('measurement_', '')
                        measure_value = float(value)
                        measurement_data.append((0, 0, {
                            'name': measurement_name,
                            'measures': measure_value,
                            'uom_id': request.env.ref('uom.product_uom_cm').id,
                        }))


                if existing_measurement_record:
                    existing_measurement_record.write({'measurement_ids': [(5, 0, 0)]})
                    existing_measurement_record.write({'measurement_ids': measurement_data})
                    existing_measurement_record.write({
                        'state': 'draft'
                    })
                else:
                    request.env['tailoring.customer.measurement'].sudo().create({
                        'line_id' : line_id,
                        'order_id': sale_order.id,
                        'cloth_type': cloth_type,
                        'measurement_ids': measurement_data,
                        'customer_id': user.id,
                        'state': 'draft',
                    })
                if line_id:
                    sale_order_line_id = request.env['sale.order.line'].sudo().browse(line_id)
                    sale_order_line_id.done = True
                    

                return request.redirect(request.httprequest.referrer or '/')
            else:
                raise UserError("Please submit measurements before proceeding.")
            
