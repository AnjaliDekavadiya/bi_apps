# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_multi_branch = fields.Boolean(
        string="Branch",
        compute=lambda x: x._compute_report_option_filter('filter_multi_branch'), 
        readonly=False, 
        store=True, 
        depends=['root_report_id'],
    )

    ####################################################
    # OPTIONS: multi_branch
    ####################################################
    def _get_filter_multi_branchs(self):
        return self.env.user.company_branch_ids or []

    def _init_options_multi_branch(self, options, previous_options=None):
        if not self.filter_multi_branch:
            print('.................................................')
            return

        if previous_options and previous_options.get('multi_branch'):
            multi_branch_map = dict((opt['id'], opt['selected']) for opt in previous_options['multi_branch'] if 'selected' in opt)
        else:
            multi_branch_map = {}
        options['multi_branch'] = []

        for j in self._get_filter_multi_branchs():
            options['multi_branch'].append({
                'id': j.id,
                'name': j.name,
                'selected': multi_branch_map.get(j.id),
            })
        # Compute the name to display on the widget.
        names_to_display = []
        for branch in options['multi_branch']:
            if branch.get('selected'):
                names_to_display.append(branch.get('name'))

        if not names_to_display:
            names_to_display.append(_("All"))
        
        # Abbreviate the name
        max_nb_multi_branch_displayed = 5
        nb_remaining = len(names_to_display) - max_nb_multi_branch_displayed
        if nb_remaining == 1:
            options['name_multi_branch_group'] = ', '.join(names_to_display[:max_nb_multi_branch_displayed]) + _(" and one other")
        elif nb_remaining > 1:
            options['name_multi_branch_group'] = ', '.join(names_to_display[:max_nb_multi_branch_displayed]) + _(" and %s others", nb_remaining)
        else:
            options['name_multi_branch_group'] = ', '.join(names_to_display)

    @api.model
    def _get_options_multi_branch(self, options):
        selected_multi_branchs = [
            branch for branch in options.get('multi_branch', [])
            if not branch['id'] in ('divider', 'group') and branch['selected']
        ]
        if not selected_multi_branchs:
            # If no branch is specifically selected, we actually want to select them all.
            selected_multi_branchs = [
                branch for branch in options.get('multi_branch', []) if
                not branch['id'] in ('divider', 'group')
            ]
        return selected_multi_branchs

    @api.model
    def _get_options_multi_branch_domain(self, options):
        if not options.get('multi_branch'):
            return []

        # Make sure to return an empty array when nothing selected to handle archived journals.
        selected_branchs = self._get_options_multi_branch(options)
        return selected_branchs and [('company_branch_id', 'in', [j['id'] for j in self._get_options_multi_branch(options)])] or []


    def _get_options_domain(self, options, date_scope):
        domain = super(AccountReport, self)._get_options_domain(options, date_scope)
        domain += self._get_options_multi_branch_domain(options)
        return domain
