# -*- coding: utf-8 -*-

import base64
import logging
import os
import time
import traceback

from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException, WebDriverException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    _silenium_lib_imported = True
except ImportError:
    _silenium_lib_imported = False
    _logger.info(
        "The `selenium` Python module is not available. "
        "WhatsApp Automation will not work. "
        "Try `pip3 install selenium` to install it."
    )

try:
    import phonenumbers
    from phonenumbers.phonenumberutil import region_code_for_country_code
    _whatsapp_phonenumbers_lib_imported = True

except ImportError:
    _whatsapp_phonenumbers_lib_imported = False
    _logger.info(
        "The `phonenumbers` Python module is not available. "
        "Phone number validation will be skipped. "
        "Try `pip3 install phonenumbers` to install it."
    )
driver = {}
profile = {}
wait={}
wait5={}
wait100={}
is_session_open = {}
options = {}
msg_sent = False


dir_path = os.path.dirname(os.path.realpath(__file__))


class SendWAMessage(models.TransientModel):
    _name = 'whatsapp.msg'
    _description = 'Send WhatsApp Message'

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)

    name = fields.Char()
    partner_ids = fields.Many2many(
        'res.partner', 'whatsapp_msg_res_partner_rel',
        'wizard_id', 'partner_id', 'Recipients')
    message = fields.Text('Message', compute='_compute_message',
        readonly=False, store=True, required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_msg_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)
    sending_mode = fields.Selection([('numbers', 'Numbers'), ('group', 'Group')], string='Sending Mode', default='numbers', help='Select mode for norma chat of WhatsApp Group')
    group_name = fields.Char(string='Group Name', help='Give extact name you want to send the message to WhatsApp group')

    res_model = fields.Char('Document Model Name')
    res_id = fields.Integer('Document ID')
    res_ids = fields.Char('Document IDs')
    template_id = fields.Many2one('whatsapp.template', string='Use Template', domain="[('model', '=', res_model)]")

    @api.model_create_multi
    def create(self, vals_list):
        pos_wp_login = self.env.context.get('pos_wp_login')
        for vals in vals_list:
            if not pos_wp_login:
                vals['name'] = self.env['ir.sequence'].next_by_code('whatsapp.msg.sequence') or _('New')
        context = self.env.context.copy()
        if context.get('active_model') == 'pos.order' and context.get('active_id'):
            try:
                active_id = context.pop('active_id')
                context.update({'res_id': active_id})
            except:
                pass
            self = self.with_context(context)
        res = super(SendWAMessage, self).create(vals_list)
        return res

    @api.depends('res_model', 'res_id', 'template_id')
    def _compute_message(self):
        for record in self:
            if record.template_id and record.res_id:
                record.message = record.template_id._render_field('body', [record.res_id], compute_lang=True)[record.res_id]
            elif record.template_id:
                record.message = record.template_id.body

    def format_amount(self, amount, currency):
        fmt = "%.{0}f".format(currency.decimal_places)
        lang = self.env['res.lang']._lang_get(self.env.context.get('lang') or 'en_US')

        formatted_amount = lang.format(fmt, currency.round(amount), grouping=True, monetary=True)\
            .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

        pre = post = u''
        if currency.position == 'before':
            pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=currency.symbol or '')
        else:
            post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=currency.symbol or '')

        return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)

    def _phone_get_country(self, partner):
        if 'country_id' in partner:
            return partner.country_id
        return self.env.user.company_id.country_id

    def _msg_sanitization(self, partner, field_name):
        number = partner[field_name]
        if number and _whatsapp_phonenumbers_lib_imported:
            country = self._phone_get_country(partner)
            country_code = country.code if country else None
            try:
                phone_nbr = phonenumbers.parse(number, region=country_code, keep_raw_input=True)
            except phonenumbers.phonenumberutil.NumberParseException:
                return number
            if not phonenumbers.is_possible_number(phone_nbr) or not phonenumbers.is_valid_number(phone_nbr):
                return number
            phone_fmt = phonenumbers.PhoneNumberFormat.E164
            return phonenumbers.format_number(phone_nbr, phone_fmt)
        else:
            return number

    def _get_records(self, model):
        if self.env.context.get('active_domain'):
            records = model.search(self.env.context.get('active_domain'))
        elif self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        Attachment = self.env['ir.attachment']
        receipt_data = self.env.context.get('receipt_data')
        if not active_model:
            return result
        res_id = self.env.context.get('active_id') or self.env.context.get('res_id')
        result['res_model'] = result.get('res_model') or self.env.context.get('active_model')
        if not result.get('res_ids'):
            if not result.get('res_id') and self.env.context.get('active_ids') and len(self.env.context.get('active_ids')) > 1:
                result['res_ids'] = repr(self.env.context.get('active_ids'))
        if not result.get('res_id'):
            if not result.get('res_ids') and self.env.context.get('active_id'):
                result['res_id'] = self.env.context.get('active_id')
        if active_model == 'pos.order':
            rec = self.env[active_model].search([('pos_reference', '=', res_id)], order='id desc', limit=1)
            if not rec:
                return result
            res_id = rec.id
            res_name = rec.pos_reference and rec.pos_reference.replace('/', '_').replace(' ', '_')
            if receipt_data:
                try:
                    specific_paperformat_args = {
                        'data-report-margin-top': 10,
                        'data-report-margin-left': 40,
                    }
                    data1 = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
                    receipt_data = data1 + receipt_data
                    pos_receipt_paperformat_id = self.env.ref('whatsapp_pos_integration.is_pos_receipt_paperformat')
                    pdf = self.env['ir.actions.report'].with_context(pos_receipt_paperformat_id=pos_receipt_paperformat_id)._run_wkhtmltopdf(
                        [receipt_data],
                        landscape=True,
                        specific_paperformat_args=specific_paperformat_args
                    )
                    res = base64.b64encode(pdf)
                    filename = res_name + '.pdf'
                    attachment_data = {
                        'name': filename,
                        'datas': res,
                        'type': 'binary',
                        'store_fname': filename,
                        'res_model': active_model,
                        'res_id': res_id,
                        'mimetype': 'application/pdf'
                    }
                    attachment_id = Attachment.create(attachment_data).id
                    result['attachment_ids'] = [(6, 0, [attachment_id])]
                except Exception:
                    traceback.print_exc()

                return result
        else:
            rec = self.env[active_model].browse(res_id)
            res_name = 'Invoice_' + rec.name.replace('/', '_') if active_model == 'account.move' else rec.name.replace('/', '_')
        msg = result.get('message', '')
        result['message'] = msg

        if not self.env.context.get('default_recipients') and active_model and hasattr(self.env[active_model], '_get_default_whatsapp_recipients'):
            model = self.env[active_model]
            if active_model == 'pos.order':
                records = self.with_context(active_id=res_id, active_ids=[res_id])._get_records(model)
            else:
                records = self._get_records(model)
            if active_model == 'res.partner' and records and self.env.context.get('from_multi_action'):
                records = records.filtered(lambda p: p.mobile and p.country_id)
            partners = records._get_default_whatsapp_recipients()
            phone_numbers = []
            no_phone_partners = []
            if active_model not in ['res.partner', 'hr.employee']:
                is_attachment_exists = Attachment.search([('res_id', '=', res_id), ('name', 'like', res_name + '%'), ('res_model', '=', active_model)], limit=1)
                if not is_attachment_exists:
                    attachments = []
                    if active_model == 'sale.order':
                        template = self.env.ref('sale.email_template_edi_sale')
                    elif active_model == 'account.move':
                        template = self.env.ref('account.email_template_edi_invoice')
                    elif active_model == 'purchase.order':
                        if self.env.context.get('send_rfq', False):
                            template = self.env.ref('purchase.email_template_edi_purchase')
                        else:
                            template = self.env.ref('purchase.email_template_edi_purchase_done')
                    elif active_model == 'stock.picking':
                        template = self.env.ref('stock.mail_template_data_delivery_confirmation')
                    elif active_model == 'account.payment':
                        template = self.env.ref('account.mail_template_data_payment_receipt')
                    elif active_model == 'pos.order':
                        if rec.mapped('account_move'):
                            report = self.env.ref('point_of_sale.pos_invoice_report')
                            report_service = res_name + '.pdf'
                        else:
                            return result

                    if active_model != 'pos.order':
                        report = template.report_template
                        report_service = report.report_name

                    if report.report_type not in ['qweb-html', 'qweb-pdf']:
                        raise UserError(_('Unsupported report type %s found.') % report.report_type)
                    res, format = report._render_qweb_pdf(report_service, [res_id])
                    res = base64.b64encode(res)
                    if not res_name:
                        res_name = 'report.' + report_service
                    ext = "." + format
                    if not res_name.endswith(ext):
                        res_name += ext
                    attachments.append((res_name, res))
                    attachment_ids = []
                    for attachment in attachments:
                        attachment_data = {
                            'name': attachment[0],
                            'datas': attachment[1],
                            'type': 'binary',
                            'res_model': active_model,
                            'res_id': res_id,
                        }
                        attachment_ids.append(Attachment.create(attachment_data).id)
                    if attachment_ids:
                        result['attachment_ids'] = [(6, 0, attachment_ids)]
                else:
                    result['attachment_ids'] = [(6, 0, [is_attachment_exists.id])]

            for partner in partners:
                number = self._msg_sanitization(partner, self.env.context.get('field_name') or 'mobile')
                if number:
                    phone_numbers.append(number)
                else:
                    no_phone_partners.append(partner.name)
            if len(partners) > 1:
                if no_phone_partners:
                    raise UserError(_('Missing mobile number for %s.') % ', '.join(no_phone_partners))
            if partners:
                result['partner_ids'] = [(6, 0, partners.ids)]
        return result

    def send_whatsapp_msgs(self, number, msg, get_qr=False, group_name=False):
        global driver
        global wait
        global wait5
        global msg_sent
        if not driver.get(self.unique_user):
            return {'result': False, 'msg_sent': False}
        if not self.is_wp_loaded():
            try:
                elements = driver.get(self.unique_user).find_elements(by=By.CLASS_NAME, value='_20c87')
                if not elements:
                    try:
                        landing_wrapper_xpath = "//div[contains(@class, 'landing-wrapper')]"
                        landing_wrapper = wait5.get(self.unique_user).until(EC.presence_of_element_located((
                            By.XPATH, landing_wrapper_xpath)))
                        try:
                            spin_class = driver.get(self.unique_user).find_elements(by=By.CLASS_NAME, value='b9fczbqn')
                            if spin_class:
                                return {"isLoggedIn": False}
                        except:
                            pass

                        try:
                            elements = driver.get(self.unique_user).find_elements(by=By.CLASS_NAME, value='_2znac')
                            for e in elements:
                                e.click()
                        except:
                            pass
                        qr_code_xpath = "//canvas[contains(@aria-label, 'Scan me!')]"
                        qr_code = wait5.get(self.unique_user).until(EC.presence_of_element_located((
                            By.XPATH, qr_code_xpath)))
                        base64_image = driver.get(self.unique_user).execute_script("return document.querySelector('canvas').toDataURL('image/png');")
                        return {"isLoggedIn": False, 'qr_image': base64_image}
                    except NoSuchElementException as e:
                        traceback.print_exc()
                    except Exception as ex:
                        traceback.print_exc()
            except (NoSuchElementException, Exception):
                traceback.print_exc()
                if get_qr:
                    return False
        try:
            elements  = driver.get(self.unique_user).find_elements(by=By.CLASS_NAME, value='_2Zdgs')
            for e in elements:
                e.click()
                time.sleep(7)
        except Exception as e:
            traceback.print_exc()
        count = 1
        while True:
            time.sleep(1)
            count += 1
            if self.is_wp_loaded():
                break
            if count >= 120:
                return {'result': False, 'msg_sent': False}

        if group_name:
            try:
                time.sleep(1)
                inp_elements = driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="p.selectable-text.copyable-text")
                inp_element = inp_elements and inp_elements[0]
                if inp_element:
                    inp_element.clear()
                    inp_element.send_keys(group_name)
                    time.sleep(2)
                try:
                    selected_contact = driver.get(self.unique_user).find_elements(by=By.XPATH, value="//span[@title='"+group_name+"']")
                    selected_contact = selected_contact and selected_contact[0]
                    selected_contact.click()
                except (NoSuchElementException, Exception) as e:
                    return {'group_not_available': True}
                enter_elements = driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="p.selectable-text.copyable-text")
                enter_element = enter_elements and enter_elements[1]
                if enter_element:
                    msg = msg.replace('PARTNER', 'Group Members')
                    if "\n" in msg:
                        for ch in msg:
                            if ch == "\n":
                                ActionChains(driver.get(self.unique_user)).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
                            else:
                                enter_element.send_keys(ch)
                        enter_element.send_keys(Keys.ENTER)
                    else:
                        enter_element.send_keys(msg + Keys.ENTER)
                    time.sleep(1)

                for attachment in self.attachment_ids:
                    try:
                        time.sleep(1)
                        try:
                            time.sleep(1)
                            driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='clip']").click()
                        except:
                            driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='attach-menu-plus']").click()
                        time.sleep(1)
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            tmp.write(base64.decodebytes(attachment.datas))
                        if attachment.mimetype and 'image' in attachment.mimetype or 'video' in attachment.mimetype:
                            driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="input[type='file']")[1].send_keys(tmp.name)
                        else:
                            driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="input[type='file']").send_keys(tmp.name)

                        wait_upload_xpath = "//span[@data-icon='x-alt']"
                        wait_upload = wait.get(self.unique_user).until(EC.presence_of_element_located((
                            By.XPATH, wait_upload_xpath)))
                        time.sleep(1)
                        driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='send']").click()
                    except:
                        pass
                return {'result': True, 'msg_sent': True}
            except Exception as ex:
                msg_sent = False
                return {'result': False, 'msg_sent': False}
        if not msg or not number:
            return False
        try:
            sender_el = driver.get(self.unique_user).find_element(by=By.ID, value='sender')
            if not sender_el:
                try:
                    script = 'var newEl = document.createElement("div");newEl.innerHTML = "<a href=\'#\' id=\'sender\' class=\'executor\'> </a>";var ref = document.querySelector("div#pane-side");ref.parentNode.insertBefore(newEl, ref.previousSibling);'
                    driver.get(self.unique_user).execute_script(script)
                except Exception as sc:
                    pass
        except NoSuchElementException as e:
            msg_sent = False
            try:
                script = 'var newEl = document.createElement("div");newEl.innerHTML = "<a href=\'#\' id=\'sender\' class=\'executor\'> </a>";var ref = document.querySelector("div#pane-side");ref.parentNode.insertBefore(newEl, ref.previousSibling);'
                driver.get(self.unique_user).execute_script(script)
            except Exception as sc:
                pass
        try:
            time.sleep(2)
            try:
                number = ''.join([n for n in number if n.isdigit()])
            except:
                pass
            driver.get(self.unique_user).execute_script("var idx = document.getElementsByClassName('executor').length -1; document.getElementsByClassName('executor')[idx].setAttribute(arguments[0], arguments[1]);", "href", "https://api.whatsapp.com/send?phone=" + number + "&text=" + msg.replace('\n', '%0A'))
            time.sleep(1)
            driver.get(self.unique_user).find_element(by=By.ID, value='sender').click()
            time.sleep(1)
            try:
                inp_element = driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="span[data-icon='send']")
                if inp_element:
                    inp_element.click()
                    time.sleep(2)
            except:
                pass
            try:
                enter_count = 0
                while True:
                    if enter_count == 15:
                        break
                    else:
                        time.sleep(1)
                        enter_count += 1
                    inp_elements = driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="p.selectable-text.copyable-text")
                    inp_element = inp_elements and inp_elements[1]
                    if inp_element:
                        inp_element.send_keys(Keys.ENTER)
                        time.sleep(2)
                        break
            except:
                pass

            for attachment in self.attachment_ids:
                try:
                    time.sleep(1)
                    try:
                        time.sleep(1)
                        driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='clip']").click()
                    except:
                        driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='attach-menu-plus']").click()
                    time.sleep(1)
                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                        tmp.write(base64.decodebytes(attachment.datas))
                    if attachment.mimetype and 'image' in attachment.mimetype or 'video' in attachment.mimetype:
                        driver.get(self.unique_user).find_elements(by=By.CSS_SELECTOR, value="input[type='file']")[1].send_keys(tmp.name)
                    else:
                        driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="input[type='file']").send_keys(tmp.name)

                    wait_upload_xpath = "//span[@data-icon='x-alt']"
                    wait_upload = wait.get(self.unique_user).until(EC.presence_of_element_located((
                        By.XPATH, wait_upload_xpath)))
                    time.sleep(1)
                    driver.get(self.unique_user).find_element(by=By.CSS_SELECTOR, value="span[data-icon='send']").click()
                except Exception as exx:
                    pass
            msg_sent = True
            source_web = driver.get(self.unique_user).page_source
            if 'Phone number shared via url is invalid' in source_web:
                return {'result': False, 'msg_sent': False, 'invalid_phone': True}
            return {'result': True, 'msg_sent': True}
        except Exception as e:
            _logger.info("WhatsApp message proccessing error: %s" % e)
            traceback.print_exc()
            msg_sent = False
            return {'result': False, 'msg_sent': False}

    def get_qr_img(self):
        data = self.send_whatsapp_msgs(number=False, msg=False, get_qr=True)
        if self.is_wp_loaded():
            return False
        if data and not data.get('isLoggedIn'):
            if data.get('qr_image'):
                img = data.get('qr_image')
                del data
                return img
        return False

    def get_status(self):
        global is_session_open
        global driver
        try:
            driver.get(self.unique_user).title
            return True
        except WebDriverException:
            is_session_open[self.unique_user] = False
            return False

    def is_wp_loaded(self):
        global is_session_open
        global driver
        status = False
        if driver.get(self.unique_user):
            status = driver.get(self.unique_user).execute_script(
                "if (document.querySelector('*[data-icon=new-chat-outline]') !== null || document.querySelector('div[id=side]') !== null ) { return true } else { return false }"
            )
        return status

    def browser_session_open(self, unique_user):
        global is_session_open
        global options
        global dir_path
        profile_dir = dir_path + '/.user_data_uid_' + str(unique_user)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        options[unique_user] = Options()
        options[unique_user].add_argument('--user-data-dir=' + profile_dir)
        options[unique_user].add_argument('--headless')
        options[unique_user].add_argument('--no-sandbox')
        options[unique_user].add_argument('--window-size=1366,768')
        options[unique_user].add_argument('--start-maximized')
        # options[unique_user].add_argument('--disable-logging')
        # options[unique_user].add_argument('--enable-logging=stderr')
        options[unique_user].add_argument('--remote-debugging-port=9222')
        options[unique_user].add_argument('--remote-debugging-address=0.0.0.0')
        options[unique_user].add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.3312.0 Safari/537.36'
        options[unique_user].add_argument('user-agent='+user_agent)
        try:
            log_path = dir_path + '/chromedriver.log'
            service = Service(executable_path= dir_path + '/chromedriver_119', log_path=log_path)
            driver[unique_user] = webdriver.Chrome(service=service, options=options.get(unique_user))
        except Exception as bex:
            _logger.info("browser not starting exception: %s" % bex)
        wait[unique_user] = WebDriverWait(driver.get(self.unique_user), 22)
        wait5[unique_user] = WebDriverWait(driver.get(self.unique_user), 17)
        driver.get(unique_user).get("https://web.whatsapp.com")
        ixpath = "//div[contains(@id, 'pane-side')]"
        is_session_open[self.unique_user] = True
        try:
            wait.get(unique_user).until(EC.presence_of_element_located((
                    By.XPATH, ixpath)))
            script = 'var newEl = document.createElement("div");newEl.innerHTML = "<a href=\'#\' id=\'sender\' class=\'executor\'> </a>";var ref = document.querySelector("div#pane-side");ref.parentNode.insertBefore(newEl, ref.previousSibling);'
            driver.get(unique_user).execute_script(script)
        except Exception as e:
            pass

    def action_send_msg(self, answer=False, message=False):
        if not _silenium_lib_imported:
            raise UserError('Silenium is not installed. Please install it.')
        global is_session_open
        global msg_sent
        try:
            if not is_session_open.get(self.unique_user) or not self.get_status():
                    self.browser_session_open(self.unique_user)
        except Exception as e:
            _logger.warning('Error opening Browser %s' % str(e))

        if self.sending_mode == 'group':
            number = 0
            resp = {}
            try:
                wp_message = message or self.message
                wp_message = wp_message.replace('PARTNER', partner.name).replace('&', '%26').replace('+', '%2B')
                resp = self.send_whatsapp_msgs(number, wp_message, group_name=self.group_name and self.group_name.strip())
            except:
                _logger.warning('Failed to send Message to WhatsApp number ', number)
            if resp and resp.get('group_not_available'):
                raise UserError(_("No such group available in your WhatsApp chat list, please check the Group name twice. it's case sensitive"))
            if resp and not resp.get('isLoggedIn'):
                if resp.get('qr_image'):
                    img_data = resp.get('qr_image')
                    view_id = self.env.ref('whatsapp_integration.whatsapp_qr_view_form').id
                    context = dict(self._context, qr_image=img_data, wiz_id=self.id)
                    if self.env.context.get('from_pos'):
                        return {
                            'name': 'Scan WhatsApp QR Code',
                            'qr_img': img_data,
                        }
                    return {
                            'name':_("Scan WhatsApp QR Code"),
                            'view_mode': 'form',
                            'view_id': view_id,
                            'res_model': 'whatsapp.scan.qr',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'context': context,
                        }
            return

        active_model = self.env.context.get('active_model')
        partner_ids = []
        if active_model == 'hr.employee':
            partner_ids = self.employee_ids
        else:
            partner_ids = self.partner_ids

        for partner in partner_ids:
            number = ''
            if active_model == 'hr.employee':
                number = partner.mobile_phone
                if '+' not in number:
                    number = str(partner.country_id.phone_code) + partner.mobile_phone
            else:
                number = partner.mobile
                if '+' not in number:
                    number = str(partner.country_id.phone_code) + partner.mobile
            number = ''.join(no for no in number if no.isdigit())
            check = {}
            try:
                wp_message = message or self.message
                wp_message = wp_message.replace('PARTNER', partner.name).replace('&', '%26').replace('+', '%2B')
                check = self.send_whatsapp_msgs(number, wp_message)
            except:
                _logger.warning('Failed to send Message to WhatsApp number ', number)
            if check and not check.get('isLoggedIn'):
                if check.get('qr_image'):
                    img_data = check.get('qr_image')
                    view_id = self.env.ref('whatsapp_integration.whatsapp_qr_view_form').id
                    context = dict(self._context, qr_image=img_data, wiz_id=self.id)
                    if self.env.context.get('from_pos'):
                        return {
                            'name': 'Scan WhatsApp QR Code',
                            'qr_img': img_data,
                        }
                    return {
                            'name':_("Scan WhatsApp QR Code"),
                            'view_mode': 'form',
                            'view_id': view_id,
                            'res_model': 'whatsapp.scan.qr',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'context': context,
                        }
        if msg_sent:
            if not active_model:
                return True
            res_id = self.env.context.get('active_id')
            rec = self.env[active_model].browse(res_id)
            if active_model == 'sale.order':
                rec.message_post(body=Markup("%s %s sent via WhatsApp") % (_('Quotation') if rec.state in ('draft', 'sent', 'cancel') else _('Sales Order'), rec.name))
                if rec.state == 'draft':
                    rec.write({'state': 'sent'})
            elif active_model == 'account.move':
                rec.message_post(body=Markup("Invoice %s sent via WhatsApp") % (rec.name))
            elif active_model == 'purchase.order':
                rec.message_post(body=Markup("%s %s sent via WhatsApp") % (_('Request for Quotation') if rec.state in ['draft', 'sent'] else _('Purchase Order'), rec.name))
                if rec.state == 'draft':
                    rec.write({'state': 'sent'})
            elif active_model == 'stock.picking':
                rec.message_post(body=Markup("Delivery Order %s sent via WhatsApp") % (rec.name))
            elif active_model == 'account.payment':
                rec.message_post(body=Markup("Payment %s sent via WhatsApp") % (rec.name))
        else:
            view_id = self.env.ref('whatsapp_integration.whatsapp_retry_msg_view_form').id
            context = dict(self.env.context or {})
            context.update(wiz_id=self.id)
            return {
                    'name':_("Retry to send"),
                    'view_mode': 'form',
                    'view_id': view_id,
                    'res_model': 'whatsapp.retry.msg',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': context,
                }

        return True

    def _cron_kill_chromedriver(self):
        global driver
        for w in self.search([]):
            try:
                driver.get(w.unique_user).close()
                driver.get(w.unique_user).quit()
                driver[w.unique_user] = None
                is_session_open[w.unique_user] = None
            except Exception as e:
                pass


class ScanWAQRCode(models.TransientModel):
    _name = 'whatsapp.scan.qr'
    _description = 'Scan WhatsApp QR Code'

    name = fields.Char()

    def action_send_msg(self):
        res_id = self.env.context.get('wiz_id')
        if res_id:
            time.sleep(5)
            self.env['whatsapp.msg'].browse(res_id).action_send_msg()
        return True


class RetryWAMsg(models.TransientModel):
    _name = 'whatsapp.retry.msg'
    _description = 'Retry WhatsApp Message'

    name = fields.Char()

    def action_retry_send_msg(self):
        res_id = self.env.context.get('wiz_id')
        if res_id:
            time.sleep(5)
            self.env['whatsapp.msg'].browse(res_id).action_send_msg()
        return True
