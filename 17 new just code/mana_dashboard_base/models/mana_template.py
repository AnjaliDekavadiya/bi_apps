# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ManaDashboardTemplate(models.Model):
    '''
    Mana Template
    '''
    _name = 'mana_dashboard.template'
    _description = 'Mana Template'

    name = fields.Char(string="Template Name", required=True)
    component_type = fields.Char(string="Component Type")
    dashboard_template_id = fields.Many2one(
        comodel_name='mana_dashboard.dashboard_template',
        string='Dashboard Template',
        ondelete='set null')
    template = fields.Text(string='Template')
    has_template = fields.Boolean(string='Has Template', default=True)
    disable_children = fields.Boolean(string='Disable Children', default=False)
    disable_first_child = fields.Boolean(string='Disable First Child', default=False)
    demo_data = fields.Text(string='Demo Data')
    demo_template = fields.Text(string='Demo Template')
    has_demo_template = fields.Boolean(string='Has Demo Template', default=True)
    category = fields.Char(string='Category')
    type = fields.Char(string='Type')
    styles = fields.Text(string='Styles')
    has_styles = fields.Boolean(string='Has Styles', default=True)
    scripts = fields.Text(string='Scripts')
    has_scripts = fields.Boolean(string='Has Scripts', default=True)
    default_scripts = fields.Text(
        string='Default Scripts',
        help='Default Scripts, script when no data source is set')
    preview = fields.Binary(string='Preview')
    data_validate = fields.Text(string='Data Validate', help='Python Code for Data Source Validate')
    multi_data_source = fields.Boolean(string='Multi Data Source', default=False)
    default_code = fields.Text(string='Example Code', help='Example Code')
    default_json = fields.Text(string='Example Json', help='Example Json')
    default_sql = fields.Text(string='Example Sql', help='Example Sql')
    default_data_source_type = fields.Many2one(
        comodel_name='mana_dashboard.data_source_type',
        default=lambda self: self.env.ref('mana_dashboard_base.data_source_model'),
        string='Default Data Source Type',
        help='Default Data Source Type')
    default_result_type = fields.Many2one(
        comodel_name='mana_dashboard.result_type',
        default=lambda self: self.env.ref('mana_dashboard_base.result_type_standard'),
        string='Default Result Type',
        help='Default Result Type')
    need_measure = fields.Boolean(string='Need Measure', default=True)
    need_category = fields.Boolean(string='Need Category', default=True)
    need_column_aggregation = fields.Boolean(string='Need Column Aggregation', default=False)
    is_custom = fields.Boolean(string='Is Custom', default=False)
    preview_background_color = fields.Char(
        string='Preview Background Color',
        default='#ffffff')
    get_previous_data = fields.Boolean(string='Get Previous Data', default=False)
    help = fields.Html(string='Help', translate=True)

    supported_data_source_types = fields.Many2many(
        comodel_name='mana_dashboard.data_source_type',
        relation='mana_dashboard_template_data_source_type_rel',
        column1='template_id',
        column2='data_source_type_id',
        string='Supported Data Source Types', 
        help='Supported Data Source Types, if empty, all types are supported')

    supported_result_types = fields.Many2many(
        comodel_name='mana_dashboard.result_type',
        relation='mana_dashboard_template_data_result_type_rel',
        column1='template_id',
        column2='data_result_type_id',
        string='Supported Data Result Types', 
        help='Supported Data Result Types, if empty, all types are supported')
    
    supported_series_types = fields.Many2many(
        comodel_name='mana_dashboard.series_type',
        relation='mana_dashboard_template_data_series_type_rel',
        column1='template_id',
        column2='data_series_type_id',
        string='Supported Series Types',
        help='Supported Series Types')
    
    data_source_mode = fields.Selection(
        string='Data Source Mode',
        selection=[
            ('single', 'Single'), 
            ('multi', 'Multi'),
            ('mixed', 'Mixed')],
        default='single')

    def get_image_url(self):
        """
        get image url
        """
        self.ensure_one()
        return '/web/image/mana_dashboard.template/%s/preview' % self.id
