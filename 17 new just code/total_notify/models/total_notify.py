#coding: utf-8

import base64
import calendar
import logging
import tempfile

from calendar import monthcalendar
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import  _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import single_email_re, SQL, email_split_tuples
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")

@api.model
def _lang_get(self):
    languages = self.env["res.lang"].search([])
    return [(language.code, language.name) for language in languages]

def _calc_month_day_byday_and_weekday(next_month_day, byday, week_list):
    """
    Method to return month day based on week day and the number of month week
    Zero might be returned only in case the number of week is too big, e.g fith Sunday might not exists

    Args:
     * next_month_day - date.date
     * byday - the number of week in a month [1-4; -1], where 1 is the first week
     * weeklist - the weekday [0-6]

    Returns:
     * integer

    Extra info:
     * 5th and bigger byday is not supported!
    """
    monthcal = monthcalendar(year=next_month_day.year, month=next_month_day.month)
    if byday != -1:
        byday -= 1
    these_days = list(filter(bool, [week_ca[week_list] for week_ca in monthcal]))
    new_day = these_days[byday]
    return new_day


class total_notify(models.Model):
    """
    The model to prepare and forward a list of records
    """
    _name = "total.notify"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "List Reminder"
    _mail_post_access = "read"

    @api.model
    def _return_year_month(self):
        """
        The method to return year months
        """
        month = 1
        months = []
        while month < 13:
            months.append((str(month), calendar.month_name[month]))
            month += 1
        return months

    @api.depends("model")
    def _compute_ir_model_id(self):
        """
        Compute method for ir_model_id

        Extra info:
         * we use compute/inverse/onchange instrad of simple 'related' to the backward compatibility
        """
        for notify in self:
            notify.ir_model_id = self.env["ir.model"].search([("model", "=", notify.model)])

    @api.depends("ir_model_id")
    def _compute_model(self):
        """
        Compute method for model period_ids, column_ids, domain, sort_field_id, partner_model_field, user_model_field
        """
        for notify in self:
            notify.model = notify.ir_model_id and notify.ir_model_id.model or False
            notify.period_ids = False
            notify.column_ids = False
            notify.domain = "[]"
            notify.sort_field_id = False
            notify.partner_model_field = False
            notify.user_model_field = False

    @api.depends("period_ids", "period_ids.field_id", "period_ids.period_value",
        "period_ids.period_type", "period_ids.inclusive_this", "period_ids.compared_to", "period_ids.compared_to_type",
        "period_ids.compared_to_value")
    def _compute_period_title(self):
        """
        Compute method for period_title & period_domain

        Methods:
         * _return_translation_for_field_label
        """
        for notify in self:
            merged_periods = {}
            for period in notify.period_ids:
                field = notify._return_translation_for_field_label(field=period.field_id)
                if merged_periods.get(field):
                    or_str = _("or")
                    merged_periods[field] = {
                        "domain": ["|"] + merged_periods[field]["domain"] + safe_eval(period.domain),
                        "title": u"{} {} {}".format(merged_periods[field]["title"], or_str,  period.title)
                    }
                else:
                    merged_periods[field] = {
                        "domain": safe_eval(period.domain),
                        "title": period.title,
                    }
            domain = []
            title = ""
            for field, values in merged_periods.items():
                domain += values["domain"]
                title += "{}: {}; ".format(field, values["title"])
            notify.period_domain = domain
            notify.period_title = title and title[:-2] or ""

    def _inverse_ir_model_id(self):
        """
        Inverse method for ir_model_id
        """
        for notify in self:
            notify.model = notify.ir_model_id and notify.ir_model_id.model or False

    @api.constrains("partner_id", "partner_model_field")
    def _check_partner_model_field(self):
        """
        Constraint method to make sure filters by partner and user are correct res.partner and res.users fields
        """
        for notify in self:
            if notify.partner_id and notify.partner_model_field:
                fields_chain = notify.partner_model_field.split(".")
                current_parent = notify.model
                c_field_instance = False
                for c_field in fields_chain:
                    c_field_instance = self.sudo().env["ir.model.fields"].search([
                        ("model", "=", current_parent), ("name", "=", c_field)
                    ])
                    current_parent = c_field_instance.relation
                else:
                    if c_field_instance.relation != "res.partner":
                        raise ValidationError(_(
                            "Error! The 'Filter by partner' field should be Many2one linked to the res.partner model"
                        ))

    @api.constrains("user_id", "user_model_field")
    def _check_user_model_field(self):
        """
        Constraint method to make sure filters by partner and user are correct res.partner and res.users fields
        """
        for notify in self:
            if notify.user_id and notify.user_model_field:
                fields_chain = notify.user_model_field.split(".")
                current_parent = notify.model
                c_field_instance = False
                for c_field in fields_chain:
                    c_field_instance = self.sudo().env["ir.model.fields"].search([
                        ("model", "=", current_parent), ("name", "=", c_field)
                    ])
                else:
                    if c_field_instance.relation != "res.users":
                        raise ValidationError(_(
                            "Error! The 'Filter by responsible' field should be Many2one linked to the res.users model"
                        ))

    @api.constrains("include_table_in_message", "send_by_xls", "send_pdf")
    def _check_include_table_in_message(self):
        """
        Constraint method to make sure filters by partner and user are correct res.partner and res.users fields
        """
        for notify in self:
            if not notify.include_table_in_message and not notify.send_by_xls and not notify.send_pdf:
                raise ValidationError(_("Turn on either 'List in Mail Body' or attaching Excel Table/PDF Version!"))

    @api.constrains("email_from")
    def _check_email_from(self):
        """
        Email from should be a valid email address
        """
        for notify in self:
            if notify.email_from:
                split_results = email_split_tuples(notify.email_from)
                email = False
                if split_results:
                    name, email = split_results[0]
                if not email or not single_email_re.match(email):
                    raise ValidationError(_("Email from does not a valid email address"))

    name = fields.Char(string="Reference", required=True)
    ir_model_id = fields.Many2one(
        "ir.model",
        string="Model",
        compute=_compute_ir_model_id,
        inverse=_inverse_ir_model_id,
    )
    model = fields.Char(
        string="Model name",
        compute=_compute_model,
        store=True,
        readonly=False,
    )
    domain = fields.Text(
        string="Filters",
        compute=_compute_model,
        store=True,
        required=True,
        readonly=False,
        default="[]",
    )
    period_ids = fields.One2many(
        "relative.period",
        "total_notify_id",
        string="Periods",
        compute=_compute_model,
        store=True,
        readonly=False,
        copy=True,
    )
    period_domain  = fields.Char(string="Domain by periods", compute=_compute_period_title)
    period_title = fields.Char(
        string="If the reminder is sent today, the periods will be",
        compute=_compute_period_title,
    )
    column_ids = fields.One2many(
        "fields.line",
        "total_notify_id",
        string="Columns to show",
        compute=_compute_model,
        store=True,
        readonly=False,
        copy=True,
    )
    sort_field_id = fields.Many2one(
        "ir.model.fields",
        string="Sorting field",
        compute=_compute_model,
        store=True,
        readonly=False,
        help="How to sort found records. If not defined, standard sorting will be applied",
    )
    sort_field_direction = fields.Selection(
        [("asc", "Ascending"), ("desc", "Descending")],
        string="Sort direction",
        default="asc",
    )
    group_field_id = fields.Many2one(
        "ir.model.fields",
        string="Group by field",
        help="How to group records. If not defined, no grouping will be applied",
    )
    lang = fields.Selection(_lang_get, "Language", default=api.model(lambda self: self.env.lang))
    include_table_in_message = fields.Boolean(
        string="List in Mail Body",
        default=True,
        help="If checked, this list will be inside a message body. If not checked, do not forget to turn on the \
'Attach Excel Table' or 'Attach PDF'. Otherwise, the email will contain only greetings",
    )
    send_by_xls = fields.Boolean(
        string="Attach Excel Table",
        default=False,
        help="If checked, the email will have the .xlsx table with all found records attached",
    )
    send_pdf = fields.Boolean(
        string="Attach PDF version",
        default=False,
        help="If checked, the reminder will have the .pdf version of the table attached. Please use only if the \
number of columns might suit the A4 width",
    )
    url_included = fields.Boolean(
        string="Provide Links",
        default=True,
        help="If checked, the reminder will have the reference in each row for the source Odoo record. If you sent \
this reminder to your partners, links will not have any use for them",
    )
    extra_message = fields.Html(
        string="Message introduction",
        help="This text will be included at the beginning of the sent message",
    )
    active = fields.Boolean(string="Active", default=True)
    # To the needs of proper recurrency (as it is done in calendar)
    last_sent_date = fields.Date(string="Last Sent Date")
    next_sent_date = fields.Date(string="Next To Send Date", default=lambda self: fields.Date.today())
    interval = fields.Integer(string="Interval", default=1)
    periodicity = fields.Selection(
        [("daily", "Day(s)"), ("weekly", "Week(s)"), ("monthly", "Month(s)"), ("yearly", "Year(s)")],
        string="Repeat Every",
        default="monthly",
    )
    mo = fields.Boolean("Mon")
    tu = fields.Boolean("Tue")
    we = fields.Boolean("Wed")
    th = fields.Boolean("Thu")
    fr = fields.Boolean("Fri")
    sa = fields.Boolean("Sat")
    su = fields.Boolean("Sun")
    month_by = fields.Selection(
        [
            ("the_first_date", "The first day"), ("the_last_date", "The last day"), ("date", "Date of month"),
            ("day", "Day of month")
        ],
        string="Option",
        default="date",
    )
    day = fields.Integer("Day of month", default=1)
    year_day = fields.Integer("Month Day", default=1)
    year_month = fields.Selection(_return_year_month, string="Month", default="1")
    week_list = fields.Selection(
        [
            ("0", "Monday"), ("1", "Tuesday"), ("2", "Wednesday"), ("3", "Thursday"), ("4", "Friday"),
            ("5", "Saturday"), ("6", "Sunday")
        ],
        string="Weekday",
    )
    byday = fields.Selection(
        [("1", "First"), ("2", "Second"), ("3", "Third"), ("4", "Fourth"), ("-1", "Last")],
        string="By day",
    )
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user, string="Responsible user")
    partner_id = fields.Many2one("res.partner", string="Partner")
    email_from = fields.Char(
        string="Email from",
        help="If not defined, the user who sends a reminder (usually the Odoo bot) will be the email author",
    )
    partner_model_field = fields.Char(
        string="Filter by partner",
        compute=_compute_model,
        store=True,
        readonly=False,
        help="Choose a model field that will be used to filter records by the selected reminder partner",
    )
    user_model_field = fields.Char(
        string="Filter by responsible",
        compute=_compute_model,
        store=True,
        readonly=False,
        help="Choose a model field that will be used to filter records by the selected responsible user",
    )

    _sql_constraints = [("interval_check", "check (interval>0)", _("Repeat interval should be positive!")),]

    def read(self, fields=None, load="_classic_read"):
        """
        Rewrite to add the extra check for model

        Methods:
         * check_reminder_model_access()
        """
        res = super(total_notify, self).read(fields=fields, load=load)
        for notify in self:
            check_access = notify.check_reminder_model_access()
            if not check_access:
                raise AccessError(_("Sorry, you are not allowed to access the model {}".format(notify.model)))
        return res

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """
        Rewrite to exlude not allowed reminders accoriding to the model

        # Methods:
        #  * check_reminder_model_access()

        Extra info:
         * self.browse(ids) - do not use sudo() here, hence check will be under the SuperUser
        """
        query = super()._search(domain, offset, limit, order, access_rights_uid)
        self.flush_model(["model"])
        allowed_ids = []
        self.env.cr.execute(query.select(
            SQL.identifier(self._table, "id"),
            SQL.identifier(self._table, "model"),
        ))
        all_models = self._cr.fetchall()
        for _id, model in all_models:
            check_access = self.env["ir.model.access"].check(model, "read", raise_exception=False)
            if check_access:
                allowed_ids.append(_id)
        allowed = self.browse(allowed_ids)
        return allowed._as_query(order)

    def check_reminder_model_access(self):
        """
        Method to check whether a user has access to this reminder according to the model specified

        Returns:
         * Boolean

        Extra info:
         * sudo() in self.sudo().model is absolutely necessary, since it itself make "read()"
         * Expected singleton
        """
        res = True
        model = self.sudo().model
        if model:
            res = self.env["ir.model.access"].check(model, "read", raise_exception=False)
        return res

    @api.model
    def send_reminders(self):
        """
        Method to find reminders to send based on recurrence and send them

        Methods:
         * action_make_notification

        Extra info:
         * the method name is not adapted to include "action_" since cron is in not updatable data. So, to suit
           the previous versions the name is kept as it is
        """
        today = fields.Date.today()
        reminders = self.search(["|", ("next_sent_date", "<=", today), ("next_sent_date", "=", False)])
        _logger.info("Notifications job for reminders {} are started to be prepared".format(reminders))
        for reminder in reminders:
            # We are in loop to make commit after each reminder is sent
            reminder.action_make_notification()
            self.env.cr.commit()

    def action_make_notification(self):
        """
        Method to find the objects and send a correct reminder

        Methods:
         * _prepare_values
         * _prepare_and_send_email

        Extra info:
         * We are under sudo() to find all documents disregarding current user accesses
        """
        self = self.sudo()
        for notify in self:
            lang = notify.lang or self.env.user.lang
            columns, instances, group_operators = notify.with_context(lang=lang)._prepare_values()
            if instances:
                notify.with_context(lang=lang)._prepare_and_send_email({
                    "extra_message": self.extra_message and self.extra_message != "<p><br></p>" \
                        and self.extra_message or False,
                    "include_table_in_message": self.include_table_in_message,
                    "list_name": self.name,
                    "url_included": self.url_included,
                    "title": self.period_title,
                    "columns": columns,
                    "instances": instances,
                    "group_operators": group_operators,
                })
            else:
                _logger.info(u"For the reminder {} ({}) no instances are found".format(notify.name, notify.id))

    def action_get_report_name(self):
        """
        The method to prepare a title for Excel and PPDf versions

        Extra info:
         * Expected singleton
        """
        return "{}#{}".format(self.name, self.period_title)

    def _prepare_and_send_email(self, values={}):
        """
        The method to render template and sent message

        Args:
         * values - dict of values

        Methods:
         * _prepare_xls_table
         * _prepare_pdf_table
         * _action_send_mail
         * _calc_the_next_sent_date

        Attrs update:
         * last_sent_date

        Extra info:
         * There should be proper lang in context
         * Expected singleton
        """
        body_html = self.env["ir.qweb"]._render(
            "total_notify.total_notify_template", values, minimal_qcontext=True, raise_if_not_found=False,
        )
        subject = "{}: {}".format(self.name, self.period_title)
        composer_values = {
            "author_id": self.env.user.partner_id.id,
            "body": body_html,
            "subject": subject,
            "email_from": self.email_from or self.env.user.partner_id.email_formatted,
            "record_name": False,
            "composition_mode": "mass_mail",
            "template_id": None,
            "model": "total.notify",
            "res_ids": [self.id],
            "partner_ids": [(6, 0, self.message_partner_ids.ids)],
        }
        attachments = []
        if self.send_by_xls:
            attachment_id = self._prepare_xls_table(
                columns=values.get("columns"),
                instances=values.get("instances"),
                group_operators=values.get("group_operators"), 
            )
            attachments.append((4, attachment_id.id))
        if self.send_pdf:
            attachment_id = self._prepare_pdf_table(values)
            attachments.append((4, attachment_id.id))
        if attachments:
            composer_values.update({"attachment_ids": attachments})
        composer = self.env["mail.compose.message"].create(composer_values)
        composer.with_context(total_notify=True, active_ids=self.ids)._action_send_mail(auto_commit=True)
        self.last_sent_date = fields.Date.today()
        self.next_sent_date = self._calc_the_next_sent_date()

    def _prepare_xls_table(self, columns, instances, group_operators):
        """
        The method to generate an XLS attachment if necessary

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like "A" or "S" (ascii char depends on counter)
          2.2 Calculate column widt based on value inside. The min is 20
        3. Prepare each row of instances
        4. Prepare total line
        5. Create an attachment

        Args:
         * columns - list of column names
         * instances - list of lists of each row values
         * group_operators - list

        Methods:
         * _get_default_xlsx_styles
         * action_get_report_name

        Returns:
         * ir.attachment object

        Extra info:
         * There should be proper lang in context
         * Expected singleton
        """
        # 1
        file_path = tempfile.mktemp(suffix=".xlsx")
        workbook = xlsxwriter.Workbook(file_path)
        styles = self._get_default_xlsx_styles(workbook)
        worksheet = workbook.add_worksheet(self.name)
        # 2
        cur_column = 0
        for column in columns:
            column = cur_column == 0 and "#" or column
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            # 2.2
            column_width = len(column) + 2 > 20 and len(column) + 2 or 20
            worksheet.set_column("{c}:{c}".format(c=col_letter), column_width)
            cur_column += 1
        # 3
        for row, instance in enumerate(instances):
            cell_style = styles.get("main_data_style")
            for counter, column in enumerate(instance):
                value = column
                if value  == "group_header":
                    worksheet.merge_range(row+1, 0, row+1, len(columns)-1, instance[1], styles.get("group_data_style"))
                    break
                else:
                    if value == "total_line":
                        value, cell_style = "", styles.get("group_total_style")
                    worksheet.write(row+1, counter, value, cell_style)
        # 4
        if group_operators:
            for counter, group_operator in enumerate(group_operators):
                value = group_operator
                if value == "total_line":
                    value = ""
                worksheet.write(row+2, counter, value, styles.get("main_header_style"))
        workbook.close()
        # 5
        with open(file_path, "rb") as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            "name":  u"{}.xlsx".format(self.action_get_report_name()),
            "type": "binary",
            "datas": xls_file,
            "res_model": "total.notify",
            "res_id": self.id,
        }
        attachment_id = self.env["ir.attachment"].create(att_vals)
        return attachment_id

    def _prepare_pdf_table(self, report_values):
        """
        The method to generate PDF attachment

        Args:
         * report_values - dict of values to render report

        Methods:
         * action_get_report_name

        Returns:
         * ir.attachment object

        Extra info:
         * Expected singleton
        """
        result, format = self.env["ir.actions.report"]._render_qweb_pdf(
            "total_notify.action_report_total_notify", [self.id], report_values
        )
        result = base64.b64encode(result)
        att_vals = {
            "name":  u"{}.pdf".format(self.action_get_report_name()),
            "type": "binary",
            "datas": result,
            "res_model": "total.notify",
            "res_id": self.id,
        }
        attachment_id = self.env["ir.attachment"].create(att_vals)
        return attachment_id

    def _prepare_values(self):
        """
        The method to prepare values for rendering in email temlates, pdf, and xls

        Methods:
         * _return_lang_date_format
         * _return_records_filtered
         * _return_total_line
         * _return_field_value
         * _prepare_record_url

        Returns:
         * column_names - list
         * columns - list of lists.
         * group_operators - list

        Extra info:
         * We do not use in return list of dicts, since a single column name might be introduced a few times
         * Expected singleton
        """
        self = self.with_context(lang=self.lang) # Since we are under admin, we use lang of total.notify object
        column_names, columns, group_operators = [" "] + [column.field_label for column in self.column_ids], [], []
        records = self._return_records_filtered()
        lang_date_format, lang_datetime_format = self._return_lang_date_format()
        current_records, field_group = self.env[self.model], None
        for row_number, record in enumerate(records):
            if self.group_field_id:
                this_field_group = record[self.group_field_id.name] or False
                if this_field_group != field_group:
                    if field_group:
                        group_lines = self._return_total_line(current_records)
                        if group_lines:
                            columns.append(group_lines)
                    group_header = ["group_header", self._return_field_value(
                        record, self.group_field_id, False, lang_date_format, lang_datetime_format
                    )]
                    columns.append(group_header)
                    field_group = this_field_group
                    current_records = record
                else:
                    current_records += record
            record_url = self.url_included and self._prepare_record_url(record=record) or row_number + 1
            values = [record_url]
            for column in self.column_ids:
                cfield_id = column.field_id
                crelated_field_id = column.related_field
                values.append(self._return_field_value(
                    record, cfield_id, crelated_field_id, lang_date_format, lang_datetime_format
                ))
            columns.append(values)
        else:
            if self.group_field_id:
                group_lines = self._return_total_line(current_records)
                if group_lines:
                    columns.append(group_lines)
        group_operators = self._return_total_line(records)
        return column_names, columns, group_operators

    def _return_records_filtered(self):
        """
        The method to find instances by filters and restrictions indicated in the record
        Here we also sort records by the group operator (if any) and the defined sorting criteria

        Returns:
         * recordset of defined model

        Extra info:
         * Expected singleton
        """
        partner_user_domain, order_param = [], ""
        group_field, sort_field = self.group_field_id, self.sort_field_id
        if self.partner_id and self.partner_model_field:
            partner_user_domain.append((self.partner_model_field, "=", self.partner_id.id))
        if self.user_id and self.user_model_field:
            partner_user_domain.append((self.user_model_field, "=", self.user_id.id))
        domain = safe_eval(self.period_domain) + safe_eval(self.domain) + partner_user_domain
        if group_field and group_field.model == self.model and group_field.store == True:
            order_param = "{}".format(group_field.name)
        if sort_field and sort_field.model == self.model and sort_field.store == True:
            order_param = "{}{} {}".format(
                order_param and "{},".format(order_param) or "", sort_field.name, self.sort_field_direction or "asc",
            )
        if order_param:
            res = self.env[self.model].search(domain, order=order_param)
        else:
            res = self.env[self.model].search(domain)
        return res

    def _return_field_value(self, crecord, cfield, crelated_field, lang_date_format, lang_datetime_format):
        """
        The method to get the value for a field
         1. For selection options we need the value, not the key
         2. For date and datetime we should parse to string according to lang format
         3. For not relational field we just retrieve the value from field
         4. For relational fields without complementary fields we use the object name
         5. For relational fields with complementary field of selection type we should also retrieve value
         6. For relational fields with complementary field of m2o type we get name of complementary field
         7. For relational fields with complementary field of not m2o type we get complementary value
         8. O2m & M2m fields are not possible here, but for sudden cases we check it

        Args:
         * crecord - Odoo object
         * cfield - ir.model.fields object
         * crelated_field - ir.model.feilds.object
         * lang_date_format - str
         * lang_datetime_format - str

        Methods:
         * _prepare_string_on_x2m_values
         * _parse_selection_value

        Returns:
         * str/integer/number

        Extra info:
         * Expected singleton
        """
        column_value = False
        field_name = cfield.name
        field_value = crecord[field_name]
        field_type = cfield.ttype
        if field_type == "selection":
            # 1
            try:
                column_value = dict((crecord._fields[field_name]._description_selection(self.env)))[field_value]
            except:
                column_value = field_value
        elif field_type == "date":
            # 2
            column_value = field_value and field_value.strftime(lang_date_format) or False
        elif field_type == "datetime":
            # 2
            column_value = field_value and field_value.strftime(lang_datetime_format) or False
        elif field_type not in ["many2one", "one2many", "many2many"]:
            # 3
            column_value = field_value
        else:
            if not crelated_field:
                # 4
                column_value = field_type == "many2one" and field_value.name \
                    or self._prepare_string_on_x2m_values(field=field_value)
            else:
                related_name = crelated_field.name
                related_ttype = crelated_field.ttype
                if related_ttype == "selection":
                    # 5
                    column_value = field_type == "many2one" \
                        and self._parse_selection_value(field=field_value, field_name=related_name)\
                        or self._prepare_string_on_x2m_values(
                            field=field_value, relational_field=related_name, selection_field=True,
                        )
                elif related_ttype == "many2one":
                    # 6
                    column_value = field_type == "many2one" \
                        and field_value[related_name].name \
                        or self._prepare_string_on_x2m_values(
                            field=field_value, relational_field=related_name, relational_m2o=True,
                        )
                elif related_ttype not in ["many2many", "one2many"]:
                    # 7
                    column_value = field_type == "many2one" and field_value[related_name] \
                        or self._prepare_string_on_x2m_values(field=field_value, relational_field=related_name)
                else:
                    # 8
                    raise UserError(_(u"Many2many and One2many fields are not supported as complementaries"))
        if not column_value:
            if not (type(column_value) == int or type(column_value) == float):
                column_value = "-----"
        elif column_value == "False":
            column_value = "-----"
        return column_value

    def _return_total_line(self, gr_records):
        """
        The method to get total line for the particular records

        Args:
         * gr_records - recordset

        Returns:
         * list

        Extra info:
         * Expected singleton
        """
        groupped_line = ["total_line"]
        group_line_needed = False
        for column in self.column_ids:
            new_value = " "
            if column.group_operator:
                records_sum = 0
                column_name = column.field_id.name
                related_field_name = column.related_field and column.related_field.name or False
                for record in gr_records:
                    if related_field_name:
                        records_sum += record[column_name][related_field_name] or 0
                    else:
                        records_sum += record[column_name] or 0
                if column.group_operator == "sum":
                    new_value = round(records_sum, 2)
                elif column.group_operator == "average":
                    gr_records_len = len(gr_records)
                    if gr_records_len > 0:
                        new_value = round(records_sum / gr_records_len, 2)
                    else:
                        new_value = 0
            groupped_line.append(new_value)
            if new_value != " ":
                group_line_needed = True
        return group_line_needed and groupped_line or False

    def _return_lang_date_format(self):
        """
        The method to get datetime format based on lang

        Returns:
         * tuple: str, srt

        Extra info:
         * Expected singleton
        """
        lang_date_format, lang_datetime_format = "%m/%d/%Y", "%m/%d/%Y %H:%M:%S"
        record_lang = self.env["res.lang"].search([("code", "=", self.lang)], limit=1)
        if record_lang:
            lang_date_format = record_lang.date_format
            lang_datetime_format = "{} {}".format(lang_date_format, record_lang.time_format)
        return lang_date_format, lang_datetime_format

    @api.model
    def _parse_selection_value(self, field, field_name):
        """
        The method to parse seleciton value for given field and key

        Args:
         * field - ir.models.fields object
         * field_name - char

        Methods:
        * _description_selection of ir.model.fields

        Returns:
         * char
        """
        try:
            selection_value = dict((field._fields[field_name]._description_selection(self.env)))[field[field_name]]
        except:
            selection_value = field[field_name]
        return selection_value

    @api.model
    def _prepare_string_on_x2m_values(self, field, relational_field=False, relational_m2o=False, selection_field=False):
        """
        Method to make string from x2m fields

        Args:
         * field - xm2 ir.model.fields object
         * relational_field - name of related field if exist, False otherwise
         * relational_m2o - in case relation is of m2o type
         * selection_field - in case relation is of selection type

        Methods:
         * _parse_selection_value

        Returns:
         * char
        """
        res = ""
        if not relational_field:
            res = ", ".join([instance.display_name for instance in field])
        else:
            if selection_field:
                res = ", ".join(
                    [str(self._parse_selection_value(field=instance, field_name=relational_field)) for instance
                    in field]
                )
            elif relational_m2o:
                res = ", ".join(
                  [str(instance[relational_field] and instance[relational_field].display_name or False) for instance
                   in field]
                )
            else:
                res = ", ".join([str(instance[relational_field]) for instance in field])
        return res

    @api.model
    def _prepare_record_url(self, record):
        """
        The method to retrieve record backend url

        Args:
         * record - instance of some Odoo model

        Returns:
         * Char
        """
        ICPSudo = self.env["ir.config_parameter"].sudo()
        base_url = ICPSudo.get_param("web.base.url", default="http://localhost:8069")
        dbname = self.env.cr.dbname
        url = "{}/web?db={}#id={}&view_type=form&model={}".format(base_url, dbname, record.id, record._name)
        return url

    def _return_translation_for_field_label(self, field):
        """
        The method to return translation for field label

        Args:
         * ir.model.fields object

        Returns:
         * char

        Extra info:
         * Expected singleton or empty recordset
        """
        lang = self.lang or self.env.user.lang
        return  field.with_context(lang=lang).field_description

    @api.model
    def _get_default_xlsx_styles(self, workbook):
        """
        Return dict with default workbook.style for xlsx printouts
        """
        styles = {
            "main_header_style": workbook.add_format({"bold": True, "font_size": 13, "border": 1}),
            "main_data_style": workbook.add_format({"font_size": 11, "border": 1}),
            "group_data_style": workbook.add_format({
                "bold": True, "align": "center", "bg_color": "#ededed", "font_size": 12, "border": 1,
            }),
            "group_total_style": workbook.add_format({"italic": True, "font_size": 11, "border": 1}),
        }
        return styles

    def _calc_the_next_sent_date(self):
        """
        Method to find the next date by the setting
         1. We are from today not from the last_sent_date no to make excess repeats
         2. Althoug the period is weekly, it might be this week by days. If the days are not define, it just a week dif
         3. In case a day is not found (e.g. 30th in February, we get the last month day)

        Returns:
         * date.date()

        Extra info:
         * Expected singleton
        """
        periodicity = self.periodicity
        interval = self.interval
        # 1
        today = fields.Date.from_string(fields.Date.today())
        res_date = False
        if periodicity == "daily":
            res_date = today + relativedelta(days=interval)
        elif periodicity == "weekly":
            current_week_day = today.weekday()
            wd_ids = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            time_delta = 7 * interval
            # 2
            for wd in wd_ids[current_week_day+1:7]:
                # Firstly search in this week days
                if self[wd]:
                    time_delta = wd_ids.index(wd) - current_week_day
                    break
            if time_delta == 7 * interval:
                # Then search in the next week
                for wd in wd_ids[0:current_week_day]:
                    if self[wd]:
                        time_delta = (7 * interval) + (wd_ids.index(wd) - current_week_day)
                        break
            # if no other days, just go to the next interval
            res_date = today + relativedelta(days=time_delta)
        elif periodicity == "monthly":
            month_by = self.month_by
            next_month_day = today + relativedelta(months=interval)
            first_month_date = date(year=next_month_day.year, month=next_month_day.month, day=1)
            last_month_date = date(
                year=next_month_day.year,
                month=next_month_day.month,
                day=monthrange(next_month_day.year, next_month_day.month)[1],
            )
            if month_by in ["the_first_date"]:
                res_date = first_month_date
            elif month_by in ["the_last_date"]:
                res_date = last_month_date
            elif month_by in ["day"]:
                byday = int(self.byday)
                week_list = int(self.week_list)
                new_day = _calc_month_day_byday_and_weekday(
                    next_month_day=next_month_day, byday=byday, week_list=week_list,
                )
                res_date = date(year=next_month_day.year, month=next_month_day.month, day=new_day,)
            elif month_by in ["date"]:
                # 3
                try:
                    res_date = date(year=next_month_day.year, month=next_month_day.month, day=self.day)
                except:
                    next_month_day = last_month_date
        elif periodicity == "yearly":
            the_next_year_day = today + relativedelta(years=interval)
            try:
                res_date = date(year=the_next_year_day.year, month=int(self.year_month), day=self.year_day)
            except:
                res_date = date(
                    year=the_next_year_day.year,
                    month=int(self.year_month),
                    day=monthrange(the_next_year_day.year, int(self.year_month))[1],
                )
        return res_date
