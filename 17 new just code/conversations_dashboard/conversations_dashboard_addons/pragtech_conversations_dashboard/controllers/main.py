from odoo import http
from odoo.http import request


class Conversation(http.Controller):

    @http.route('/web#action=164&cids=1&menu_id=115', type='http', auth='public')
    def conversation_info(self, **kwargs):
        try:
            # users = request.env['facebook.messenger'].sudo().search([])
            #sql = request.env.cr.execute("select name from patient_prescription")
            #return "Thanks for watching"
            print("users")
        except:
            return "<h1>Can't access API</h1>"

        return request.render("pragtech_conversations_dashboard.conversations.Sidebar", {'patients': users})

