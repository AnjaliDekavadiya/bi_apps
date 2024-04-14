import base64
import csv
from io import StringIO

from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import UserError


class AmazonReportTypeField(models.Model):
    _name = 'amazon.report.type.field'
    _description = "Amazon Report Type Fields"

    report_type_id = fields.Many2one(
        "amazon.report.type",
        string="Report Type"
    )
    sequence = fields.Integer(string="Sequence", readonly=True)
    name = fields.Char(string="Field Name")
    example_value = fields.Char(string="Example Value")
    model_id = fields.Many2one(
        "ir.model", string="Model",
        related="report_type_id.model_id"
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="[('model_id', '=', model_id)]"
    )

    def create_odoo_field(self):
        self.ensure_one()
        if self.field_id:
            raise UserError(_("Field already exists!"))
        if not self.model_id:
            raise UserError(_("No Report model found!"))
        if self.example_value.isdigit() and int(self.example_value) < 99999:
            field_type = "float"
        else:
            field_type = "char"
        field_vals = {
            "name": f"x_{self.name.replace('-', '_').replace(' ', '_')}",
            "model_id": self.model_id.id,
            "ttype": field_type,
            "field_description": self.name,
        }
        odoo_field = self.env["ir.model.fields"].create(field_vals)
        self.write({"field_id": odoo_field.id})
        return odoo_field


class AmazonReportType(models.Model):
    _inherit = 'amazon.report.type'

    ir_cron_ids = fields.One2many("ir.cron", "amazon_report_type_id", string="Crons")
    report_field_ids = fields.One2many(
        "amazon.report.type.field", "report_type_id", string="Report Fields"
    )
    model_id = fields.Many2one(
        "ir.model", string="Model", readonly=True,
    )
    is_only_update = fields.Boolean(
        string="Only Update?",
        help="If checked, only update existing records, don't create new ones."
    )
    tree_view_id = fields.Many2one(
        "ir.ui.view", string="Report Lines Tree View",
        domain="[('model', '=', model_id)]",
        readonly=True
    )

    def generate_auto_retrieve_process_report(self, marketplaces=False,
                                              processing_type="normal"):
        self.ensure_one()
        cron_report_vals = {
            "account_id": 1,
            "report_type_id": self.id,
        }
        if marketplaces:
            cron_report_vals['amz_marketplace_ids'] = [(6, 0, marketplaces.ids)]
        code = f"report = model.create({str(cron_report_vals)})\n"
        code += "report.request_report()\n"
        request_report_cron = self.env['ir.cron'].create({
            'name': f"Request Amazon Report: {self.name} [{self.technical_name}]",
            'amazon_report_type_id': self.id,
            'model_id': self.env.ref('amazon_connector_base.model_amazon_report_log').id,
            'state': 'code',
            'interval_number': 1,
            'interval_type': 'days',
            'user_id': self.env.user.id,
            'numbercall': -1,
            'doall': False,
            'nextcall': fields.Datetime.now() + relativedelta(days=1),
            'code': code,
        })
        cron_report_domain = [("state", "=", "DRAFT"), ("report_type_id", "=", self.id)]
        code = f"report = model.search({str(cron_report_domain)}, limit=1)\n"
        code += "report.check_report_status()\n"
        if processing_type == "spreadsheet":
            code += "report.convert_report_to_document()\n"
        elif processing_type == "record":
            code += "report.create_odoo_report_lines()\n"
        else:
            # normal case
            code += "report.process_report()\n"
        process_report_cron = request_report_cron.copy({
            'name': f"Process Amazon Report: {self.name} [{self.technical_name}]",
            'nextcall': fields.Datetime.now() + relativedelta(days=1) + relativedelta(minutes=5),
            'code': code,
        })
        return process_report_cron

    def generate_model_for_report_type(self):
        self.ensure_one()
        if self.model_id:
            return True
        report_log = self.env['amazon.report.log'].search([
            ('report_type_id', '=', self.id),
            ('report_file', '!=', False)
        ], limit=1)
        if not report_log:
            raise UserError(_("No report log found for this report type!\n"
                              "Please request a report first."))
        imp_file = StringIO(base64.b64decode(report_log.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        first_row = next(reader)
        # go to 3rd row in case of settlement report
        second_row = next(reader)
        fields_vals = [(5, 0, 0)]
        for seq, field in enumerate(reader.fieldnames):
            field_vals = {
                "sequence": seq,
                "name": field,
                "example_value": second_row[field],
                "report_type_id": self.id,
            }
            fields_vals.append((0, 0, field_vals))
        model_name = self.technical_name.lower()  #.replace("_", ".")
        report_model = self.env["ir.model"].create({
            "name": self.name,
            "model": f"x_{model_name}",
        })
        report_model.write({
            "access_ids": [(0, 0, {
                "name": f"access.model.amazon.report.{model_name}",
                "group_id": self.env.ref("base.group_user").id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            })],
            "field_id": [(0, 0, {
                "name": "x_report_log_id",
                "field_description": "Amazon Report Log",
                "ttype": "many2one",
                "relation": "amazon.report.log",
            })],
        })
        self.write({
            "model_id": report_model,
            "report_field_ids": fields_vals,
        })

    def create_update_tree_view_for_report_lines(self):
        self.ensure_one()
        tree_arch = '<tree string="%s">\n    <field name="create_date" />\n' % self.name
        tree_field = '    <field name="%s" optional="show"/>\n'
        for field in self.report_field_ids:
            if not field.field_id:
                continue
            tree_arch += tree_field % field.field_id.name
        tree_arch += "</tree>"
        if not self.tree_view_id:
            tree_view = self.env["ir.ui.view"].create({
                "name": self.name,
                "type": "tree",
                "model": self.model_id.model,
                "arch": tree_arch,
            })
            self.write({"tree_view_id": tree_view.id})
        elif self.tree_view_id.arch != tree_arch:
            self.tree_view_id.write({
                "arch": tree_arch,
            })
        return True
