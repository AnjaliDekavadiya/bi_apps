# -*- coding: utf-8 -*-
#from openerp import models, api, fields, _ odoo13
from odoo import models, api, fields, _


class HelpdeskPostQuestionWizard(models.TransientModel):
    _name = "helpdesk.post.question.wizard"
    _description = "Helepdesk Post Question"

#    @api.multi odoo13
    def action_post_question(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        question_url = "/ticket_faq_add?ticket_id=%s" %(active_id)
        return {
            'type': 'ir.actions.act_url',
            'url': question_url,
            'target': 'new',
        }
