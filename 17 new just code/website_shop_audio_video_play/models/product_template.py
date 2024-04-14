# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    custom_file_attachment_id = fields.Many2one(
        'ir.attachment', 
        string='Attach Audio/Video',
        domain="[('res_id','=',id),('res_model','=','product.template')]",
        copy=False
    )
    custom_file_type = fields.Selection([
        ('none', 'None'),
        ('audio', 'Play Audio'),
        ('video', 'Play Video'),
    ], 
        required=True, 
        default='none',
        string="Widget Player",
        copy=False
    )
    custom_video_type = fields.Selection([
        ('url', 'URL Input'),
        ('attachment', 'Attchment Input'),
    ], 
        required=False,
        string="Video Input",
        default='url',
        copy=False
    )
    custom_url = fields.Char(
        string="Video URL",
    )