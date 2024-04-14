# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api,fields,models

class Calendar(models.Model):
    _inherit = "calendar.event"

    presenter_id = fields.Many2one("res.partner",string="Presenter")
    facilitator_id = fields.Many2one("res.partner",string="Facilitator")
    note_taker_id = fields.Many2one("res.partner",string="Note Taker")
    time_keeper_id = fields.Many2one("res.partner",string="Time Keeper")

    agenda_items = fields.Text("Agenda Items")
    action_items = fields.Text("Action Items")
    conclusion = fields.Text("Conclusion")
    calendar_lines = fields.One2many('calendar.line', 'calendar_event_id',
                                         'Minutes Of Meeting')
    agenda_line = fields.One2many('agenda.line', 'calendar_event_id',
                                         'Minutes Of Meeting ')
    

class AgendaLine(models.Model):
    _name = "agenda.line"
    _description = "AgendaLine"
    _rec_name="name_agenda"

    description= fields.Char("Description Of Agenda")
    calendar_event_id = fields.Many2one('calendar.event', string = "Name")
    name_agenda = fields.Char(string="Name Of Agenda", required=True)


class CalendarLine(models.Model):
    _name = "calendar.line"
    _description="CalendarLine"
    _rec_name="agendas"


    descriptions= fields.Char("Description",)
    calendar_event_id= fields.Many2one('calendar.event', string="Agenda", required=True)
    agendas= fields.Many2one('agenda.line', string="Agenda ", required=True,)
    action = fields.Many2one("res.users",string="Action By", required=True)
    responsible =fields.Many2many("res.users",string="Responsible", required=True)


    @api.onchange('agendas')
    def onchange_agendas(self):
        for rec in self:
            rec.descriptions=rec.agendas.description
            return {'domain': {'agendas': [('id', 'in', rec.calendar_event_id._origin.agenda_line.ids)]}}
    
