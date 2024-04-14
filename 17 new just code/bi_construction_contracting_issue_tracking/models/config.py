# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api

class IssuesTeams(models.Model):
    _name = "issue.teams"
    _description = "Issue Teams"

    name = fields.Char(string="Name")
    leader = fields.Many2one('res.users', string="Leader")


class TypeOfIssueSubject(models.Model):
    _name = "type.issue.subject"
    _description = "type issue subject"

    name = fields.Char(string="Name")


class TypeOfIssue(models.Model):
    _name = "type.issue"
    _description = "type issue"

    name = fields.Char(string="Name")


class Categories(models.Model):
    _name = "categories"
    _description = "categories"

    name = fields.Char(string="Name")


class IssueStages(models.Model):
    _name = "issue.stages"
    _description = "Issue Stages"

    name = fields.Char(string="Name")
    construction_team_id = fields.Many2one('issue.teams', string='Construction Team')
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.", default=lambda *args: 1)
    fold = fields.Boolean(string="Folded in Form")
    _defaults = {
        'sequence': lambda *args: 1
    }


class Website(models.Model):
    _inherit = "website"

    def get_category_list(self):
        category_ids = self.env['categories'].sudo().search([])
        return category_ids

    def get_project_list(self):
        project_ids = self.env['project.project'].sudo().search([])
        user = self.env['res.users'].sudo().browse(self.env['res.users']._context['uid']).partner_id.id
        partner = self.env['res.partner'].sudo().browse(
            self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id)
        projects = []
        for i in project_ids:
            if partner in i.message_partner_ids:
                projects.append(i)
        return projects
