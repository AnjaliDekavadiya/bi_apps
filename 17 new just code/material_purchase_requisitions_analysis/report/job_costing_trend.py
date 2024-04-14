# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models, tools


class ReportJobCostingVolumnTrend(models.Model):
    _name = 'report.material.requisition.analysis.trend'
    _auto = False
  
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True
    )
    qty = fields.Float(
        string='Requisition Quantity',
        readonly=True
    )
    product_uom_qty = fields.Float(
        'Picking Quantity',
        readonly=True
    )
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        readonly=True
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Internal Picking'),
                    ('purchase','Purchase Order'),
        ],
        string='Requisition Action',
        readonly=True
    )
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
        readonly=True
    )
    request_date = fields.Date(
        string='Requisition Date',
        required=True,
    )
    purchase_qty = fields.Float(
        string='Purchase Quantity',
        readonly=True
    )
    state = fields.Selection([
            ('draft', 'New'),
            ('cancel', 'Cancelled'),
            ('waiting', 'Waiting Another Move'),
            ('confirmed', 'Waiting Availability'),
            ('partially_available', 'Partially Available'),
            ('assigned', 'Available'),
            ('done', 'Done')
        ],
        string='Move Status',
        readonly=True
    )
    activity_state = fields.Selection([
            ('draft', 'RFQ'),
            ('sent', 'RFQ Sent'),
            ('to approve', 'To Approve'),
            ('purchase', 'Purchase Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled')
        ],
        string='Purchase Status',
        readonly=True
    )
    requisition_state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approved'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        string='Requisition Status',
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner', 
        'Picking Partner',
    )
    rec_partner_id = fields.Many2one(
        'res.partner', 
        'Vendor ',
    )
    picking_date = fields.Datetime(
        'Picking Date'
    )
    purchase_date = fields.Datetime(
        'Purchase Date'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Requisition Department',
        required=True,
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Requisition Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    receive_date = fields.Date(
        string='Requisition Received Date',
        readonly=True,
        copy=False,
    )
    date_end = fields.Date(
        string='Requisition Deadline', 
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )

    def _select(self):
        select_str = """
            SELECT
                req_line.id as id,
                sm.state as state,
                mpr.id as requisition_id,
                req_line.product_id,
                req_line.qty,
                req_line.uom,
                req_line.requisition_type,
                mpr.request_date,
                pol.product_qty as purchase_qty,
                sm.product_uom_qty,
                sp.partner_id as partner_id,
                po.partner_id as rec_partner_id,
                sm.date as picking_date,
                po.date_order as purchase_date,
                po.state as activity_state,
                mpr.state as requisition_state,
                mpr.department_id,
                mpr.employee_id,
                mpr.receive_date,
                mpr.date_end
         """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    req_line.id,
                    mpr.id,
                    req_line.product_id,
                    req_line.qty,
                    req_line.uom,
                    req_line.requisition_type,
                    mpr.request_date,
                    pol.product_qty,
                    sm.product_uom_qty,
                    sm.state,
                    sp.partner_id,
                    po.partner_id,
                    sm.date,
                    po.date_order,
                    po.state,
                    mpr.state,
                    mpr.department_id,
                    mpr.employee_id,
                    mpr.receive_date,
                    mpr.date_end
                    
        """
        return group_by_str

    def _from(self):
        from_str = """
                material_purchase_requisition_line req_line
                LEFT JOIN material_purchase_requisition mpr ON (req_line.requisition_id = mpr.id)
                LEFT JOIN purchase_order_line pol ON (pol.custom_requisition_line_id = req_line.id)
                LEFT JOIN purchase_order po ON (pol.order_id = po.id)
                LEFT JOIN stock_move sm ON (sm.custom_requisition_line_id = req_line.id)
                LEFT JOIN stock_picking sp ON (sm.picking_id= sp.id)
        """
        return from_str


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM  %s
                %s
        """ % (self._table, self._select(),self._from(), self._group_by()))