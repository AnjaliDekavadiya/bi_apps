import re
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, modules, _


class KsMailActivity(models.Model):
    _inherit = 'mail.message'

    ks_user_id = fields.Many2one("res.users", default=lambda self: self.env.user.id)
    ks_office_task_id = fields.Char(default=False)
    ks_is_completed_task = fields.Boolean(default=False)
    ks_summary = fields.Char(default=False)
    # ks_note = fields.Html('Note')
    # ks_date_deadline = fields.Date('Due Date', index=True, required=False, default=False)


class KsActivity(models.Model):
    _inherit = 'mail.activity'

    date_deadline = fields.Date('Due Date', index=True, required=False, default=False)
    state = fields.Selection(selection_add=[('unplanned', 'Unplanned')])
    summary = fields.Char('Summary', translate=True)
    ks_user_id = fields.Many2one("res.users", default=lambda self: self.env.user.id)
    ks_is_recurrent = fields.Boolean(default=False)
    ks_is_exported = fields.Boolean(default=False)
    ks_office_task_id = fields.Char(default="")
    ks_office_created_date = fields.Char('Office Created Date', required=False)
    ks_attachment_ids = fields.Many2many('ir.attachment', 'ks_mail_activity_ir_attachment', string='Attachments')

    # @api.multi
    def copy(self):
        self.ks_office_task_id = ""
        return super(KsActivity, self).copy()

    def _action_done(self, feedback=False, attachment_ids=None):
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []
        for activity in self:
            # extract value to generate next activities
            if activity.chaining_type == 'trigger':
                Activity = self.env['mail.activity'].with_context(
                    activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
                vals = Activity.default_get(Activity.fields_get())

                vals.update({
                    'previous_activity_type_id': activity.activity_type_id.id,
                    'res_id': activity.res_id,
                    'res_model': activity.res_model,
                    'res_model_id': self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity = Activity.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_source(
                'mail.message_activity_done',
                render_values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                # subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_activities'),
                subtype_xmlid='mail.mt_activities',
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )
            messages |= record.message_ids[0]

            # Code modified to keep track of completed tasks
            messages.write({
                'ks_office_task_id': activity.ks_office_task_id,
                'ks_summary': activity.summary,
                'ks_is_completed_task': True,
                'ks_user_id': activity.ks_user_id.id
            })

        next_activities = self.env['mail.activity'].create(next_activities_values)
        # will unlink activity, dont access `self` after that
        # sync_deleted is for office365 syncing
        self.unlink(sync_deleted=False)

        return messages, next_activities

    # @api.multi
    def unlink(self, sync_deleted=True):
        for rec in self:
            if rec.activity_type_id.id == 4 and self.env.user.ks_sync_deleted_task and sync_deleted:
                self.env['ks.deleted'].create({
                    'name': rec.summary,
                    'ks_odoo_id': rec.id,
                    'ks_office_id': rec.ks_office_task_id,
                    'ks_module': 'task',
                    'ks_user_id': rec.env.user.id,
                })
        return super(KsActivity, self).unlink()

    @api.depends('date_deadline')
    def _compute_state(self):
        for record in self.filtered(lambda activity: activity.date_deadline):
            tz = record.user_id.sudo().tz
            date_deadline = record.date_deadline
            record.state = self._compute_state_from_date(date_deadline, tz)

        for record in self.filtered(lambda activity: not activity.date_deadline):
            if not record.date_deadline:
                record.state = 'unplanned'


class MyAttachment(models.Model):
    _inherit = 'ir.attachment'
    ks_office_task_attachment_id = fields.Char(default="")

class ksIrModel(models.Model):
    _inherit = 'ir.model'

    def getting_user_name(self):
        return [(record.id, record.display_name) for record in self]



class Tasks(models.Model):
    _inherit = "res.users"

    ks_task_import = fields.Boolean("Import Tasks", default=True, readonly=True)
    ks_task_export = fields.Boolean("Export Tasks", default=True, readonly=True)

    ks_task_sync_using_subject = fields.Boolean(string='Subject', default=True, readonly=True)
    ks_task_sync_using_create_date = fields.Boolean(string='Create Date', default=True, readonly=True)
    ks_task_sync_days_before = fields.Integer(string="Sync Mails from last (in days)", default=1,
                                              help="This will allow you to sync only those tasks/events that are "
                                                   "created or updated in the given days. Here 0 days means Today.")
    ks_task_sync_using_days = fields.Boolean(default=True)
    # ks_task_sync_repeated = fields.Boolean(default=False)
    # ks_repeat_occurrence = fields.Char("Occurrences (1-10)", default=5,
    #                                    help="Number of Occurrences of repeating tasks.")
    ks_task_filter_domain = fields.Char("Task Filter Domain",
                                        help="This filter domain is only applicable while syncing "
                                             "from Odoo to office 365.")
    ks_sync_deleted_task = fields.Boolean("Sync deleted tasks", default=True)
    ks_is_manager_tasks = fields.Boolean("Is Manager", compute="_ks_is_manager_tasks", default=False)

    def _ks_is_manager_tasks(self):
        for rec in self:
            if self.env.user.has_group("ks_office365_base.office_manager_group_id"):
                rec.ks_is_manager_tasks = True
            else:
                rec.ks_is_manager_tasks = False

    # User Activity count Override
    @api.model
    def systray_get_activities(self):
        # res = super(Tasks, self).systray_get_activities()
        query = """SELECT m.id, count(*), act.res_model as model,
                            CASE
                                WHEN %(today)s::date - act.date_deadline::date = 0 Then 'today'
                                WHEN %(today)s::date - act.date_deadline::date > 0 Then 'overdue'
                                WHEN %(today)s::date - act.date_deadline::date < 0 Then 'planned'
                            END AS states
                        FROM mail_activity AS act
                        JOIN ir_model AS m ON act.res_model_id = m.id
                        WHERE user_id = %(user_id)s
                        GROUP BY m.id, states, act.res_model;
                        """
        self.env.cr.execute(query, {
            'today': fields.Date.context_today(self),
            'user_id': self.env.uid,
        })
        activity_data = self.env.cr.dictfetchall()
        model_ids = [a['id'] for a in activity_data]
        model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(model_ids).getting_user_name()}

        user_activities = {}
        for activity in activity_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'id': activity['id'],
                    'name': model_names[activity['id']],
                    'model': activity['model'],
                    'type': 'activity',
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0, 'today_count': 0, 'overdue_count': 0, 'planned_count': 0,
                }
                # res.insert(0, user_activities)
            if activity['states']:
                user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
            if activity['states'] in ('today', 'overdue'):
                user_activities[activity['model']]['total_count'] += activity['count']


        return list(user_activities.values())
        # return res

    def ks_get_tasks(self):
        try:
            if self.ks_task_sync_using_days:
                _days = str(self.ks_task_sync_days_before)
                if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
                    return self.ks_show_error_message(_("Days can only be in numbers less then 999 and greater "
                                                        "than or equal to 0."))
            # if self.ks_task_sync_repeated and not 1 <= int(self.ks_repeat_occurrence) <= 10:
            #     return self.ks_show_error_message(_("Number of occurrence must lie between 0 and 11."))
            res = self.ks_import_tasks()
            return res
        except Exception as ex:
            if type(ex) is requests.exceptions.ConnectionError:
                ex = "Internet Connection Failed"
            ks_current_job = self.env["ks.office.job"].sudo().search([('ks_records', '>=', 0),
                                                               ('ks_status', '=', 'in_process'),
                                                               ('ks_job', '=', 'task_import'),
                                                               ('create_uid', '=', self.env.user.id)])
            if ks_current_job:
                ks_current_job.write({'ks_status': 'error', 'ks_error_text': ex})
                self.env.cr.commit()
            self.ks_create_log("task", "Error", "", 0, datetime.today(), "office_to_odoo", False, "failed",
                               str(ex) +
                               "\nCheck Jobs to know how many records have been processed.")
            return self.ks_has_sync_error()

    def ks_office_task_folders(self, ks_head, ks_current_job):
        ks_office_task_folders = dict()
        ks_task_folders = json.loads(requests.get("https://graph.microsoft.com/beta/me/outlook/taskFolders",
                                                  headers=ks_head).text)

        if 'error' in ks_task_folders:
            if ks_task_folders["error"]['code'] == 'InvalidAuthenticationToken':
                self.refresh_token()
                ks_head['Authorization'] = self.ks_auth_token
                ks_task_folders = json.loads(requests.get("https://graph.microsoft.com/beta/me/outlook/taskFolders",
                                                          headers=ks_head).text)
                if 'error' in ks_task_folders:
                    self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(),
                                       "office_to_odoo",
                                       "authentication", "failed", ks_task_folders["error"]['code'])
                    ks_current_job.write({'ks_status': 'completed'})
                    return self.ks_show_error_message(
                        _("Some error occurred! \nPlease check logs for more information."))
            else:
                self.ks_create_log("task", "Authentication", "", 0, datetime.today(), "office_to_odoo",
                                   "authentication", "failed", ks_task_folders["error"]['code'])
                ks_current_job.write({'ks_status': 'completed'})
                return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for more "
                                                    "information."))

        for folder in ks_task_folders['value']:
            ks_office_task_folders.update({
                folder['name']: folder['id'],
                folder['id']: folder['name'],
            })

        return ks_office_task_folders

    def ks_import_tasks(self):
        ks_current_job = self.sudo().ks_is_job_completed("task_import", "task")
        if not ks_current_job:
            return self.ks_show_error_message(_('Process Is Already Running.'))
        else:
            ks_current_job.write({'ks_status': 'in_process', 'ks_error_text': False})

        ks_sync_task_from_date = str(datetime.min.replace(year=1900)).replace(' ', 'T') + ".0000000"
        if self.ks_task_sync_using_days:
            ks_days = self.ks_task_sync_days_before
            ks_sync_task_from_date = datetime.today() + relativedelta(days=-ks_days)

        ks_task_imported = ks_current_job.ks_records
        ks_auth_token = self.env["res.users"].search([("id", "=", self.id)]).ks_auth_token
        if not ks_auth_token:
            self.ks_create_log("task", "", "", 0, datetime.today(), "office_to_odoo", "authentication", "failed",
                               "Generate Authentication Token")
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_show_error_message('Generate Authentication Token!')

        ks_head = {
            "Authorization": ks_auth_token,
            "Host": "graph.microsoft.com"
        }
        # Only tasks in the default folder is being synced because assigned user data is not available
        ks_office_task_folders = self.ks_office_task_folders(ks_head, ks_current_job)

        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks?$top=1000000&$skip=" + \
                          str(ks_task_imported) + "&$filter=lastModifiedDateTime ge " + \
                          str(ks_sync_task_from_date).replace(' ', 'T') + "Z"

        ks_response = requests.get(ks_api_endpoint, headers=ks_head)
        ks_office_tasks = json.loads(ks_response.text)['value']

        # For finding the duplicates
        ks_all_response = requests.get("https://graph.microsoft.com/beta/me/outlook/taskFolders/" +
                                       ks_office_task_folders['Tasks'] + "/tasks?$top=1000000", headers=ks_head)
        ks_all_office_tasks = json.loads(ks_all_response.text)['value']

        ks_syncing_field = list()
        if self.ks_task_sync_using_subject:
            ks_syncing_field.append("subject")
        if self.ks_task_sync_using_create_date:
            ks_syncing_field.append("create_date")

        # Finding duplicates
        ks_office_duplicate_subject = set()
        ks_office_duplicate_subject_create = set()
        ks_office_duplicate_create = set()

        if 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
            # Finding duplicates in office 365
            _subject = list()
            for ks_task in ks_all_office_tasks:
                if _subject.count(ks_task['subject']) == 1:
                    if ks_task['recurrence']:
                        continue
                    self.ks_create_log("task", ks_task['subject'], ks_task['id'], 0,
                                       datetime.today(), "office_to_odoo", "update", "failed",
                                       "Multiple task with the same subject \'" + ks_task['subject'] +
                                       "\' exists in in Office 365.\nNote: This task is being synced with respect to "
                                       "subject.")
                    ks_office_duplicate_subject.add(ks_task['subject'])
                _subject.append(ks_task['subject'])

        elif 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
            # Finding duplicates in office
            _subject_create_date = list()
            for ks_task in ks_all_office_tasks:
                _create = ks_task['createdDateTime'].split('T')[0]
                if _subject_create_date.count((ks_task['subject'], _create)) == 1:
                    if ks_task['recurrence']:
                        continue
                    self.ks_create_log("task", ks_task['subject'], ks_task['id'], 0, datetime.today(),
                                       "office_to_odoo", "update", "failed",
                                       "Multiple task with the same subject \'" + ks_task['subject'] +
                                       "\' and create date \'" + _create +
                                       "\' exists in in Office 365.\nNote: This task is being synced with respect to "
                                       "subject and create date.")
                    ks_office_duplicate_subject_create.add((ks_task['subject'], _create))
                _subject_create_date.append((ks_task['subject'], _create))

        ks_sync_error = False
        for task in ks_office_tasks:
            """ Deleted Lists' tasks are comming in response """
            if task['parentFolderId'] not in ks_office_task_folders:
                continue

            """ Syncing deleted tasks in odoo """
            if self.ks_sync_deleted_task:
                is_deleted = self.ks_sync_task_deleted_in_odoo(ks_head, task)
                if is_deleted:
                    continue

            """ Not syncing tasks having folder other than Tasks as
            we cannot identify if it is assigned to someone else """
            _folder_name = ks_office_task_folders[task['parentFolderId']]
            _assigned_to = task['assignedTo'] or "None"
            if _folder_name != "Tasks":
                message = "\'%s\' can\'t be created! \nReason: It resides in List \'%s\' and assigned to \'%s\', But " \
                          "currently we can't identify if its assigned to someone" % \
                          (task['subject'], _folder_name, _assigned_to)
                self.ks_create_log("task", task['subject'], task['id'], 0, datetime.today(), "office_to_odoo",
                                   "create", "failed", message)
                continue

            ks_task_imported += 1
            ks_task_id = task['id']
            ks_subject = task['subject']
            ks_attachments = task['hasAttachments']
            vals = {
                "summary": task['subject'],
                "ks_office_task_id": ks_task_id,
                "ks_user_id": self.id,
                "date_deadline": self.ks_get_due_date(task['dueDateTime']),
                "ks_is_recurrent": True if task['recurrence'] else False,
                "activity_type_id": 4,
                "user_id": self.id,
                "res_id": self.partner_id.id,
                "res_model_id": self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id,
                "previous_activity_type_id": False,
                "chaining_type": False,
                "activity_category": 'default',
                "recommended_activity_type_id": False,
                "note": '<p>' + task['body']['content'] + '</p>'
            }

            # Recurrent task completed in outlook, need to query again
            _mail_activities = self.env.cr.execute("select id,ks_office_task_id,summary,create_date::DATE from "
                                                   "mail_activity where ks_user_id = %s" % self.id)
            odoo_mail_activities = self._cr.dictfetchall()

            ks_existing_tasks_id = [task['ks_office_task_id'] for task in odoo_mail_activities]
            ks_completed_task_ids = self.env['mail.message'].search([('ks_is_completed_task', '=', True),
                                                                     ('ks_user_id', '=', self.id)]) \
                .mapped('ks_office_task_id')

            if ks_task_id in ks_existing_tasks_id:
                if 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
                    if task['subject'] in ks_office_duplicate_subject:
                        continue

                elif 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
                    _create = task['createdDateTime'].split('T')[0]
                    if (task['subject'], _create) in ks_office_duplicate_subject_create:
                        continue

                ks_task = self.env['mail.activity'].search([('ks_office_task_id', '=', task['id'])], limit=1)
                _error = self.ks_update_odoo_task(ks_current_job, vals, ks_task, task, ks_task_imported,
                                                  task['hasAttachments'], ks_head)
                if _error:
                    ks_sync_error = True

            elif ks_task_id in ks_completed_task_ids:
                if task["status"] == "notStarted":
                    tasks = self.env['mail.message'].search([('ks_office_task_id', '=', ks_task_id)])
                    for t in tasks:
                        t.unlink()
                    _error = self.ks_create_odoo_task(vals, task['status'], task['hasAttachments'], ks_head, task)
                    ks_current_job.write({'ks_records': ks_task_imported})
                    if _error:
                        ks_sync_error = True
                else:
                    self.ks_create_log("task", task['subject'], task['id'], 0, datetime.today(),
                                       "office_to_odoo", "update", "success",
                                       _("Completed task can't be modified"))

            elif 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
                if task['subject'] in ks_office_duplicate_subject:
                    continue

                _task = self.env.cr.execute("select * from mail_activity where summary = %(summary)s and "
                                            "ks_user_id = %(uid)s", {'summary': task['subject'], 'uid': self.id})
                ks_task = self._cr.dictfetchall()
                if not ks_task:
                    _error = self.ks_create_odoo_task(vals, task['status'], task['hasAttachments'], ks_head, task)
                    ks_current_job.write({'ks_records': ks_task_imported})
                    if _error:
                        ks_sync_error = True

                elif len(ks_task) > 1:
                    self.ks_create_log("task", ks_task.display_name, ks_task_id, ks_task.id,
                                       datetime.today(), "office_to_odoo", "update", "failed",
                                       "Multiple tasks with same Subject \'" + ks_subject + "\' exists in Odoo.")
                    ks_sync_error = True
                else:
                    ks_task = self.env['mail.activity'].search([('id', '=', ks_task[0]['id'])])
                    _error = self.ks_update_odoo_task(ks_current_job, vals, ks_task, task, ks_task_imported,
                                                      task['hasAttachments'], ks_head)
                    if _error:
                        ks_sync_error = True

                    self.ks_create_log("task", ks_task.display_name, ks_task.ks_office_task_id, ks_task.id,
                                       datetime.today(), "office_to_odoo", "update", "success",
                                       "Record updated!")

            elif 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
                _create = task['createdDateTime'].split('T')[0]
                if (task['subject'], _create) in ks_office_duplicate_subject_create:
                    continue

                # x={"en_US": task['subject']}
                # _task = self.env.cr.execute("select * from mail_activity where summary = '%s' and "
                #                             "create_date = '%s'"%(x,_create))
                                            # {'summary': task['subject'], 'create_date': _create})
                ks_task = self.env['mail.activity'].sudo().search([('summary','=',task['subject']), ('create_date','=',_create)])
                # ks_task = self._cr.dictfetchall()
                if not ks_task:
                    _error = self.ks_create_odoo_task(vals, task['status'], ks_attachments, ks_head, task)
                    ks_current_job.write({'ks_records': ks_task_imported})
                    if _error:
                        ks_sync_error = True
                elif len(ks_task) > 1:
                    self.ks_create_log("task", ks_task.display_name, ks_task_id, ks_task.id, datetime.today(),
                                       "office_to_odoo", "update", "failed",
                                       "Multiple task with same subject \'" +
                                       ks_subject + "\' and create date \'" + _create +
                                       "\' exists in Odoo. \nNote: This Task is being synced with respect to subject "
                                       "and created date.")
                    ks_sync_error = True
                else:
                    ks_task = self.env['mail.activity'].search([('id', '=', ks_task[0]['id'])])
                    _error = self.ks_update_odoo_task(ks_current_job, vals, ks_task, task, ks_task_imported,
                                                      task['hasAttachments'], ks_head)
                    if _error:
                        ks_sync_error = True

        if not ks_sync_error:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_no_sync_error()
        else:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_has_sync_error()

    def ks_sync_task_deleted_in_odoo(self, header, task):
        ks_del_event = self.env['ks.deleted'].search([('ks_office_id', '=', task['id']), ('ks_module', '=', 'task'),
                                                      ('ks_user_id', '=', self.id)])
        if ks_del_event:
            url = "https://graph.microsoft.com/beta/me/outlook/tasks/%s" % task['id']
            response = requests.delete(url, headers=header)
            if response.status_code == 204:
                self.ks_create_log("task", task['subject'], task['id'], 0, datetime.today(),
                                   "office_to_odoo", "delete", "success",
                                   _("Task deleted from outlook Tasks"))
                return True
            else:
                self.ks_create_log("calendar", task['subject'], task['id'], 0, datetime.today(),
                                   "office_to_odoo", "delete", "failed",
                                   _("Task not deleted from outlook Tasks \nReason: %s") %
                                   response['error']['message'])
        return False

    def ks_get_due_date(self, due_datetime):
        if due_datetime:
            _due_date = due_datetime['dateTime'].split('T')[0]
            _due_date = datetime.strptime(_due_date, '%Y-%m-%d') + relativedelta(days=1)
            return str(_due_date)
        return False

    def ks_create_odoo_task(self, vals, _task, ks_attachments, ks_head, task):
        ks_some_error = False
        ks_task = self.env['mail.activity'].search([('ks_office_task_id', '=', vals['ks_office_task_id']), ('ks_user_id', '=', vals['ks_user_id'])], limit=1)
        # ks_current_job = self.sudo().ks_is_job_completed("task_import", "task")
        try:
            if ks_task:
                if ks_task.ks_is_exported:
                    if task['dueDateTime']:
                        vals["date_deadline"] = task['dueDateTime']['dateTime'].split('T')[0]
                    else:
                        vals["date_deadline"] = False
                ks_task.write(vals)
                # ks_current_job.write({'ks_records': ks_task_imported})
                self.ks_create_log("task", ks_task.display_name, ks_task.ks_office_task_id, ks_task.id,
                                   datetime.today(), "office_to_odoo", "update", "success", "Record updated!")
                # if ks_attachments:
                self.ks_get_attachment(task, ks_head, ks_task, update_attachment=True)
            else:
                ks_task = self.env['mail.activity'].create(vals)
                self.ks_create_log("task", ks_task.display_name, ks_task.ks_office_task_id, ks_task.id,
                                   datetime.today(), "office_to_odoo", "create", "success", "Record created!")
                if ks_attachments:
                    self.ks_get_attachment(task, ks_head, ks_task, update_attachment=False)
                if _task == 'completed':
                    ks_task.action_done()
        except Exception as ex:
            self.ks_create_log("task", vals['summary'], vals['ks_office_task_id'], "0", datetime.today(),
                               "office_to_odoo", "create", "failed",
                               "Record not created! \nReason: " + str(ex))
            ks_some_error = True
        return ks_some_error

    def ks_update_odoo_task(self, ks_current_job, vals, ks_task, task, ks_task_imported, ks_attachments, ks_head):
        ks_some_error = False
        ks_task = ks_task.search([('ks_office_task_id', '=', ks_task.ks_office_task_id), ('ks_user_id', '=', vals['ks_user_id'])], limit=1)
        try:
            if ks_task:
                if ks_task.ks_is_exported:
                    if task['dueDateTime']:
                        vals["date_deadline"] = task['dueDateTime']['dateTime'].split('T')[0]
                    else:
                        vals["date_deadline"] = False
                ks_task.write(vals)
                ks_current_job.write({'ks_records': ks_task_imported})
                self.ks_create_log("task", ks_task.display_name, ks_task.ks_office_task_id, ks_task.id,
                                   datetime.today(), "office_to_odoo", "update", "success", "Record updated!")
                # if ks_attachments:
                self.ks_get_attachment(task, ks_head, ks_task, update_attachment=True)
            else:
                ks_task = self.env['mail.activity'].create(vals)
                self.ks_create_log("task", ks_task.display_name, ks_task.ks_office_task_id, ks_task.id,
                                   datetime.today(), "office_to_odoo", "create", "success", "Record created!")
                if ks_attachments:
                    self.ks_get_attachment(task, ks_head, ks_task, update_attachment=False)
            if task['status'] == "completed":
                _task = self.env['mail.activity'].search([('ks_office_task_id', '=', task['id'])])
                _task.action_done()
        except Exception as ex:
            self.ks_create_log("task", vals['summary'], vals['ks_office_task_id'], "0", datetime.today(),
                               "office_to_odoo", "update", "failed",
                               "Record not updated! \nReason: " + str(ex))
            ks_some_error = True
        return ks_some_error

    # Getting Attachment
    def ks_get_attachment(self, ks_office_task, ks_head, ks_task, update_attachment):
        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks/" + str(ks_office_task['id']) + \
                          "/attachments/"
        attachment_data = json.loads(requests.get(ks_api_endpoint, headers=ks_head).text)
        ks_office_attachments_list = list()
        for attachment in attachment_data['value']:
            office_attachment_id = attachment.get('id')
            data = {
                'ks_office_task_attachment_id': office_attachment_id,
                'name': attachment.get('name'),
                'datas': attachment.get('contentBytes').encode('utf-8'),
                'type': 'binary',
                # 'datas_fname': attachment.get('name'),
                'description': attachment.get('name'),
                'res_model': 'mail.activity',
                'mimetype': attachment.get('contentType'),
            }
            if update_attachment:
                ks_office_attachments_list.append(office_attachment_id)
                ks_odoo_attachments = self.env['ir.attachment'].sudo().search(
                    [('ks_office_task_attachment_id', '=', office_attachment_id)])
                if not ks_odoo_attachments:
                    ks_attach_id = self.env['ir.attachment'].create(data)
                    ks_task.update({'ks_attachment_ids': [(4, ks_attach_id.id)]})
                    ks_office_attachments_list.append(ks_attach_id.id)
            else:
                ks_attach = self.env['ir.attachment'].create(data)
                ks_task.update({'ks_attachment_ids': [(4, ks_attach.id)]})
        if update_attachment:
            self._cr.execute("select ks_office_task_attachment_id from ir_attachment where id in "
                             "(select ir_attachment_id from ks_mail_activity_ir_attachment where mail_activity_id = %s)"
                             % ks_task.id)
            ks_odoo_ids = self._cr.dictfetchall()
            self.ks_unlink_attachment(ks_odoo_ids, ks_office_attachments_list)

    def ks_unlink_attachment(self, ks_odoo_ids, ks_office_attachments_list):
        for ks_odoo_attach in ks_odoo_ids:
            if ks_odoo_attach['ks_office_task_attachment_id'] not in ks_office_attachments_list:
                ks_odoo_attachments = self.env['ir.attachment'].sudo().search(
                    [('ks_office_task_attachment_id', '=', ks_odoo_attach['ks_office_task_attachment_id'])])
                res = ks_odoo_attachments.unlink()

    def ks_post_tasks(self):
        try:
            if self.ks_task_sync_using_days:
                _days = str(self.ks_task_sync_days_before)
                if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
                    return self.ks_show_error_message(
                        _("Days can only be in numbers less then 999 and greater than or equal to 0."))
            res = self.ks_export_tasks()
            return res
        except Exception as ex:
            if type(ex) is requests.exceptions.ConnectionError:
                ex = "Internet Connection Failed"
            ks_current_job = self.env["ks.office.job"].search([('ks_records', '>=', 0),
                                                               ('ks_status', '=', 'in_process'),
                                                               ('ks_job', '=', 'task_export'),
                                                               ('create_uid', '=', self.env.user.id)])
            if ks_current_job:
                ks_current_job.write({'ks_status': 'error', 'ks_error_text': ex})
                self.env.cr.commit()

            self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(), "odoo_to_office",
                               "authentication", "failed", str(ex) +
                               "\nCheck Jobs to know how many records have been processed.")
            return self.ks_has_sync_error()

    def ks_export_tasks(self):
        ks_current_job = self.sudo().ks_is_job_completed("task_export", "task")
        if not ks_current_job:
            return self.ks_show_error_message(_('Process Is Already Running.'))
        else:
            ks_current_job.write({'ks_status': 'in_process'})
        ks_sync_task_from_date = datetime.min.date().replace(year=1900)
        if self.ks_task_sync_using_days:
            ks_days = self.ks_task_sync_days_before
            ks_sync_task_from_date = datetime.today().date() + relativedelta(days=-ks_days)
        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks?$top=1000000"
        ks_auth_token = self.ks_auth_token

        if not ks_auth_token:
            self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(), "odoo_to_office",
                               "authentication", "failed", "Generate Authentication Token")
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_show_error_message(_("Generate Authentication Token"))

        head = {
            "Authorization": ks_auth_token,
            "Content-Type": "application/json"
        }
        ks_search_domain = self.ks_get_task_search_domain(self.ks_task_filter_domain, ks_sync_task_from_date)

        # tasks to be synced
        ks_odoo_tasks = self.env['mail.activity'].sudo().search(ks_search_domain)

        # tasks to verify duplicates
        ks_odoo_all_tasks = self.env['mail.activity'].sudo().search(ks_search_domain[0:-1])

        ks_office_tasks = json.loads(requests.get(ks_api_endpoint, headers=head).text)

        if 'error' in ks_office_tasks:
            if ks_office_tasks["error"]['code'] == 'InvalidAuthenticationToken':
                self.refresh_token()
                head['Authorization'] = self.ks_auth_token
                ks_office_tasks = json.loads(requests.get(ks_api_endpoint, headers=head).text)
                if 'error' in ks_office_tasks:
                    self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(),
                                       "office_to_odoo",
                                       "authentication", "failed", ks_office_tasks["error"]['code'])
                    ks_current_job.write({'ks_status': 'completed'})
                    return self.ks_show_error_message(
                        _("Some error occurred! \nPlease check logs for more information."))
            else:
                self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(), "odoo_to_office",
                                   "authentication", "failed", ks_office_tasks["error"]['code'])
                ks_current_job.write({'ks_status': 'completed'})
                return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for more information."))

        ks_all_office_tasks = ks_office_tasks['value']

        ks_syncing_field = list()
        if self.ks_task_sync_using_subject:
            ks_syncing_field.append("subject")
        if self.ks_task_sync_using_create_date:
            ks_syncing_field.append("create_date")

        ks_odoo_duplicate_subject = set()
        ks_office_task_subjects = list()
        if 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
            # Finding duplicate tasks in odoo schedule activities
            _subjects = list()
            for task in ks_odoo_all_tasks:
                if not task.summary:
                    self.ks_create_log("task", (task.summary or ''), "", task.id, datetime.today(), "office_to_odoo",
                                       "update", "failed", "Multiple task with the same subject \'" +
                                       (task.summary or '') + "\' exists in in Office 365.\nNote: This task is being "
                                                      "synced with respect to subject.")
                elif _subjects.count(task.summary) == 1:
                    ks_odoo_duplicate_subject.add(task.summary)
                    self.ks_create_log("task", (task.summary or ''), "", task.id, datetime.today(), "office_to_odoo",
                                       "update", "failed", "Multiple task with the same subject \'" +
                                       (task.summary or '') + "\' exists in in Office 365.\nNote: This task is being "
                                                      "synced with respect to subject.")
                _subjects.append(task.summary)

            # storing task data for finding if any task is already available in office
            for task in ks_all_office_tasks:
                ks_office_task_subjects.append(task['subject'])

        ks_odoo_duplicate_subject_create = set()
        ks_office_task_subject_create = list()
        if 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
            # Finding duplicate tasks in odoo schedule activities
            _subject_create_date = list()
            for task in ks_odoo_all_tasks:
                _create = str(task.create_date.date())
                if _subject_create_date.count((task.summary, _create)):
                    ks_odoo_duplicate_subject_create.add((task.summary, _create))
                    self.ks_create_log("task", (task.summary or ''), "", task.id, datetime.today(), "office_to_odoo",
                                       "update",
                                       "failed", "Multiple task with the same subject \'" + (task.summary or '') +
                                       "\' and create date \'" + _create +
                                       "\' exists in in Office 365.\nNote: This task is being synced with respect to "
                                       "subject.")
                _subject_create_date.append((task.summary, _create))

            # storing task data for finding if any task is already available in office
            for task in ks_all_office_tasks:
                ks_office_task_subject_create.append((task['subject'], self.ks_get_due_date(task['dueDateTime'])))

        ks_sync_error = False
        ks_task_exported = ks_current_job.ks_records
        for task in ks_odoo_tasks[ks_task_exported:]:
            ks_task_exported += 1

            ks_date_due = None
            if task.date_deadline:
                ks_date_due = {
                    'dateTime': str(task.date_deadline) + "T18:30:00.0000000",
                    'timeZone': 'UTC'
                }

            self.env.cr.execute("select * from ir_attachment where id in (select ir_attachment_id from "
                                "ks_mail_activity_ir_attachment where mail_activity_id = %(act_id)s);",
                                {'act_id': task.id})
            ks_attachment = self._cr.dictfetchall()

            ks_note = str()
            for text in re.findall(r'>([^<>]*)<', str(task.note)):
                if len(text) and not text.isspace() and not text.startswith('\n') and not text.startswith('\r') and text != '\n' and text != '\r':
                    if text[0].isspace():
                        text = text[1:]
                    if text[len(text)-1].isspace():
                        text = text[:len(text)-1]
                    ks_note += text + "\n"
            # ks_note = str(task.note).split('<div>')[1].split("</div>")[0]

            ks_data = {
                "subject": task.summary,
                "dueDateTime": ks_date_due,
                "status": 'notStarted',  # Only syncing planned non-completed tasks
                "body": {
                    "contentType": "text",
                    "content": ks_note
                },
                "hasAttachments": True if ks_attachment else False,
            }

            if task.ks_office_task_id != '':
                if 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
                    if task.summary in ks_odoo_duplicate_subject:
                        continue
                elif 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
                    if task.ks_office_created_date in ks_odoo_duplicate_subject_create:
                        continue

                ks_some_error = self.ks_update_office_task(task.ks_office_task_id, task, ks_data, head,
                                                           ks_current_job)
                ks_current_job.write({'ks_records': ks_task_exported})
                if ks_some_error:
                    ks_sync_error = True

            elif 'subject' in ks_syncing_field and 'create_date' not in ks_syncing_field:
                # if not task.summary or task.summary in ks_odoo_duplicate_subject:
                if task.summary in ks_odoo_duplicate_subject:
                    continue

                elif task.summary in ks_office_task_subjects:
                    ks_office_task_id = list()
                    for _task in ks_all_office_tasks:
                        if task.summary == _task['subject']:
                            ks_office_task_id.append(_task['id'])

                    if len(ks_office_task_id) > 1:
                        self.ks_create_log("task", (task.summary or ''), '', task.id, datetime.today(), "odoo_to_office",
                                           "update", "failed",
                                           "Multiple task with the same subject \'" + (task.summary or '') +
                                           "\' exists in in Office 365.\nNote: This task is being synced with respect "
                                           "to subject.")
                        continue

                    else:
                        ks_some_error = self.ks_update_office_task(ks_office_task_id[0], task, ks_data, head,
                                                                   ks_current_job)
                        ks_current_job.write({'ks_records': ks_task_exported})
                        if ks_some_error:
                            ks_sync_error = True

                else:
                    ks_some_error = self.ks_create_office_task(head, ks_data, task, ks_current_job)
                    ks_current_job.write({'ks_records': ks_task_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif 'subject' in ks_syncing_field and 'create_date' in ks_syncing_field:
                if (task.summary, str(task.create_date.date())) in ks_odoo_duplicate_subject_create:
                    continue

                elif (task.summary, str(task.create_date.date())) in ks_office_task_subject_create:
                    ks_office_task_id = list()
                    for _task in ks_all_office_tasks:
                        if self.ks_get_due_date(_task['dueDateTime']) == str(task.create_date.date()) \
                                and task.summary == _task['subject']:
                            ks_office_task_id.append(_task['id'])

                    if len(ks_office_task_id) > 1:
                        self.ks_create_log("task", (task.summary or ''), '', task.id, datetime.today(), "odoo_to_office",
                                           "update", "failed",
                                           "Multiple task with the same subject \'" + (task.summary or '') +
                                           "\' and create date \'" + str(task.create_date.date()) +
                                           "\' exists in in Office 365.\nNote: This task is being synced with respect "
                                           "to subject and create date.")
                        continue

                    else:
                        ks_some_error = self.ks_update_office_task(ks_office_task_id[0], task, ks_data, head,
                                                                   ks_current_job)
                        ks_current_job.write({'ks_records': ks_task_exported})
                        if ks_some_error:
                            ks_sync_error = True

                else:
                    ks_some_error = self.ks_create_office_task(head, ks_data, task, ks_current_job)
                    ks_current_job.write({'ks_records': ks_task_exported})
                    if ks_some_error:
                        ks_sync_error = True

        _error = self.ks_mark_completed_tasks(head, ks_current_job)
        if _error:
            ks_sync_error = True

        if not ks_sync_error:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_no_sync_error()
        else:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_has_sync_error()

    def ks_mark_completed_tasks(self, head, ks_current_job):
        _error = False
        # All completed odoo tasks that are synced with outlook initially will be completed in outlook as well
        ks_completed_odoo_tasks = self.env['mail.message'].search([('ks_is_completed_task', '=', True),
                                                                   ('ks_office_task_id', '!=', False),
                                                                   ('ks_user_id', '=', self.id)])
        for marked_task in ks_completed_odoo_tasks:
            if not marked_task.ks_office_task_id:
                self.ks_create_marked_task_in_office(head, marked_task, ks_current_job)
                continue

            ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks/" + marked_task.ks_office_task_id
            res = requests.patch(ks_api_endpoint, headers=head, json={"status": "completed"})
            office_task = json.loads(res.text)
            if 'error' in office_task:
                if office_task["error"]['code'] == 'InvalidAuthenticationToken':
                    self.refresh_token()
                    head['Authorization'] = self.ks_auth_token
                    office_task = json.loads(requests.patch(ks_api_endpoint, headers=head,
                                                            json={"status": "notStarted"}).text)
                elif res.status_code == 404:
                    for task in self.env['mail.message'].search(
                            [('ks_office_task_id', '=', marked_task.ks_office_task_id)]):
                        del_task = {"summary": task.ks_summary, "ks_office_id": task.ks_office_task_id, "id": 0}
                        if self.ks_sync_deleted_task:
                            task.unlink()
                            self.ks_create_log("task", del_task["summary"], del_task["ks_office_id"],
                                               del_task["id"], datetime.today(), "odoo_to_office", "delete",
                                               "success", "Task deleted from Odoo Mail Message")
                        else:
                            self.ks_create_log("task", del_task["summary"], del_task["ks_office_id"],
                                               del_task["id"], datetime.today(), "odoo_to_office", "create",
                                               "failed", "Completed task in Odoo cannot be recreated in outlook")
                else:
                    ks_error = office_task['error']['code'] + "\n" + office_task['error'].get('message')
                    self.ks_create_log("task", "Completed Task", "", 0, datetime.today(), "odoo_to_office",
                                       "create", "failed", ks_error)
                    _error = True
            else:
                self.ks_create_log("task", office_task['subject'], office_task['id'], 0, datetime.today(),
                                   "odoo_to_office", "update", "success", "Record updated!")

        return _error

    def ks_create_office_task(self, head, ks_data, task, ks_current_job):
        _error = False
        _folders = self.ks_office_task_folders(head, ks_current_job)
        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/taskFolders/" + _folders['Tasks'] + "/tasks"
        ks_office_task = json.loads(requests.post(ks_api_endpoint, headers=head, json=ks_data).text)
        if 'error' in ks_office_task:
            if 'code' in ks_office_task['error']:
                ks_error = ks_office_task['error']['code'] + "\n" + ks_office_task['error']['message']
            else:
                ks_error = ks_office_task['error']['message']
            self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                               "odoo_to_office", "create", "failed", ks_error)
            _error = True
        else:
            try:
                task.write({"ks_office_task_id": ks_office_task['id'], "ks_is_exported": True})
                if task.ks_attachment_ids:
                    self.ks_create_office_attachment(head, ks_office_task['id'], task, create_rec=True)
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "create", "success", "Record created!")
            except Exception as ex:
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "create", "failed", str(ex))
                _error = True
        return _error

    def ks_update_office_task(self, ks_office_task_id, task, ks_data, head, ks_current_job):
        _error = False
        if task.ks_is_recurrent:
            ks_data.pop("dueDateTime")
        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks/" + ks_office_task_id
        ks_response = requests.patch(ks_api_endpoint, headers=head, json=ks_data)
        ks_office_task = json.loads(ks_response.text)
        if 'error' in ks_office_task:
            if ks_response.status_code == 404:
                if self.ks_sync_deleted_task:
                    del_task = {"summary": task.summary, "ks_office_id": ks_office_task_id, "id": task.id}
                    task.unlink()
                    self.ks_create_log("task", del_task["summary"], del_task["ks_office_id"],
                                       del_task["id"], datetime.today(), "odoo_to_office", "delete", "success",
                                       "Task deleted from Odoo TODO Activities")
                else:
                    self.ks_create_office_task(head, ks_data, task, ks_current_job)
            elif 'code' in ks_office_task['error']:
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "create", "failed", ks_office_task['error']['code'] + "\n" +
                                   ks_office_task['error']['message'])
                _error = True
            else:
                self.ks_create_log("task", task.display_name, task.ks_office_task_id, str(task.id),
                                   datetime.today(),
                                   "odoo_to_office", "create", "failed", ks_office_task['error']['message'])
                _error = True
        else:
            task.write({'ks_office_task_id': ks_office_task['id'], 'ks_is_exported': True})
            # if task.ks_attachment_ids:
            self.ks_create_office_attachment(head, ks_office_task['id'], task)
            if task.ks_is_recurrent:
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "update", "success",
                                   "Record updated but due date cannot be modified because it will create a "
                                   "duplicate in outlook.")
            else:
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "update", "success", "Record updated!")

        return _error

    def ks_create_marked_task_in_office(self, head, marked_task, ks_current_job):
        ks_date_due = None
        # if marked_task.ks_date_deadline:
        #     ks_date_due = {
        #         'dateTime': str(marked_task.ks_date_deadline) + "T18:30:00.0000000",
        #         'timeZone': 'UTC'
        #     }
        #
        # ks_note = str()
        # for text in re.findall(r'>([^<>]*)<', str(marked_task.ks_note)):
        #     if text:
        #         ks_note += text + "\n "
        # self.env.cr.execute("select * from ir_attachment where id in (select ir_attachment_id from "
        #                     "ks_mail_activity_ir_attachment where mail_activity_id = %(act_id)s);",
        #                     {'act_id': marked_task.id})
        # ks_attachment = self._cr.dictfetchall()
        ks_data = {
            "subject": marked_task.ks_summary,
            "dueDateTime": ks_date_due,
            "status": "completed",
            "body": {
                "contentType": "text",
                "content": ""
            },
            "hasAttachments": False,
        }
        _folders = self.ks_office_task_folders(head, ks_current_job)
        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/taskFolders/" + _folders['Tasks'] + "/tasks"
        ks_office_task = json.loads(requests.post(ks_api_endpoint, headers=head, json=ks_data).text)
        if 'error' in ks_office_task:
            if ks_office_task["error"]['code'] == 'InvalidAuthenticationToken':
                self.refresh_token()
                head['Authorization'] = self.ks_auth_token
                ks_office_task = json.loads(requests.post(ks_api_endpoint, headers=head, json=ks_data).text)
                marked_task.write({"ks_office_task_id": ks_office_task['id']})
            else:
                ks_error = ks_office_task['error']['code'] + "\n" + ks_office_task['error'].get('message')
                self.ks_create_log("task", "Completed Task", "", 0, datetime.today(), "odoo_to_office",
                                   "create", "failed", _(ks_error))
                _error = True
        else:
            marked_task.write({"ks_office_task_id": ks_office_task['id']})
            self.ks_create_log("task", ks_office_task['subject'], ks_office_task['id'], 0, datetime.today(),
                               "odoo_to_office", "create", "success", _("Record updated!"))

    def ks_create_office_attachment(self, ks_head, ks_office_task_id, task, create_rec=False):
        _error = False

        ks_api_endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks/%s/attachments" % ks_office_task_id

        ks_office_task_attachment_ids = list()
        office_task_attachments = json.loads(requests.get(ks_api_endpoint, headers=ks_head).text)['value']
        if office_task_attachments:
            for attach in office_task_attachments:
                ks_office_task_attachment_ids.append(attach['id'])

        for attach in task.ks_attachment_ids:
            vals = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": attach.name,
                "contentType": attach.mimetype,
                "isInline": False,
                "contentBytes": attach.datas.decode('utf-8'),
            }
            if not create_rec:
                if attach.ks_office_task_attachment_id and attach.ks_office_task_attachment_id in \
                        task.ks_attachment_ids.mapped('ks_office_task_attachment_id'):
                    if attach.ks_office_task_attachment_id in ks_office_task_attachment_ids:
                        ks_office_task_attachment_ids.remove(attach.ks_office_task_attachment_id)
                        continue

            ks_office_attachment = json.loads(requests.post(ks_api_endpoint, headers=ks_head, json=vals).text)
            if 'error' in ks_office_attachment:
                if 'code' in ks_office_attachment['error']:
                    ks_error = ks_office_attachment['error']['code'] + "\n" + ks_office_attachment['error']['message']
                else:
                    ks_error = ks_office_attachment['error']['message']
                self.ks_create_log("task", task.summary, task.ks_office_task_id, str(task.id), datetime.today(),
                                   "odoo_to_office", "create", "failed",
                                   "Attachment creation failed for id \'%s\' \nError: %s" % (
                                       attach.id, ks_error))
                _error = True
            else:
                attach.write({'ks_office_task_attachment_id': ks_office_attachment['id']})

        # deleting attachments in office that are deleted in odoo (updating)
        if len(ks_office_task_attachment_ids):
            for attach_id in ks_office_task_attachment_ids:
                requests.delete(ks_api_endpoint + "/" + attach_id, headers=ks_head)

        return _error

    def ks_get_task_search_domain(self, ks_domain, ks_sync_task_from_date):
        ks_search_domain = [('user_id', '=', self.id), ('activity_type_id', '=', 4), ]
        if ks_domain:
            for d in eval(ks_domain):
                if type(d) is list:
                    ks_search_domain.append(tuple(d))

        ks_search_domain.append(('write_date', '>=', ks_sync_task_from_date))
        return ks_search_domain
