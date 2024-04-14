# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime


class AppointmentStatEndWizard(models.TransientModel):

    _name = 'appointment.start.end.wizard'
    _description = "This is form for view of tender"
    
    phy_id = fields.Many2one("medical.physician", 'Name Of Physician', required=True)
    s_date = fields.Date('Start Date')
    e_date = fields.Date('End Date')
    
    def show_record(self):
        pres_request_obj = self.env['medical.appointment']
        res_ids = []
        for res in self:
            record = pres_request_obj.search([('doctor', '=', res.phy_id.id), ('validity_status', '=', 'invoiced')])
            for rec in record:
                rec_startdate = datetime.strptime(str(rec.appointment_sdate), '%Y-%m-%d %H:%M:%S')
                if res.s_date and res.e_date:
                    if (str(res.s_date) <= str(rec_startdate.date()) and str(res.e_date) >= str(rec_startdate.date())):
                        res_ids.append(rec.inv_id.id)
                elif res.s_date and not res.e_date:  
                    if (str(res.s_date)==str(rec_startdate.date())):
                        res_ids.append(rec.inv_id.id)
                elif str(res.e_date) and not res.s_date:
                    if (str(res.e_date) >= str(rec_startdate.date())):
                        res_ids.append(rec.inv_id.id) 
                else:
                    res_ids.append(rec.inv_id.id)  
        imd = self.env['ir.model.data']
        res_id = imd._xmlid_to_res_id('account.view_move_tree')
        res_id_form = imd._xmlid_to_res_id('account.view_move_form')
        
        result = {
            'name': 'Create invoice',
            'type': 'tree',
            'views': [(res_id, 'tree'), (res_id_form, 'form')],
            'target': 'current',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        if res_ids:
            result['domain'] = "[('id','in',%s)]" % res_ids
        return result  

#     def show_record(self, cr, uid, ids, context=None):
#         v=[]
#         q = self.browse(cr,uid,ids)[0]
#         rec= self.pool.get('medical.appointment').search(cr,uid,[('doctor','=',q.phy_id.id),('validity_status','=','invoiced')])
#         obj = self.pool.get('medical.appointment')
#         res = obj.browse(cr, uid, rec)
#         for r in res:
#             b_day = datetime.strptime((r.appointment_sdate), '%Y-%m-%d %H:%M:%S')
#             if q.s_date and q.e_date:
#                 if (q.s_date <= str(b_day.date()) and q.e_date >= str(b_day.date())):
#                     v.append(r.inv_id.id)
#             elif q.s_date and not q.e_date:  
#                 if (q.s_date==str(b_day.date())):
#                     v.append(r.inv_id.id)
#             elif q.e_date and not q.s_date:  
#                 if (q.e_date >= str(b_day.date())):
#                     v.append(r.inv_id.id) 
#             else:
#                 v.append(r.inv_id.id)  
#         return {
#         'name': _('Customer Invoices'),
#         'view_type': 'form',
#         'view_mode':'tree,form',
#         'res_model': 'account.invoice',
#         'type': 'ir.actions.act_window',
#         'domain': [('id', 'in', v)],
#         'context': context,
#     }
#