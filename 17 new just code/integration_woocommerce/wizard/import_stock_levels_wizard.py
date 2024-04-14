# See LICENSE file for full copyright and licensing details.

from odoo import models


class ImportStockLevelsWizard(models.TransientModel):
    _inherit = 'import.stock.levels.wizard'

    def run_import_stock_levels(self):
        integration = self.integration_id
        if not integration.is_woocommerce():
            return super(ImportStockLevelsWizard, self).run_import_stock_levels()

        external_data = self.env['integration.product.template.external'].search_read(
            domain=[('integration_id', '=', integration.id)],
            fields=['code'],
        )
        external_ids = [x['code'] for x in external_data if x['code']]

        limit = integration.get_external_block_limit()
        location_lines = self.get_location_lines(integration)

        for line in location_lines:
            idx = int()

            while external_ids:
                idx += 1
                job_kwargs = integration._job_kwargs_import_stock_from_location(line, block=idx)

                job = integration.with_delay(**job_kwargs)\
                    .import_stock_levels_integration_woocommerce(external_ids[:limit], line)

                integration.job_log(job)
                external_ids = external_ids[limit:]

        return self.raise_notification()
