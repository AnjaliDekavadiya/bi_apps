'''
Created on Mar 16, 2023

@author: Zuhair Hammadi
'''

from odoo import models, fields, api, _
from odoo.tools.sql import index_exists

class AppraisalNameMixin(models.AbstractModel):    
    _name = 'appraisal.name.mixin'
    _description = 'Appraisal Name Mixin'
    
    name = fields.Char(required=True, translate=True)
    active= fields.Boolean(default=True)
    company_id = fields.Many2one('res.company')

    _sql_constraints = [
        ('name_uniq_en_us', '', 'Name must be unique!'),
    ]
                    
    def _auto_init(self):
        super()._auto_init()
        if self._abstract:
            return

        self._create_name_unique_index()
            
    def _create_name_unique_index(self, create_constraint = False):
        for code,__ in self.env['res.lang'].get_installed():
            code = code.lower()
            index_name = f'{self._table}_name_uniq_{code}'            
            if not index_exists(self.env.cr, index_name):
                self.env.cr.execute(f"""
                    CREATE UNIQUE INDEX {index_name}
                    ON {self._table}((name->>'{code}'), COALESCE(company_id,0));
                """)    
            
            if not create_constraint:
                continue
            self.env.registry._sql_constraints.add(index_name) 
            
            module_id= self.env.ref(f'base.module_{self._module}').id
            if not self.env['ir.model.constraint'].search([('name','=', index_name)]):
                constraint = self.env['ir.model.constraint'].create({
                    'name' : index_name,
                    'message' : _('Name must be unique!'),
                    'model' : self.env['ir.model']._get_id(self._name),
                    'module' : module_id,
                    'type' : 'u',
                    })
                for code,__ in self.env['res.lang'].get_installed():
                    if code == self.env.lang:
                        continue
                    context = {'lang' : code}  # @UnusedVariable                    
                    constraint.with_context(lang = code).message = _('Name must be unique!')
                                            
    def _register_hook(self):
        super(AppraisalNameMixin, self)._register_hook()    
        if self._abstract:
            return
        self._create_name_unique_index(True)
                            
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default = default or {}
        default.setdefault('name', _('%s Copy') % self.name)        
        return super(AppraisalNameMixin, self).copy(default)
    