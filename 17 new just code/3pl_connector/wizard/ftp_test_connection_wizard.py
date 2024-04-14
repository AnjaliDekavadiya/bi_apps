# -*- coding: utf-8 -*-

from odoo import fields, models


class FTPTestConnectionWizard(models.TransientModel):
    _name = "ftp.test.connection.wizard"
    _description = 'Test Connection'

    name = fields.Char('Connection Succeeded!!!!!')
