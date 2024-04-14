from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.osv import expression


class AmazonReportTypeCategory(models.Model):
    _name = 'amazon.report.type.category'
    _description = "Amazon Report Type Category"
    _rec_name = 'complete_name'

    name = fields.Char(string="Report Category")
    complete_name = fields.Char(
        string="Full Category Name",
        compute='_compute_complete_name',
        recursive=True, store=True
    )
    description = fields.Char(string="Description")
    parent_id = fields.Many2one(
        "amazon.report.type.category",
        string="Parent Category"
    )
    child_ids = fields.One2many(
        comodel_name='amazon.report.type.category',
        inverse_name='parent_id',
        string='Child Categories')

    @api.depends('name', 'parent_id', 'parent_id.name')
    def _compute_complete_name(self):
        for categ in self:
            if categ.parent_id:
                categ.complete_name = '%s/%s' % (categ.parent_id.name, categ.name)
            else:
                categ.complete_name = categ.name


class AmazonReportType(models.Model):
    _name = 'amazon.report.type'
    _description = "Amazon Report Type"
    _rec_names_search = ['name', 'technical_name']

    name = fields.Char(string="Report Type")
    technical_name = fields.Char(string="Technical Name")
    description = fields.Char(string="Description")
    category_id = fields.Many2one(
        "amazon.report.type.category",
        string="Report Category"
    )
