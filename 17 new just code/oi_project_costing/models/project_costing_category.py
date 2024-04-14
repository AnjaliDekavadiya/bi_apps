'''
Created on Apr 22, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
import re

def normilize(*names):
    name = ' '.join(names)
    return re.sub('\W',' ', name.lower()).strip().replace(' ', '_')    

def remove_unchange(vals, record):
    for fname in list(vals):
        value = vals[fname]
        field = record._fields[fname]
        value = field.convert_to_cache(value, record, validate=False)
        value = field.convert_to_record(value, record)
        if record[fname] == value:
            vals.pop(fname)
            
_view_arch = """
<data>
<notebook> 
    <page name="%(name)s" string="%(name)s" >
        <field name="%(field_name)s" widget="section_and_note_one2many" mode="tree" nolabel="1" context="{'default_category_id' : %(id)d}">
            <tree editable="bottom">            
                <control>
                    <create string="Add a line" />
                    <create string="Add a section" context="{'default_display_type': 'line_section'}" />
                </control>                
                <field name="category_id" column_invisible="1" />
                <field name="display_type" column_invisible="1" />
                <field name="sequence" widget="handle" />                    
                <field name="name" />
                <field name="product_id" />
                <field name="product_uom_id" />
                <field name="plan_price"/>
                <field name="actual_price"/>
                <field name="plan_qty"/>
                <field name="actual_qty"/>
                <field name="plan_amount_display" string="Plan Amount" sum="Total"/>
                <field name="actual_amount_display" string="Actual Amount" sum="Total"/>                                    
            </tree>
        </field>
    </page>
</notebook>
</data>
"""            
            
class ProjectCostingCategory(models.Model):
    _name = 'project.costing.category'
    _description = _name
    _order = 'sequence,id'
    
    sequence = fields.Integer()
    name = fields.Char()
    code = fields.Char()
    
    field_id = fields.Many2one('ir.model.fields')
    field_name = fields.Char(related='field_id.name', readonly = True)
    view_id = fields.Many2one('ir.ui.view')        
    
    _sql_constraints = [
        ('uk_name', 'unique(name)', 'Name must be unique!'),
        ('uk_code', 'unique(code)', 'Code must be unique!')
        ]
        
    
    def _create_field(self):
        if self.field_id:
            if self.field_id.field_description != self.name:
                self.field_id.field_description = self.name
            return
        self = self.sudo()
        vals = {            
            'field_description' : self.name,
            'name' : 'x_%s_project_costing_ids' % (normilize(self.code)),
            'model_id' : self.env['ir.model']._get_id('account.analytic.account'),
            'ttype':'one2many',
            'relation':'project.costing',
            'relation_field': 'analytic_id',
            'domain': "[('category_id.code','=','%s')]" %(self.code),
            'copied' : False                      
            }
        self.field_id=self.env['ir.model.fields'].create(vals)
    
    
    def _get_view_arch(self):
        vals, = self.read([], load = False)
        return _view_arch % vals
        
    
    def _create_view(self):
        self = self.sudo()
        inherit_id = self.env.ref('oi_project_costing.view_analytic_project_costing')
        vals = {
            'arch' : self._get_view_arch(),
            'priority' : self.search([]).ids.index(self.id) + 1,
            'inherit_id' : inherit_id.id,
            'type' : inherit_id.type,
            'model' : inherit_id.model,
            'name' : '%s.%s' % (inherit_id.name, self.code)
            }
        
        if self.view_id:
            remove_unchange(vals, self.view_id)
            self.view_id.write(vals)
        else:
            self.view_id = self.env['ir.ui.view'].create(vals)
    
    @api.model
    def _update_views(self):        
        for record in self.search([]):
            record._create_field()
            record._create_view()
            
            
    
    def unlink(self):
        view_ids = self.mapped('view_id')
        field_ids = self.mapped('field_id')
        
        res = super(ProjectCostingCategory, self).unlink()
        
        view_ids.unlink()
        field_ids.unlink()
        
        self.sudo()._update_views()
        
        return res
        
        
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(ProjectCostingCategory, self).create(vals_list)
        self.sudo()._update_views()
        return records
    
    def write(self, vals):
        res = super(ProjectCostingCategory, self).write(vals)
        self.sudo()._update_views()
        return res
    
    def create_product_category(self):
        for record in self:
            record.env['product.category'].sudo().create({
                'name':record.name,
                'property_valuation':"real_time" if record.code == "3" else "manual_periodic",
                'costing_category_id':record.id,
                })
            
            