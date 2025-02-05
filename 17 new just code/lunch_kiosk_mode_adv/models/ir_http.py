from odoo import models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super(Http, self).session_info()
        if self.env.user.has_group('base.group_user'):
            company = self.env.company
            result['lunch_face_recognition'] = company.lunch_face_recognition       
        return result