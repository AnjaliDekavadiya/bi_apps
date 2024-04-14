from odoo import http, _
from odoo.http import request
import json


class TailoringController(http.Controller):
    @http.route('/', type='http', auth="public", website=True)
    def tailor_page(self, **kw):
        men = request.env.ref('pragtech_tailoring_management.product_category_men').id
        women = request.env.ref('pragtech_tailoring_management.product_category_women').id
        kids = request.env.ref('pragtech_tailoring_management.product_category_kids').id
        vals = {
            'men': men,
            'women': women,
            'kids': kids,
        }
        return request.render('pragtech_tailoring_management.home_page_template', vals)


class FeedbackController(http.Controller):

    @http.route('/feedback/page/', type='http', auth="public", website=True)
    def feedback_page(self, **kw):
        if not request.website.is_public_user():
            user = request.env.user
            orders = request.env['sale.order'].search([('partner_id', '=', user.partner_id.id)])
            return request.render('pragtech_tailoring_management.feedback_page_template', {'user': user, 'orders': orders})
        else:
            alert_message = "To provide feedback, please log in or create an account."
            return """
                <script>
                    alert('%s');
                    window.location.href = '/web/login';
                </script>
            """ % alert_message

    @http.route('/feedback/submit', type='http', auth="public", website=True)
    def submit_feedback(self, **post):
        Feedback = request.env['tailoring.feedback']
        user = request.env.user

        selected_order_id = post.get('order_id')
        Feedback.create({
            'name': user.name,
            'email': user.email,
            'feedback': post.get('feedback'),
            'order_id': selected_order_id,
        })

        return request.render('pragtech_tailoring_management.home_page_template', {'user': user})


class TestimonialController(http.Controller):

    @http.route('/fetch_testimonials', type='http', auth="public", website=True, csrf=False)
    def fetch_testimonials(self, **kw):
        testimonials = request.env['tailoring.feedback'].search([])
        testimonial_data = []

        for testimonial in testimonials:
            testimonial_data.append({
                'name': testimonial.name,
                'feedback': testimonial.feedback
            })

        return json.dumps(testimonial_data)
