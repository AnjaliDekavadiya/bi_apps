from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    lunch_face_recognition = fields.Boolean(string="Face Recognition", default=False)