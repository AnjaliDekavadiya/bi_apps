# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')

    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    limit_sale_order = fields.Integer(string='Limit Sale Order', default=15)

    def write(self, values):
        res = super(ResUsers, self).write(values)
        if 'default_picking_type_ids' in values or 'warehouse_ids' in values:
            obj1 = self.env['ir.module.module'].search([('name', '=', 'warehouse_stock_restrictions')])
            obj1.button_immediate_upgrade()
        return res

class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        for rec in self:
            if rec.state == 'draft':
                return True

            user_locations = []
            for i in rec.env.user.stock_location_ids:
                user_locations.append(i.id)

            # user_locations = rec.env.user.stock_location_ids
            if rec.env.user.restrict_locations:
                message = _(
                    'Invalid Location. You cannot process this move since you do '
                    'not control the location "%s". '
                    'Please contact your Administrator.')

                if rec.location_id.id not in user_locations:
                    raise UserError(message % rec.location_id.name)
                elif rec.location_dest_id.id not in user_locations:
                    raise UserError(message % rec.location_dest_id.name)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None):
        res = super(SaleOrder, self)._search(args, offset=offset, limit=self.env.user.limit_sale_order, order=order)
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def get_view(self, view_id=None, view_type='tree', **options):
        result = super(StockPicking, self).get_view(view_id, view_type, **options)
        if self.env.user.has_group('warehouse_stock_restrictions.group_restrict_button') and view_type == 'tree':
            result['arch'] = result['arch'].replace('<tree', '<tree create="0"')
        if self.env.user.has_group('warehouse_stock_restrictions.group_restrict_button') and view_type == 'form':
            result['arch'] = result['arch'].replace('<form', '<form create="0"')
        return result