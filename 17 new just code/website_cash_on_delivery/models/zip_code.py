# coding: utf-8

from odoo import fields, models


class CodZipCode(models.Model):
    _name = 'cod.zip.code'
    _description = 'COD Zip Code'

    name = fields.Char(
        string='Zip',
        required=True,
    )
    payment_acquirer_id = fields.Many2one(
#        'payment.acquirer',
        'payment.provider',
        string='Payment Acquirer',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
