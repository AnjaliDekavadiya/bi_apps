# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,SUPERUSER_ID, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        return self.stage_find([])
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    custom_stage_id = fields.Many2one(
        'custom.project.stage', 
        string='Stage', 
        readonly=False, 
        ondelete='restrict', 
        tracking=True, 
        index=True,
        default=_get_default_stage_id, 
        group_expand='_read_group_stage_ids',
        copy=False, 
    )

    # def stage_find(self, section_id, domain=[], order='sequence'):
    def stage_find(self, section_id, domain=[], order='sequence, id'):

        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        search_domain = []
        if section_id:
            section_ids.append(section_id)
        # perform search, return the first found
        return self.env['custom.project.stage'].search(search_domain, order=order, limit=1).id