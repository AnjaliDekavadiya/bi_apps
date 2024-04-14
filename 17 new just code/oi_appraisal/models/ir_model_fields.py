'''
Created on Apr 2, 2023

@author: Zuhair Hammadi
'''
from odoo import models

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'
    
    def name_get(self):
        if self._context.get("from_appraisal_template"):
            res = []
            for record in self:
                res.append((record.id, record.field_description))
            res.sort(key = lambda item : item[1])
            return res
        return super(IrModelFields, self).name_get()