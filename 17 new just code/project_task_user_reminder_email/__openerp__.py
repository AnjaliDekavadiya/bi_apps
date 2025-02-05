# -*- coding:utf-8 -*-
{
    'name' : 'Project Task User Reminder Email',
    'version': '4.5',
    'price': 49.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Project',
    'summary':  """This module send auto reminder to responsible user of task if deadline = Today.""",
    'description': """
    This module allow reminder task to user in deadline.

This module send auto reminder to responsible user of task if deadline = Today. Cron job will run everyday and search for task which due today and send reminder email to employee.

Project Task Form - Configuration of Task Reminder

If set this box then only this task will be consider for reminder.

Email to User/Employee

View Now button will allow user to jump to related task directly. This email will group all tasks which are deadline today for that user and send summary table to user/employee by email.

Task reminder
task alert
task email send
send task reminder
project user reminder
project alert
project management
task deadline
deadline reminder
deadline alert
reminder by email to user
task reminder to employee
employee alert
employee reminder
task start
task end reminder
    """,
    'depends': ['project'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_user_reminder_email/975',#'https://youtu.be/4I9liL8lV3E',
    'images': ['static/description/image1.jpg'],
    'data': [
        'data/task_reminder_data.xml',
        'views/project_view.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}
