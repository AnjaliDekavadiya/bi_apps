# See LICENSE file for full copyright and licensing details.
from odoo import models


class ImportCustomersWizardWoocommerce(models.TransientModel):
    _name = 'import.customers.wizard.woocommerce'
    _inherit = 'import.customers.wizard'
    _description = 'Import Customers Wizard for WooCommerce'

    def run_import(self):
        integration = self._get_sale_integration()
        self = self.with_context(company_id=integration.company_id.id)

        job = self.with_delay(
            description=f'{integration.name}: Import Customers: Page 1',
        ).woocommerce_run_import_by_blocks(integration, 1, self.date_since)

        integration.job_log(job)

    def woocommerce_run_import_by_blocks(self, integration, page, date_since):
        self = self.with_context(company_id=integration.company_id.id)

        adapter = integration._build_adapter()
        ext_customers = adapter.get_customer_by_pages(date_since, page)

        if not ext_customers:
            return

        customers = list()
        for ext_customer in ext_customers:
            customers.append(self.env['integration.sale.order.factory']._create_customer(
                integration, ext_customer))

        page += 1

        job = self.with_delay(
            description=f'{integration.name}Import Customers: Page ' + str(page),
        ).woocommerce_run_import_by_blocks(integration, page, date_since)

        integration.job_log(job)
        return customers
