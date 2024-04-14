from odoo import api, models

NEW_USER_FIELDS = [
    'pos_access_close_sent_kitchen',
    'pos_access_decrease_quantity_sent_kitchen',
    'pos_access_delete_order_sent_kitchen',
    'pos_access_delete_orderline_sent_kitchen',
]


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        result['search_params']['fields'] += NEW_USER_FIELDS
        return result
