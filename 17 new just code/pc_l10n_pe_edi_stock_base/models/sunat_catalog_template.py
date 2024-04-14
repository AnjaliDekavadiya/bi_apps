from odoo import fields, models, api
from odoo.osv import expression

class SunatCatalogTemplate(models.Model):
    _name = 'sunat.catalog.tmpl'
    _description = 'Sunat Catalog Template'

    code = fields.Char('Code')
    name = fields.Char('Description')

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.code, r.name)))
        return result
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        # OVERRIDE
        domain = domain or []
        if operator != 'ilike' or (name or '').strip():
            name_domain = ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)