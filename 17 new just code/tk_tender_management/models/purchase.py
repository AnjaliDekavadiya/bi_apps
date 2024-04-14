# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class TenderPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tender_id = fields.Many2one('tender.information', string="Tender")

    def _prepare_invoice(self):
        res = super(TenderPurchaseOrder, self)._prepare_invoice()
        if self.tender_id:
            res['tender_id'] = self.tender_id.id
        return res


class ConstructionBills(models.Model):
    _inherit = 'account.move'

    tender_id = fields.Many2one('tender.information', string="Tender")
