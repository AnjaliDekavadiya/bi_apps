## -*- coding: utf-8 -*-
## Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

#import logging
#from collections import defaultdict

#from odoo import api, fields, models, tools, SUPERUSER_ID, _
#from odoo.exceptions import AccessError
#from odoo.tools import config, human_size, ustr, html_escape

#_logger = logging.getLogger(__name__)


#class IrAttachment(models.Model):
#    """Attachments are used to link binary files or url to any openerp document.

#    """
#    _inherit = 'ir.attachment'

#    @api.model
#    def _hook_warning_employee_check(self, require_employee):
#        if require_employee:
#            if not (self.env.user._is_admin() or self.env.user.has_group('base.group_user')):
#                raise AccessError(_("Sorry, you are not allowed to access this document."))
#            return True
#    
#    @api.model
#    def check(self, mode, values=None):
#        """Restricts the access to an ir.attachment, according to referred model
#        In the 'document' module, it is overriden to relax this hard rule, since
#        more complex ones apply there.
#        """
#        # collect the records to check (by model)
#        model_ids = defaultdict(set)            # {model_name: set(ids)}
#        require_employee = False
#        if self:
#            self._cr.execute('SELECT res_model, res_id, create_uid, public FROM ir_attachment WHERE id IN %s', [tuple(self.ids)])
#            for res_model, res_id, create_uid, public in self._cr.fetchall():
#                if public and mode == 'read':
#                    continue
#                if not (res_model and res_id):
#                    if create_uid != self._uid:
#                        require_employee = True
#                    continue
#                model_ids[res_model].add(res_id)
#        if values and values.get('res_model') and values.get('res_id'):
#            model_ids[values['res_model']].add(values['res_id'])

#        # check access rights on the records
#        for res_model, res_ids in model_ids.items():
#            # ignore attachments that are not attached to a resource anymore
#            # when checking access rights (resource was deleted but attachment
#            # was not)
#            if res_model not in self.env:
#                require_employee = True
#                continue
#            records = self.env[res_model].browse(res_ids).exists()
#            if len(records) < len(res_ids):
#                require_employee = True
#            # For related models, check if we can write to the model, as unlinking
#            # and creating attachments can be seen as an update to the model
#            records.check_access_rights('write' if mode in ('create', 'unlink') else mode)
#            records.check_access_rule(mode)

#        self._hook_warning_employee_check(require_employee)#hook method #probuse

#   
