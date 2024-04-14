# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

import datetime
from odoo import fields, models

class HelpdeskTeamInherit(models.Model):
    _inherit="helpdesk.ticket"

    helpdesk_stage_history_line=fields.One2many("sh.helpdesk.ticket.info",'stage_task_id',string="Stage History Line")

    def write(self, vals):
        res = super(HelpdeskTeamInherit, self).write(vals)

        if vals.get('stage_id'):
            # for update record=====================
            last_create_id=self.helpdesk_stage_history_line.ids
            if last_create_id:
                previous_id=self.env['sh.helpdesk.ticket.info'].browse(last_create_id[-1])
                sub_time = datetime.datetime.now() - previous_id.date_in

                # for days difference
                day_diff=sub_time.days

                # for hours difference
                test = str(sub_time.seconds//3600) +':'+ str(((sub_time.seconds//60)%60))
                vals = test.split(':')
                hours = divmod(float(vals[0]), 24)
                minutes = divmod(float(vals[1]), 60)
                minute = minutes[1] / 60.0
                time_to_fl =  hours[1] + minute

                # for total time count
                if day_diff>0:
                    test = str(sub_time.seconds//3600) +':'+ str(((sub_time.seconds//60)%60))
                    vals = test.split(':')
                    hours = divmod(float(vals[0]), 24)
                    minutes = divmod(float(vals[1]), 60)
                    minute = minutes[1] / 60.0
                    hours+=day_diff*24
                    total_time_to_fl =  hours + minute
                else:
                    total_time_to_fl=time_to_fl

                stage_history={
                        'date_out':  datetime.datetime.now(),
                        'date_out_by': self.env.user,
                        'day_diff':day_diff,
                        'time_diff':time_to_fl,
                        'total_time_diff':total_time_to_fl,
                    }

                self.helpdesk_stage_history_line = [(1,last_create_id[-1],stage_history)]

        #     # for new record====================
            stage_history={
                        'stage_task_id': self.id,
                        'stage_name': self.stage_id.name,
                        'date_in': datetime.datetime.now(),
                        'date_in_by': self.env.user.id,
                    }
            self.helpdesk_stage_history_line = [(0,0,stage_history)]
        return res
