# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields


class JobTransactionMixin(models.AbstractModel):
    _name = 'job.transaction.mixin'
    _description = 'Job Transaction Mixin'

    job_transaction_count = fields.Integer(
        string='Job Transaction Count',
    )

    def increment_counter(self):
        self.ensure_one()
        value = self.job_transaction_count + 1
        self.job_transaction_count = value
        return value

    def update_transaction_kwargs(self):
        self.ensure_one()
        vals = dict()
        if self.job_transaction_count:
            vals['check_external'] = True
        return vals
