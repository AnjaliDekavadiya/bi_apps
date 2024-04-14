# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.car_repair_maintenance_service.controllers.main import CarRepairSupport


class CarRepairSupport(CarRepairSupport):

    def _prepare_car_repair_service_vals(self, Partner, post):
        '''
            Override method with super to pass multiple nature of services on repair request services
        '''
        vals = super(CarRepairSupport, self)._prepare_car_repair_service_vals(Partner, post)
        if post.get("request_service_check"):
            services = request.httprequest.values.getlist('request_service_check')
            if services:
                vals.update({
                    'nature_of_service_ids': [(6, 0, map(int, services))],
                })
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
