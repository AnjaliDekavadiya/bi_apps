# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import logging
import base64
import xlwt
import tempfile
import binascii
import xlrd
from odoo import fields, SUPERUSER_ID, api
from odoo.http import request, route
from odoo import http, tools, _
from xlrd.timemachine import xrange
from io import BytesIO
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


def validate_mandatory_field(field, kw):
    error = None
    data = {}
    for key, value in field.items():
        if not kw.get(key):
            error = "Necessary field " + value + " is missing"
            break
        else:
            data[key] = kw.get(key)
    return error, data


def validate_optional_fields(opt_fields, kw):
    data = {}
    for fld in opt_fields:
        if kw.get(fld):
            data[fld] = kw.get(fld)
    return data


class TenderWebsite(http.Controller):
    @http.route('/get_state', type='json', auth="public")
    def get_state(self, country_id):
        state_ids = {}
        if country_id:
            states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
            for data in states:
                state_ids[data.id] = data.name
        return state_ids

    @http.route(['/vendor/signup'], type='http', auth="public", website=True)
    def vendor_signup(self, **kw):
        country = request.env['res.country'].search([])
        state = request.env['res.country.state'].search([])
        tender_category = request.env['tender.type'].search([])
        values = {
            'country': country,
            'state': state,
            'tender_category': tender_category,
            'already_login': True,
        }
        if request.env.user._is_public():
            values['already_login'] = False
        return request.render('tk_tender_management.vendor_signup', values)

    @http.route(['/vendor-sign-up'], type='http', auth="public", website=True)
    def vendor_register_process(self, **kw):
        emails = []
        country = request.env['res.country'].sudo().search([])
        state = request.env['res.country.state'].sudo().search([])
        tender_category = request.env['tender.type'].sudo().search([])
        values = {
            'country': country,
            'state': state,
            'tender_category': tender_category,
        }
        required_field = {'name': 'Name',
                          'tender_category_ids': 'Tender Categories',
                          'email': 'Email',
                          'phone': 'Phone',
                          'company_type': 'Company Type - Individual / Company'}
        optional_fields = ['street', 'street2', 'city', 'country_id', 'mobile', 'comment', 'state_id']
        error, vendor_data = validate_mandatory_field(required_field, kw)
        if error:
            country_id = kw.get('country_id')
            if not int(country_id) == 0:
                country_state = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
                values['state'] = country_state
                values['err_msg'] = error
                kw.update(values)
                return request.render('tk_tender_management.vendor_signup', kw)
        if kw.get('email'):
            email = kw.get('email')
            email_check = request.env['res.partner'].sudo().search([('email', '=', str(email))])
            if email_check:
                country_id = kw.get('country_id')
                country_state = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
                values['err'] = True
                values['state'] = country_state
                kw.update(values)
                return request.render('tk_tender_management.vendor_signup', kw)
        opt_data = validate_optional_fields(optional_fields, kw)
        vendor_data.update(opt_data)
        ids = request.httprequest.form.getlist('tender_category_ids')
        if ids:
            vendor_data['tender_category_ids'] = [(6, 0, ids)]
        if kw.get('vendor_image', False):
            img = kw.get('vendor_image')
            image = base64.b64encode(img.read())
            vendor_data['image_1920'] = image
        vendor_data['is_vendor'] = True
        vendor_data['website'] = kw.get('vendor_website')
        vendor_data['zip'] = kw.get('zip_code')
        vendor_data['country_id'] = int(kw.get('country_id'))
        if kw.get('state_id'):
            vendor_data['state_id'] = int(kw.get('state_id'))
        vendor_id = request.env['res.partner'].sudo().create(vendor_data)
        try:
            if request.website.auto_create:
                user_id = request.env['res.users'].sudo().search([('partner_id', '=', vendor_id.id)], limit=1)
                if not user_id and vendor_id:
                    wizard_portal_obj = request.env['portal.wizard']
                    created_portal_wizard = wizard_portal_obj.sudo().create({})
                    if created_portal_wizard and vendor_id.email and request.env.user:
                        portal_wizard_user_obj = request.env['portal.wizard.user']
                        wiz_user_vals = {
                            'wizard_id': created_portal_wizard.id,
                            'partner_id': vendor_id.id,
                            'email': vendor_id.email,
                            'is_portal': True,
                        }
                        created_portal_wizard_user = portal_wizard_user_obj.sudo().create(wiz_user_vals)
                        if created_portal_wizard_user:
                            created_portal_wizard_user.sudo().with_user(SUPERUSER_ID).action_grant_access()
            elif not request.website.auto_create and request.website.sudo().followup_user_ids.sudo():
                for user in request.website.followup_user_ids.sudo():
                    if user.sudo().partner_id.sudo() and user.sudo().partner_id.sudo().email:
                        emails.append(user.sudo().partner_id.sudo().email)
                email_values = {
                    'email_to': ','.join(emails),
                    'email_from': request.website.company_id.sudo().email,
                }
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + "/web#id=" + str(vendor_id.id) + "&&model=res.partner&view_type=form"
                ctx = {
                    "customer_url": url,
                }
                template_id = request.env.ref('tk_tender_management.vendor_signup_mail_template').sudo()
                request.env['mail.template'].sudo().browse(template_id.id).with_context(ctx).send_mail(
                    vendor_id.id, email_values=email_values, email_layout_xmlid='mail.mail_notification_light',
                    force_send=True)
        except Exception as e:
            _logger.exception(e)
        return request.render('tk_tender_management.vendor_signup_thank_you')

    @http.route(['/tender'], type='http', auth="user", website=True, cache=300)
    def tender_details(self, **kw):
        today_date = fields.Date.today()
        user = request.env.user.partner_id
        user_tender_category = user.tender_category_ids.ids
        tenders = request.env['tender.information'].sudo().search(
            [('tender_type_id', 'in', user_tender_category), ('end_date', '>=', today_date),
             ('stage', 'in', ['bid_submission'])])
        values = {
            'tender': tenders
        }
        return request.render('tk_tender_management.tender_details', values)

    @http.route(['/tender/details/<model("tender.information"):t>'], type='http', auth="user", website=True)
    def tender_information(self, t):
        today_date = fields.Date.today()
        values = {
            'applied': False,
            'tender': t.sudo(),
            'bid_range': True
        }
        partner_id = request.env.user.partner_id.id
        bidding_obj = request.env['tender.bidding'].search([('vendor_id', '=', partner_id), ('tender_id', '=', t.id)],
                                                           limit=1)
        user_tender_category = request.env.user.partner_id.tender_category_ids.ids
        if bidding_obj:
            values['applied'] = True
        if not t.sudo().bid_start_date <= today_date <= t.sudo().bid_end_date:
            values['bid_range'] = False
        if t.tender_type_id.id in user_tender_category and t.end_date >= today_date and t.stage == 'bid_submission':
            return request.render('tk_tender_management.tender_information', values)
        else:
            return request.redirect('/')

    @http.route(['/tender/details/bid/<model("tender.information"):tender>'], type='http', auth="user", website=True)
    def tender_bidding_apply(self, tender):
        data = {
            'tender_id': tender.id,
            'vendor_id': request.env.user.partner_id.id,
        }
        bid_id = request.env['tender.bidding'].sudo().create(data)
        bid_id._onchange_tender_details()
        if bid_id.vendor_id.id == request.env.user.partner_id.id:
            bid_name = bid_id.name
            bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid_id.id)
            return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid'], type='http', auth="user", website=True)
    def tender_user_bid(self):
        vendor_id = request.env.user.partner_id.id
        vendor_bid = request.env['tender.bidding'].sudo().search([('vendor_id', '=', vendor_id)])
        values = {'bids': vendor_bid}
        return request.render('tk_tender_management.tender_user_bid_info', values)

    @http.route(['/tender/bid/information/<model("tender.bidding"):b>'], type='http', auth="user",
                website=True)
    def tender_user_bid_detail(self, b):
        document_type = request.env['document.type'].sudo().search([('type', '=', 'bid')])
        tender_bidding_line = request.env['tender.bidding.line'].sudo().search([('tender_bidding_id', '=', b.id)],
                                                                               order='sequence asc')
        if b.vendor_id.id == request.env.user.partner_id.id:
            values = {
                'bid': b.sudo(),
                'document': document_type,
                'bid_line': tender_bidding_line
            }
            return request.render('tk_tender_management.tender_user_bid_details', values)
        else:
            return request.redirect('/')

    @http.route(['/tender/bid/information/upload-document'], type='http', auth="user",
                website=True)
    def tender_user_upload_documents(self, **kw):
        bid = request.env['tender.bidding'].sudo().browse(int(kw.get('bid_id')))
        bid_name = bid.name
        bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
        data = {'document_type_id': int(kw.get('document_type_id')),
                'note': kw.get('note'),
                'bidding_id': int(kw.get('bid_id'))}
        if kw.get('document', False):
            file_string = str(kw.get('document'))
            filename = file_string[file_string.index("'") + 1: file_string.index("'", file_string.index("'") + 1)]
            doc = kw.get('document')
            document = base64.b64encode(doc.read())
            data['document'] = document
            data['file_name'] = filename
        request.env['bid.document.line'].sudo().create(data)
        return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid/information/delete-document'], type='http', auth="user",
                website=True)
    def tender_user_delete_documents(self, **kw):
        if kw:
            bid = request.env['tender.bidding'].sudo().browse(int(kw.get('bid_id')))
            bid_name = bid.name
            bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
            document_record = request.env['bid.document.line'].sudo().browse(int(kw.get('document_id')))
            document_record.unlink()
            return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid/information/export-template/<model("tender.bidding"):bid>'], type='http', auth="user",
                website=True)
    def tender_user_export_template(self, bid):
        attachment = request.env['ir.attachment'].sudo()
        attachment_id = bid.sudo().export_tender_line_xls(bid, attachment)
        url = "/web/content/" + str(attachment_id.id) + "?download=true&access_token=" + attachment_id.access_token
        return request.redirect(url)

    @http.route(['/bid/information/apply-bid'], type='http', auth="user", website=True)
    def tender_user_bid_apply(self, **kw):
        bid_id = None
        for key, value in kw.items():
            line_record = request.env['tender.bidding.line'].sudo().browse(int(key))
            line_record.write({'price': float(value) if not value == "" else 0.0})
            bid_id = line_record.tender_bidding_id
            if bid_id.type == 'multiple_vendor' and line_record.price == 0.0:
                line_record.unlink()
        bid = request.env['tender.bidding'].sudo().browse(bid_id.id)
        bid.allow_edit = 'draft'
        bid._compute_bid_total()
        bid_name = bid.name
        bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
        return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid/information/request-edit-bid/<model("tender.bidding"):bid>'], type='http', auth="user",
                website=True)
    def tender_request_bid(self, bid):
        bid.edit_request = True
        bid.allow_edit = 'edit_request'
        bid.sudo().send_edit_request_mail(bid.id)
        bid_name = bid.name
        bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
        return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid/information/upload-template'], type='http', auth="user",
                website=True)
    def tender_user_upload_template(self, **kw):
        bid = request.env['tender.bidding'].sudo().browse(int(kw.get('bid_id')))
        bid_name = bid.name
        bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
        if kw.get('document', False):
            doc = kw.get('document')
            document = base64.b64encode(doc.read())
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(document))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            start_range = 1
            lines = []
            for row_index in xrange(start_range, sheet.nrows):
                raw_data = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in
                            xrange(sheet.ncols)}
                lines.append(raw_data)
            for raw_data in lines:
                try:
                    tender_bidding_id = request.env['tender.bidding'].sudo().browse(bid.id)
                    product_id = request.env['product.product'].sudo().search(
                        [('default_code', '=', raw_data.get('Code'))])
                    for data in tender_bidding_id.bidding_line_ids:
                        if data.product_id.id == product_id.id and not data.display_type:
                            data.write({
                                'price': float(raw_data.get('Your Price / Qty.'))
                            })
                    tender_bidding_id._compute_bid_total()
                except Exception as e:
                    raise ValidationError(e)

        return request.redirect('/tender/bid/information/' + bid_url)

    @http.route(['/tender/bid/information/resubmit-document/<model("tender.bidding"):bid>'], type='http', auth="user",
                website=True)
    def tender_resubmit_document(self, bid):
        bid.qualify_status = ""
        bid.stage = 'pre_qualification'
        bid_name = bid.name
        bid_url = bid_name.replace("/", "-").lower() + "-" + str(bid.id)
        return request.redirect('/tender/bid/information/' + bid_url)


class TenderVendorPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        bid = request.env['tender.bidding']
        domain = [('vendor_id', '=', request.env.user.partner_id.id)]
        values['bid_count'] = bid.sudo().search_count(domain)
        return values
