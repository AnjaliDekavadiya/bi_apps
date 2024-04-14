# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReportingTemplateTemplateDesign(models.Model):
    _name = 'report.template.design'

    name = fields.Char(required=True)
    name_technical = fields.Char(required=True)
    report_name = fields.Char()
    parameters = fields.Text()
    # image = fields.Binary() # DEPRECATED

    # def parameter_values(self):
    #     self.ensure_one()
    #     import ast
    #     return ast.literal_eval(self.parameters)

