# -*- coding: utf-8 -*-
from json import dumps, loads
from ..tools.controller_utils import *
from ..tools.date_utils import *
import pytz

from odoo import http
from odoo.http import Response, request


class BryntumGantt(http.Controller):
    task_id_template = 'project-task_%d'

    def get_tz(self):
        tz = pytz.utc
        try:
            if type(request.env.user.partner_id.tz) == str:
                tz = pytz.timezone(request.env.user.partner_id.tz) or pytz.utc
        except:
            return tz
        return tz

    @property
    def default_fields(self):
        return [
            ('name', 'name', None),
            ('planned_date_begin', 'startDate', from_gantt_date),
            ('planned_date_end', 'endDate', from_gantt_date),
            ('duration', 'duration', None),
            ('duration_unit', 'durationUnit', None),
            ('parent_id', 'parentId', to_task_id),
            ('project_id', 'project_id', to_project_id),
            ('parent_index', 'parentIndex', None),
            ('percent_done', 'percentDone', None),
            ('assigned_ids', 'assignedList', None),
            ('description', 'note', None),
            ('effort', 'effort', None),
            ('gantt_calendar_flex', 'calendar', None),
            ('date_deadline', 'date_deadline', from_gantt_date),
            ('scheduling_mode', 'schedulingMode', None),
            ('constraint_type', 'constraintType', None),
            ('constraint_date', 'constraintDate', from_gantt_date),
            ('effort_driven', 'effortDriven', None),
            ('bryntum_rollup', 'rollup', None),
            ('manually_scheduled', 'manuallyScheduled', None),
            ('stage_id', 'stageId', None),
            ('wbs_value', 'wbsValue', None)
        ]

    @http.route('/bryntum_gantt/load', type='json', auth='user', cors="*")
    def bryntum_gantt_load(self, data=None, **kw):
      #  headers = {'content-type': 'application/json'}
        data_json = loads(data)
        project_ids = data_json.get('project_ids')
        only_projects = data_json.get('only_projects')

        tz = self.get_tz()
        # user = request.env.user
        project_env = request.env['project.project']
        # task_env = request.env['project.task']
        resource_env = request.env['resource.resource']

        su = request.env['ir.config_parameter'].sudo()
        default_calendar_id = su.get_param('bryntum.default_calendar') or 'general'

        users = []
        resources = []
        assignments = []
        dependencies = []
        projects = []
        project_nodes = []
        calendar = []
        calendars = []

        use_user_ids = False

        for project_id in project_ids:

            if project_id:
                project_id = int(project_id)
            else:
                continue

            project = project_env.search([('id', '=', project_id)])
            task_objs = project.tasks

            if not project.id:
                continue

            project_id = 'project_%d' % project.id

            tasks = [
                {
                    "id": self.task_id_template % task.id,
                    "name": task.name,
                    "parentId": self.task_id_template % task.parent_id,
                    "parentIndex": task.parent_index,
                    "percentDone": task.percent_done,
                    "startDate": get_gantt_date(task.planned_date_begin, tz),
                    "endDate":  get_gantt_date(task.planned_date_end, tz),
                    "expanded": True,
                    "date_deadline": get_gantt_date(task.date_deadline, tz),
                    "project_id": project_id,
                    "note": task.description,
                    "effort": task.effort,
                    "duration": task.duration,
                    "durationUnit": task.duration_unit,
                    "calendar": task.gantt_calendar_flex,
                    "schedulingMode": task.scheduling_mode,
                    "constraintType": task.constraint_type or None,
                    "constraintDate": get_gantt_date(task.constraint_date, tz),
                    "effortDriven": task.effort_driven,
                    "rollup": task.bryntum_rollup,
                    "manuallyScheduled": task.manually_scheduled if project.bryntum_auto_scheduling else True,
                    "baselines": get_baselines(task, tz, get_gantt_date),
                    "segments": get_segments(task, tz, get_gantt_date),
                    "stageId": task.stage_id.id
                }
                for task in task_objs
            ]

            if project.bryntum_user_assignment:
               use_user_ids = True

            assignments = assignments + [
                {
                    'id': assignment.get('id'),
                    'event': self.task_id_template % assignment.get('event'),
                    'resource': assignment.get('resource'),
                    'units': assignment.get('units')
                }
                for task in task_objs
                for assignment in get_assignments(task, get_assignment) or []
            ]

            dependencies = dependencies + [
                {
                    'id': link.id,
                    'fromTask': self.task_id_template % link.from_id,
                    'toTask': self.task_id_template % link.to_id,
                    'lag': link.lag,
                    'lagUnit': link.lag_unit,
                    'active': link.dep_active,
                    'type': link.type
                }
                for task in task_objs for link in task.linked_ids
            ]

            project_nodes.append({
                                'id': project_id,
                                'startDate': get_gantt_date(project.project_start_date, tz),
                                'name': project.name,
                                'project_id': project_id,
                                'manuallyScheduled': not project.bryntum_auto_scheduling,
                                'expanded': True,
                                'children': tasks
                            })


        if not bool(only_projects):
            all_projects = project_env.search([])
            projects = [
                        {
                            'id': 'project_%d' % project.id,
                            'name': project.name,
                            'manuallyScheduled': not project.bryntum_auto_scheduling,
                            'taskTypes': [
                                    {
                                        "id": type.id,
                                        "name": type.name
                                    }
                                    for type in project.type_ids
                            ]
                        }
                        for project in all_projects
                    ]

            resource_ids = resource_env.search([])
            resources = [
                            {
                                "id": "r_" + str(resource.id),
                                "name": resource.name
                            }
                            for resource in resource_ids
                        ]

            calendar = all_projects.get_default_calendar()
            calendars = all_projects.get_calendars()

            calendar_config = su.get_param('bryntum.calendar_config')

            if isinstance(calendar_config, str):
                try:
                    calendar = loads(calendar_config)
                except:
                    calendar = calendar

            if use_user_ids:
                user_env = request.env['res.users']
                user_ids = user_env.search([])
                users = [
                    {
                        "id": "u_" + str(user.id),
                        "name": user.name,
                        "city": user.partner_id.city
                    }
                    for user in user_ids
                ]

        params = {
            "success": True,
            "project": {
                "id": "bryntum_gantt_project",
                "calendar": default_calendar_id
            },
            "projects": {
                "rows": projects
            },
            "calendars": {
                "rows": calendar,
                "toProcess": calendars
            },
            "tasks": {
                "rows": project_nodes
            },
            "dependencies": {
                "rows": dependencies,
            },
            "resources": {
                "rows": users + resources
            },
            "assignments": {
                "rows": assignments
            },
            "timeRanges": {
                "rows": []
            }
        }
        #return Response(response=dumps(params), headers=headers)
        return params


    @http.route('/bryntum_gantt/send/update', type='json', auth='user', cors="*")
    def bryntum_gantt_update(self, data=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']
        project_env = request.env['project.project']
        task_linked_env = request.env['project.task.linked']
        task_assignments_env = request.env['project.task.assignment']
        task_baselines_env = request.env['project.task.baseline']
        task_segments_env = request.env['project.task.segment']

        try:
            for el in data_json:
                gantt_model_id = el['model']['id']
                model, int_id = gantt_id(gantt_model_id)

                if not int_id:
                    continue

                new_data = el.get('newData', {})

                if model == 'project-task':
                    task = task_env.search([('id', '=', int_id)])
                    task_gantt_ids = new_data.get('taskLinks')

                    if not task_gantt_ids is None:
                        task.linked_ids.unlink()
                        for link in task_gantt_ids:
                            task_linked_env.create({
                                'from_id': to_task_id(link.get('from')),
                                'to_id': to_task_id(link.get('to')),
                                'lag': int(link.get('lag')),
                                'lag_unit': link.get('lagUnit'),
                                'dep_active': link.get('active'),
                                'type': link.get('type')
                            })

                    task_assignments = new_data.get('assignedResources')

                    if not task_assignments is None:
                        task.assigned_resources.unlink()
                        for assignment in task_assignments:
                            resource_id = get_resource_id(assignment.get('resource_id'))
                            t = task_assignments_env.create({
                                'task': to_task_id(assignment.get('task_id')),
                                'resource': resource_id[0],
                                'resource_base': resource_id[1],
                                'units': int(assignment.get('units'))
                            })
                        task.employee_ids = request.env['project.task.assignment'].search(
                                [('task', '=', task.id)]).resource_base.employee_id or False

                    baselines = new_data.get('baselines')

                    if not baselines is None:
                        task.baselines.unlink()
                        for baseline in baselines:
                            task_baselines_env.create({
                                'task': task.id,
                                'name': baseline.get('name'),
                                'planned_date_begin': from_gantt_date(baseline.get('startDate')),
                                'planned_date_end': from_gantt_date(baseline.get('endDate'))
                            })


                    segments = new_data.get('segments')

                    if not segments is None:
                        task.segments.unlink()
                        for segment in segments:
                            task_segments_env.create({
                                'task': task.id,
                                'name': segment.get('name'),
                                'planned_date_begin': from_gantt_date(segment.get('startDate')),
                                'planned_date_end': from_gantt_date(segment.get('endDate'))
                            })

                    data = field_related(new_data, self.default_fields)

                    task.write(data)
                elif model in ('project', 'project-project'):
                    project = project_env.search([('id', '=', int_id)])
                    start_date = new_data.get('startDate')
                    if project and start_date:
                        project.write({
                            'project_start_date': from_gantt_date(start_date)
                        })
                    name = new_data.get('name')
                    if project and name:
                        project.write({
                            'name': name
                        })

            return {'success': True, 'status': 'updated'}
        except Exception as e:
            return {'success': False, 'message': str(e) }

    @http.route('/bryntum_gantt/send/remove', type='json', auth='user', cors="*")
    def bryntum_gantt_remove(self, data=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']

        task_gantt_ids = [item for outer in data_json for item in outer]
        task_int_ids = [to_task_id(el) for el in task_gantt_ids]

        task = task_env.search([('id', 'in', task_int_ids)])
        task.unlink()

        return {'success': True, 'status': 'deleted'}

    @http.route('/bryntum_gantt/send/create', type='json', auth='user', cors='*')
    def bryntum_gantt_create(self, data=None, project_id=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']
        create_int_ids = []
        id_map = {}

        for rec in data_json:
            if not is_gantt_new_id(rec.get('id')):
                continue
            data = field_related(rec, self.default_fields)

            if data['parent_id'] is None:
                data['parent_id'] = id_map.get(rec.get('parentId')) or None

            task = task_env.create(data)
            generated_id = task.id
            id_map[rec.get('id')] = generated_id
            create_int_ids.append((rec.get('id'), self.task_id_template % generated_id))

        return {
            'success': True,
            'status': 'created',
            'ids': create_int_ids
        }
