# -*- coding: utf-8 -*-

import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account
from datetime import datetime, date
from odoo import fields


class website_account(website_account):

    @http.route(['/rma_request/<int:order>'], type='http', auth="user", website=True)
    def rma_request(self, **kw):
        reason = request.env['return.reason'].sudo().search([])
        sale_order = request.env['sale.order'].sudo().browse(int(kw.get('order')))
        
        partner = request.env.user.partner_id
        if sale_order.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
            return request.redirect('/my')
        
        values = {
            'order' : sale_order,
            'reason' : reason,
            'page_name' : 'rma_request_create',
        }
        return request.render("website_request_return_rma_odoo.product_return", values)

    @http.route(['/rma_order'], type='http', auth="user", website=True)
    def rma_order(self, **post):
        product_return = request.httprequest.form.getlist('return')
        orderline = request.httprequest.form.getlist('orderline')
        return_quantity = request.httprequest.form.getlist('returnquantity')
        attachment = request.httprequest.files.getlist('attachment')
        return_quantity = dict(zip(orderline, return_quantity))
        sale_order = request.env['sale.order'].sudo().browse(int(post.get('order')))
        reason = request.env['return.reason'].sudo().browse(int(post.get('reason')))
        values = {
            'company': request.env.user.partner_id.company_id.name,
        }
        if not product_return:
            return request.render("website_request_return_rma_odoo.select_product", values)
        vals = {
                'partner_id' : sale_order.partner_id.id,
                'saleorder_id': sale_order.id,
                'salesperson_id' : sale_order.user_id.id,
                'team_id' : sale_order.team_id.id,
                'reason': post['notes'],
                'reason_id' : int(post.get('reason')),
                'create_date' : fields.Date.today(),
                'company_id' : request.env.user.company_id.id,
                'create_date' : fields.Date.today(),
                'return_identify' : str(post['return_identify']),
                'address' : post['address'],
                'shipping_reference' : post['shipping_reference'],
            }
        return_order = request.env['return.order'].sudo().create(vals)
        values.update({'name' : return_order.partner_id.name, 'number' : return_order.number, 'return_order': return_order.id})
        group_msg = _('Customer has sent %s attachments to this product. Name of attachments are: ') % (len(attachment))
        for line in product_return:
            sale_order_line = request.env['sale.order.line'].sudo().browse(int(line))
            if line in return_quantity:
                float_value = 0.0
                if not return_quantity[line]:
                    return_order.unlink()
                    return request.render("website_request_return_rma_odoo.select_product")
                float_value = float(return_quantity[line]) or 0.0
                if sale_order_line.qty_delivered < float_value:
                    return_order.unlink()
                    return request.render("website_request_return_rma_odoo.select_product")
                rpl_vals = {
                        'product_id' : sale_order_line.product_id.id,
                        'quantity' : sale_order_line.product_uom_qty,
                        'return_quantity' : float_value,
                        'uom_id' : sale_order_line.product_id.uom_id.id,
                        'return_order_id': return_order.id,
                    }
                rpl_line = request.env['return.product.line'].sudo().create(rpl_vals)
                if post.get('attachment'):
                    attachments = {
                           'res_name': post.get('attachment').filename,
                           'res_model': 'return.order',
                           'res_id': rpl_line.id,
                           'datas': base64.b64encode(post.get('attachment').read()),
                           'type': 'binary',
#                           'datas_fname': post.get('attachment').filename, odoo13
                           'name': post.get('attachment').filename,
                       }
                    attachment_obj = http.request.env['ir.attachment']
                    attach_rec = attachment_obj.sudo().create(attachments)
        for document in attachment:
            if document:
                attachments = {
                           'res_name': document.filename,
                           'res_model': 'return.order',
                           'res_id': return_order.id,
                           'datas': base64.b64encode(document.read()),
                           'type': 'binary',
#                           'datas_fname': document.filename, odoo13
                           'name': document.filename,
                       }
                attachment_obj = http.request.env['ir.attachment']
                attach_rec = attachment_obj.sudo().create(attachments)
                group_msg = group_msg + '\n' + document.filename
        group_msg = group_msg + '\n'+  '. You can see top attachment menu to download attachments.'
        return_order.sudo().message_post(body=group_msg,message_type='comment')
        return request.render("website_request_return_rma_odoo.successful_return_product", values)
    
    # @http.route(['/my/returns/printrma/<int:return_id>'], type='http', auth="public", website=True)
    # def portal_pos_order_report(self, return_id, access_token=None, **kw):
    #     return_obj = request.env['return.order']
    #     rma_id = return_obj.sudo().browse(int(return_id))
    #     partner = request.env.user.partner_id
    #     if rma_id.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
    #         return request.redirect('/my')
        
    #     pdf = request.env.ref('website_request_return_rma_odoo.print_rma_report').sudo()._render_qweb_pdf([return_id])[0]
    #     pdfhttpheaders = [
    #         ('Content-Type', 'application/pdf'),
    #         ('Content-Length', len(pdf)),
    #     ]
    #     return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/my/returns/printrma/<model("return.order"):return_order_id>'], type='http', auth="user", website=True)
    def custom_return_printrma(self, return_order_id, access_token=None, report_type='pdf', download=False, **kw):
        try:
            return_order_sudo = self._document_check_access('return.order', return_order_id.id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=return_order_sudo, report_type=report_type, report_ref='website_request_return_rma_odoo.print_rma_report', download=download)

        return request.redirect('/my')

    @http.route(['/my/returns/detail/form/<int:return_id>'], type='http', auth="user", website=True)
    def return_order_request_form(self, return_id=None, **kw):
       returns_orders = request.env['return.order'].sudo().browse(int(return_id))
       values = {'return_details' : returns_orders,'page_name':'return_details_page'}
       return request.render("website_request_return_rma_odoo.display_return_request_order_details_probc", values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
