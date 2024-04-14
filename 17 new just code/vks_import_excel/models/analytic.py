# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AnalyticMixin(models.AbstractModel):
    _inherit = 'analytic.mixin'
    
    #Thêm bởi Tuấn - 23/10/2023 - Hàm lấy đối tượng tham chiếu để chuẩn hóa kiểu json
    @api.model
    def vks_get_json_model(self):
        return 'account.analytic.account'
    
    #Thêm bởi Tuấn - 23/10/2023 - Hàm lấy key để chuẩn hóa kiểu json
    @api.model
    def vks_get_json_field_key(self):
        return 'name'