from odoo import _, http, fields
from odoo.http import request
from odoo.exceptions import AccessError

from odoo.addons.lunch.controllers.main import LunchController as LunchController

class LunchKioskMode(http.Controller):
    
    @http.route('/lunch_kiosk_mode_adv/lunch_kiosk_keepalive', auth='user', type='json')
    def lunch_kiosk_keepalive(self):
        request.session.touch()
        return {}
    
    @http.route('/lunch_kiosk_mode_adv/loadLabeledImages/', type='json', auth="none")
    def load_lunch_labeled_images(self):
        descriptions = []
        users = request.env['res.users'].sudo().search([])
        for user in users:
            descriptors = []
            for faces in user.user_faces:
                if faces.descriptor and faces.descriptor != 'false':
                    descriptors.append(faces.descriptor)
            if descriptors:
                vals = {
                    "label": user.id,
                    "descriptors": descriptors,
                    "name": user.name,
                }
                descriptions.append(vals)
        return descriptions

class LunchControllerKiosk(LunchController):

    def _check_user_impersonification(self, user_id=None):
        if (user_id and request.env.uid != user_id and not (request.env.user.has_group('lunch.group_lunch_manager') or request.env.user.has_group('lunch_kiosk_mode_adv.group_lunch_kiosk'))):
            raise AccessError(_('You are trying to impersonate another user, but this can only be done by a lunch manager'))
    
    
        
