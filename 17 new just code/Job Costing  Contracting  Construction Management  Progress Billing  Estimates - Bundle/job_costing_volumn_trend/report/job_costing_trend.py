# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models, tools


class ReportJobCostingVolumnTrend(models.Model):
    _name = 'report.job.cost.volumn.trend'
    _description = "Job Trend"
    _auto = False


    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
                readonly=True
    )
    purchase_id = fields.Many2one(
        'purchase.order', 
        string ='Purchase Order',
        readonly=True

    )
    date = fields.Date(
        string='Date',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True
    )

    product_qty = fields.Float(
        string='Planned Quantity',
        readonly=True
    )
  

    purchase_qty = fields.Float(
        string='Purchase Quantity',
        readonly=True
    )
    job_type_id = fields.Many2one(
        'job.type',
        string='Job Type',
        readonly=True

    )
    hours = fields.Float(
        string='Hours',
        readonly=True
    )
    direct_id = fields.Many2one(
        'job.costing',
        string='Job Costing'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        readonly=True
        
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        readonly=True

    )
#    account_invoice_id = fields.Many2one( odoo13
#        'account.invoice',
#        string='Vendor Bill',
#        readonly=True
#    )
    account_invoice_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        readonly=True
    )
    task_id = fields.Many2one(
        'project.task',
        string='Job Order',
        readonly=True
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True
    )
    vendor_quantity = fields.Float(
        string='Vendor Quantity',
        readonly=True
    )
    date_invoice = fields.Date(
        string='Vendor Bill Date',
        readonly=True
    )
    date_order_purchase = fields.Datetime(
        string='Purchase Order Date',
         readonly=True
    )
    timesheet_date = fields.Date(
        'TImesheet Date',
        required=True
    )
    timesheet_quantity = fields.Float(
        'Timesheet Quantity', 
        required=True
    )
    timesheet_id = fields.Many2one(
        'account.analytic.line',
        string='Analytic Account line',
        readonly=True
    )
    material_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions', 
    )
    requisition_qty = fields.Float(
        string='Requisition Quantity',
        readonly=True
    )
    # requisition_uom = fields.Many2one(
    #     'uom.uom',#product.uom in odoo11
    #     string='Requisition Unit of Measure',
    #     readonly=True
    # )
    # cost_uom = fields.Many2one(
    #     'uom.uom',#product.uom
    #     string='Cost Unit of Measure',
    #     readonly=True
    # )
    # purchase_uom = fields.Many2one(
    #     'uom.uom', 
    #     string='Purchase Unit of Measure', 
    #     readonly=True
    # )
    # vendor_uom = fields.Many2one(
    #     'uom.uom', 
    #     string='Vendor Unit of Measure',
    #     readonly=True
    # )


#    def _select(self):
#        select_str = """
#            SELECT
#                jb.id as id,
#                jb.hours,
#                jb.date,
#                jb.product_id,
#                jb.product_qty as product_qty,
#                jb.job_type_id,
#                jb.direct_id,
#                jb.job_type,
#                -- jb.uom_id as cost_uom, 
#                jo.id as purchase_id,
#                ai.id as account_invoice_id,
#                ai.date_invoice,
#                aal.id as timesheet_id,
#                mp.id as material_requisition_id,
#                mp.qty as requisition_qty,
#                -- mp.uom as requisition_uom,
#                js.partner_id,
#                js.project_id,
#                js.task_id,
#                js.analytic_id,
#                -- jp.price_unit,
#                -- jp.product_uom as purchase_uom,
#                al.quantity as vendor_quantity,
#                -- al.uom_id as vendor_uom,
#                jo.date_order as date_order_purchase,
#                jp.product_qty as purchase_qty,
#                aal.date as timesheet_date,
#                aal.unit_amount as Timesheet_quantity
#   
#                    
#        """
#        return select_str
        
    def _select(self):
        select_str = """
            SELECT
                jb.id as id,
                jb.hours,
                jb.date,
                jb.product_id,
                jb.product_qty as product_qty,
                jb.job_type_id,
                jb.direct_id,
                jb.job_type,
                -- jb.uom_id as cost_uom, 
                jo.id as purchase_id,
                ai.id as account_invoice_id,
                ai.invoice_date as date_invoice,
                aal.id as timesheet_id,
                mp.id as material_requisition_id,
                mp.qty as requisition_qty,
                -- mp.uom as requisition_uom,
                js.partner_id,
                js.project_id,
                js.task_id,
                js.analytic_id,
                -- jp.price_unit,
                -- jp.product_uom as purchase_uom,
                al.quantity as vendor_quantity,
                -- al.uom_id as vendor_uom,
                jo.date_order as date_order_purchase,
                jp.product_qty as purchase_qty,
                aal.date as timesheet_date,
                aal.unit_amount as Timesheet_quantity
   
                    
        """
        return select_str


#    def _group_by(self):
#        group_by_str = """
#                GROUP BY
#                    jb.id,
#                    jb.date,
#                    jb.product_id,
#                    jb.product_qty,
#                    jb.hours,
#                    jb.job_type_id,
#                    jb.direct_id,
#                    jb.job_type,
#                    js.partner_id,
#                    js.project_id,
#                    js.task_id,
#                    js.analytic_id,
#                    jo.id,
#                    al.quantity,
#                    ai.id,
#                    mp.id,
#                    mp.qty,
#                    ai.date_invoice,
#                    jo.date_order,
#                    jp.product_qty,
#                    aal.id,
#                    aal.date,
#                    aal.unit_amount

#        """
#        return group_by_str
#        
    def _group_by(self):
        group_by_str = """
                GROUP BY
                    jb.id,
                    jb.date,
                    jb.product_id,
                    jb.product_qty,
                    jb.hours,
                    jb.job_type_id,
                    jb.direct_id,
                    jb.job_type,
                    js.partner_id,
                    js.project_id,
                    js.task_id,
                    js.analytic_id,
                    jo.id,
                    al.quantity,
                    ai.id,
                    mp.id,
                    mp.qty,
                    ai.invoice_date,
                    jo.date_order,
                    jp.product_qty,
                    aal.id,
                    aal.date,
                    aal.unit_amount

        """
        return group_by_str

#    def _from(self):
#        from_str = """
#                job_cost_line jb
#                left join job_costing js on (jb.direct_id = js.id)
#                left join purchase_order_line jp on (jp.job_cost_line_id = jb.id)
#                left join purchase_order jo on (jp.order_id = jo.id)
#                left join account_invoice_line al on (al.job_cost_line_id = jb.id)
#                left join account_invoice ai on (al.invoice_id = ai.id)
#                left join account_analytic_line aal on (aal.job_cost_line_id = jb.id)
#                left join material_purchase_requisition_line mp on (mp.custom_job_costing_line_id = jb.id)
#                left join material_purchase_requisition mpr on (mp.requisition_id = mpr.id)

#                WHERE
#                    jp.state in ('purchase', 'done') or
#                    ai.state in ('open', 'paid') or
#                    aal.job_cost_line_id = jb.id or
#                    mpr.state not in ('cancel')
#        """
#        return from_str

    def _from(self):
        from_str = """
                job_cost_line jb
                left join job_costing js on (jb.direct_id = js.id)
                left join purchase_order_line jp on (jp.job_cost_line_id = jb.id)
                left join purchase_order jo on (jp.order_id = jo.id)
                left join account_move_line al on (al.job_cost_line_id = jb.id)
                left join account_move ai on (al.move_id = ai.id)
                left join account_analytic_line aal on (aal.job_cost_line_id = jb.id)
                left join material_purchase_requisition_line mp on (mp.custom_job_costing_line_id = jb.id)
                left join material_purchase_requisition mpr on (mp.requisition_id = mpr.id)

                
        """
        return from_str


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM  %s 
                %s
        """ % (self._table, self._select(), self._from(), self._group_by()))

