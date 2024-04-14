from odoo import fields, models, api, _
from datetime import date, timedelta
import calendar

class KardexSunatWizard(models.TransientModel):
    _name = 'kardex.sunat.wizard'
    _description = 'Kardex Sunat Wizard Format 13.1'

    def _first_day(self):
        today_local = date.today()
        first_day = today_local - timedelta(days=today_local.day - 1)
        return first_day.strftime("%Y-%m-%d")

    def _last_day(self):
        today_local = date.today()
        last_day = str(calendar.monthrange(today_local.year, today_local.month)[1])
        return today_local.strftime("%Y-%m-") + last_day

    initial_date = fields.Date('Initial Date', default=_first_day)
    final_date = fields.Date('Final Date', default=_last_day)
    product_ids = fields.Many2many('product.product', string='Products')
    debug = fields.Boolean('Debug')

    def get_file(self):
        report = self.env.ref('account_reports.general_ledger_report')
        options = report.get_options(previous_options={})
        options['date']['date_from'] = self.initial_date
        options['date']['date_to'] = self.final_date
        options['report_code'] = 'kardex'
        options['report_name'] = 'Kardex Sunat'
        options['format'] = '1'
        options['product_ids'] = self.product_ids.ids
        options['debug'] = self.debug
        return report.export_kardex(options)