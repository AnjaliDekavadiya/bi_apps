# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

import logging
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from ..ai_chat.openai_chatbot import AiChatBot
import base64
from odoo.tools import misc
MODELDOMAIN = [("model", "in", ("product.template",))]

_logger = logging.getLogger(__name__)


class AiBotConfig(models.Model):

    _name = 'ai.bot.config'
    _description = "Ai Bot Config"

    name = fields.Char("Name", required=True)
    welcome_msg = fields.Text(
        "Welcome Message", default="Hello! Welcome to Ai Based Chat Bot. Please let me know how can i help you?")
    state = fields.Selection([('draft', 'Draft'), ('content_generated', 'Content Generated'), ('trained', 'Trained'), (
        'cancelled', 'Cancelled')], string='Status', readonly=True, default='draft')
    model_id = fields.Many2one('ir.model', string='Model Name',
                               domain=MODELDOMAIN,
                               required=True, ondelete="set default",
                               default=lambda self: self.env['ir.model'].search(MODELDOMAIN, limit=1))
    line_ids = fields.One2many(
        "ai.bot.fields.line", 'config_id',
        string="Fields",
        help="Field lines that used in the content generation.",
        copy=False
    )
    common_line_ids = fields.One2many(
        "ai.common.fields.line", 'config_id',
        string="Common Fields",
        help="Common Field lines that used in the content generation.",
        copy=False
    )

    selected_ai_model = fields.Selection(
        selection="_get_model_list", default="gpt-3.5-turbo", string="OpenAi Model", required=True)
    max_tokens = fields.Integer(
        string="Maximum tokens", help="This value decides the maximum length of AI content response", default=200)
    temprature = fields.Integer(
        string="Temprature", help="This value decides the creativity and diversity of the text", default=0)

    generated_content_file = fields.Binary(string="Content", attachment=True, copy=False)
    file_name = fields.Char("File Name", default="Content")
    key_value_separator = fields.Char("Key Value Separator", default=":")
    row_separator = fields.Char("Row Separator", default="'\n'",  help="By default '\n' consider")
    two_key_separator = fields.Char("Keys Separator", default=",",  help="By default ',' consider")
    choose_records_type = fields.Selection([('all', 'All Records'), (
        'specific', 'Specific Records')], string="Choose Records Type", default="all", required=True)
    product_ids = fields.Many2many(
        'product.template', string="Specific Products", copy=False)

    _sql_constraints = [
        ('unique_name', 'unique (name)',
         'A Bot name should be uniqe.')
    ]
    
    
    def _openai_setup(self):
        client = AiChatBot(
            api_key = self._get_openai_api_key()
        )
        return client

    def _get_model_list(self):
        ai_models = self.env['ir.config_parameter'].sudo(
        ).get_param('odoo_openai_chatbot.ai_models')
        if ai_models:
            return eval(ai_models)
        else:
            return [('gpt-3.5-turbo', 'gpt-3.5-turbo')]

    def _get_connection_info(self):
        conf_params = self.env.cr._cnx.info.dsn_parameters
        return {
            'host': tools.config.options.get('db_host', False) or 'localhost',
            'dbname': conf_params.get('dbname'),
            'user': conf_params.get('user'),
            'port': conf_params.get('port', 5432),
            'password': tools.config.options.get('db_password', 'odoo')
        }

    def _get_openai_api_key(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_openai_chatbot.openai_api_key')
        return api_key or ''

    def get_collection_name(self):
        if self and self.model_id:
            return self.model_id.model+str(self.id) + (self.name or '')

    def _get_traning_file_path(self):
        temp_file_path = misc.file_path('odoo_openai_chatbot/ai_chat/temp_content.txt')
        if self.generated_content_file:
            with open(temp_file_path, 'wb') as f:
                f.write(base64.b64decode(self.generated_content_file))
        return temp_file_path

    def action_train_data(self):
        if self.generated_content_file:
            connection_info = self._get_connection_info()
            collection_name = self.get_collection_name()
            training_filepath = self._get_traning_file_path()
            api_key = self._get_openai_api_key()
            if api_key:
                self._openai_setup().train_model(training_filepath, connection_info,
                            collection_name)
                self.state = 'trained'
            else:
                raise UserError(_("Add Openai Api Key in the settings!!"))
        else:
            raise UserError(_("Upload Custom Data!!"))

    def _format_currency_amount(self, amount, currency_id):
        pre = post = u''
        if currency_id.position == 'before':
            pre = u'{symbol}\N{NO-BREAK SPACE}'.format(
                symbol=currency_id.symbol or '')
        else:
            post = u'\N{NO-BREAK SPACE}{symbol}'.format(
                symbol=currency_id.symbol or '')
        return u' {pre}{0}{post}'.format(amount, pre=pre, post=post)

    def _prepare_values(self, domain):
        results = []
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        field_dict = {
            line.field_id.name: line.field_id.ttype for line in self.line_ids}
        datas = self.env[self.model_id.model].search(domain)
        for data in datas:
            temp = {}
            for key, type in field_dict.items():
                if type in ["many2many"]:  # need to handle this with appropriate data
                    temp[key] = ','.join(data[key].mapped(data[key]._rec_name))
                elif type == 'many2one':
                    temp[key] = data[key].name
                elif key == 'website_url':
                    # temp[key] = f"<a href={base_url+data[key]}>{base_url+data[key]}</a>"
                    temp[key] = base_url+data[key]
                elif key == 'list_price':
                    temp[key] = self._format_currency_amount(
                        data[key], data.currency_id)
                elif key == 'attribute_line_ids':
                    temp[key] = self.env['ir.ui.view']._render_template(
                        "odoo_openai_chatbot.attribute_templates",
                        values={'attribute_line_ids': data[key]})
                else:
                    temp[key] = data[key]
            results.append(temp)
        return results

    def action_generate_content(self):
        if self.line_ids:
            try:
                common_data, common_key = {}, {}
                temp_file_path = misc.file_path('odoo_openai_chatbot/ai_chat/temp_content.txt')
                field_dict = {
                    line.field_id.name: line.name for line in self.line_ids}
                if self.choose_records_type == 'all':
                    domain = [('active', '=', True)]
                else:
                    domain = [('id', 'in', self.product_ids.ids)]
                # results = self.env[self.model_id.model].search_read(
                #     domain, fields=field_dict.keys())
                results = self._prepare_values(domain)
                for rec in self.common_line_ids:
                    common_data[rec.name] = rec.value
                    common_key[rec.name] = rec.name
                field_dict.update(common_key)
                [res.update(common_data)
                 for res in results if len(common_data)]
                with open(temp_file_path, 'wb') as f:
                    for res in results:
                        # res.pop('id')
                        data = ' '.join([f"{field_dict[key]}{self.key_value_separator}{res[key] or ''}{self.two_key_separator}" for key in res.keys(
                        )]) + self.row_separator or '\n'
                        f.write(data.encode())
                file = open(temp_file_path, "rb")
                self.write({
                    'state': 'content_generated',
                    'generated_content_file': base64.b64encode(file.read())
                })
            except Exception as e:
                _logger.info(
                    _("#### Exception while generating content ##### %s", str(e)))
        else:
            raise UserError(_("Add At least one field lines!!"))

    def reset_to_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancelled'
