from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lunch_face_recognition = fields.Boolean(related="company_id.lunch_face_recognition", string="Face Recognition", readonly=False)