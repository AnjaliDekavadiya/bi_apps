# -*- coding: utf-8 -*-
from odoo import api, models, fields


class PosPayment(models.Model):
    _inherit = "pos.payment"

    covert_change_to_credit = fields.Boolean(
        "Change to Credit",
        readonly=True
    )
    used_credit_payment = fields.Boolean(
        "Credit Payment",
        readonly=True
    )
    pos_branch_id = fields.Many2one(
        'pos.branch',
        related='pos_order_id.pos_branch_id',
        store=True,
        string='Branch',
        readonly=True)

    def _export_for_ui(self, payment):
        datas = super()._export_for_ui(payment)
        datas.update({
            'covert_change_to_credit': payment.covert_change_to_credit,
            'used_credit_payment': payment.used_credit_payment,
        })
        return datas