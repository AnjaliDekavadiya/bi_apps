from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError

class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="user", website=True)
    def checkout(self, **post):
        print("clicked")

        sale_order = request.website.sale_get_order()

        if sale_order:
            user = request.env.user
            for order_line in sale_order.order_line:
                if order_line.product_id:
                    measurement_found = False
                    customer_measurement = request.env['tailoring.customer.measurement'].sudo().search([
                        ('order_id', '=', sale_order.id),
                        ('customer_id', '=', user.id),
                        ('state', '=', 'draft'),
                        ('cloth_type', '=', order_line.product_id.cloth_type.id),
                    ])

                    if customer_measurement:
                        for measurement in customer_measurement.measurement_ids:
                            if measurement.measures:
                                measurement_found = True
                                break

                    if not measurement_found:
                          return """
                        <script>
                            alert("Please provide the measurements for the selected product: %s");
                            window.location.href = '/shop/cart';
                        </script>
                        """ % order_line.product_id.display_name
        return super(CustomWebsiteSale, self).checkout(**post)
