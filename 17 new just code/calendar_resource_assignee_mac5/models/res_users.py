from dateutil.parser import parse

from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    def get_assignee_resources_hook(self, result, start, end):
        self.ensure_one()
        return result

    @api.model
    def get_assignee_resources(self, domain, date_start, date_end, filters):
        if not filters:
            filters = []

        self = self.sudo()
        start = fields.Datetime.context_timestamp(self, parse(date_start).replace(tzinfo=None)).date()
        end = fields.Datetime.context_timestamp(self, parse(date_end).replace(tzinfo=None)).date()
        results = []

        # Filter users by domain / filters
        no_id = True
        user_args = []
        count = 0
        for arg in domain:
            if type(arg) == list and arg[0] == 'assignee_user_id':
                user_args += ['|', ('id', arg[1], arg[2]), ('name', arg[1], arg[2])]
                no_id = False
                count += 1
        for ufilter in filters:
            if not ufilter.get('active') and ufilter.get('value'):
                user_args += [('id', '!=', ufilter['value'])]
            elif not ufilter.get('active') and not ufilter.get('value'):
                no_id = False
        user_args = [('is_meeting_assignee', '=', True)] + ['|'] * (count-1) + user_args

        for user in self.search(user_args):
            result = {
                'id': user.id,
                'title': user.display_name,
                'sequence': user.meeting_assignee_sequence,
            }
            user.get_assignee_resources_hook(result, start, end)
            results.append(result)

        if no_id:
            results.append({
                'id': False,
                'title': 'Unassigned',
                'sequence': 0,
            })
        return results
