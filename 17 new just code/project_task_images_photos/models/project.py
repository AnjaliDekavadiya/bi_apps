# -*- coding: utf-8 -*-


from odoo import api, fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_image1_custom = fields.Image(
        string='Image1'
    )
    task_image2_custom = fields.Image(
        string='Image2'
    )
    task_image3_custom = fields.Image(
        string='Image3'
    )
    task_image4_custom = fields.Image(
        string='Image4'
    )
    task_image5_custom = fields.Image(
        string='Image5'
    )
    task_image6_custom = fields.Image(
        string='Image6'
    )
  