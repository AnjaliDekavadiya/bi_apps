# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProjectQualityReason(models.Model):
    
    _name = 'project.quality.reason'
    _description = "Quality Reason"
    _rec_name = 'name'

    name = fields.Char(
        string= 'Name',
        required= True
    )
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       
