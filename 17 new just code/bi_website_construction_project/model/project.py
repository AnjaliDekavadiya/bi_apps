# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProjectCategory(models.Model):
    _name = 'project.category'
    _description = 'project category details'

    name = fields.Char(string="Name")
    image = fields.Binary('Image')
    project_ids = fields.One2many('project.project', 'category_id', 'Project')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    image = fields.Binary(string="Images")
    category_id = fields.Many2one('project.category', string="Category")
    brochure_ids = fields.Many2many('ir.attachment', string="Brochure Attachment")
    project_image_ids = fields.One2many('ir.attachment', 'project_image_id', 'Project Images')
    gallery_images_ids = fields.One2many('ir.attachment', 'project_gallery_image_id', 'Gallery Images')
    project_features = fields.Html(string="Project Features and Amenties")
    specification = fields.Html(string="Project Specification")
    contact_us = fields.Html(string="Contact Us")
    project_floor_plan_ids = fields.One2many("ir.attachment", "project_floor_id", string="Project Floor Plan")
    project_location_plan_ids = fields.One2many("ir.attachment", "project_location_id", string="Project Location Plan")


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    project_image_id = fields.Many2one('project.project', 'Project More Image')
    project_gallery_image_id = fields.Many2one('project.project', 'Project Image')
    project_floor_id = fields.Many2one('project.project', 'Project Floor Plan Image')
    project_location_id = fields.Many2one('project.project', 'Project Location Plan Image')


class Website(models.Model):
    _inherit = "website"

    def get_project_category(self):
        project_category_ids = self.env['project.category'].sudo().search([])
        return project_category_ids

    def get_project(self, project_id):
        project_ids = self.env['project.project'].search([('category_id', '=', project_id)])
        return project_ids

    def get_project_more_images(self, project_id):
        project_ids = self.env['ir.attachment'].sudo().search([('project_image_id', '=', project_id)])
        return project_ids
