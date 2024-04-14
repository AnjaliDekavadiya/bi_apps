# -*- coding: utf-8 -*-

import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account
from datetime import datetime, date
from odoo import fields


class website_account(website_account):

    @http.route(['/custom/rma_request/pos/<int:order>'], type='http', auth="user", website=True)
    def rma_request_pos_custom(self, **kw):
        reason = request.env['return.reason'].sudo().search([])
        pos_order = request.env['pos.order'].sudo().browse(int(kw.get('order')))
        
        partner = request.env.user.partner_id
        if pos_order.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
            return request.redirect('/my')
        
        values = {
            'order' : pos_order,
            'reason' : reason,
            'page_name' : 'pos_request_create',
        }
        return request.render("pos_return_order_rma.custom_product_return_pos_rma", values)

    @http.route(['/custom/rma_order/pos'], type='http', auth="user", website=True)
    def rma_order_pos_custom(self, **post):
        product_return = request.httprequest.form.getlist('return')
        orderline = request.httprequest.form.getlist('orderline')
        return_quantity = request.httprequest.form.getlist('returnquantity')
        attachment = request.httprequest.files.getlist('attachment')
        return_quantity = dict(zip(orderline, return_quantity))
        pos_order = request.env['pos.order'].sudo().browse(int(post.get('order')))
        reason = request.env['return.reason'].sudo().browse(int(post.get('reason')))
        values = {
            'company': request.env.user.partner_id.company_id.name,
        }
        if not product_return:
            return request.render("pos_return_order_rma.custom_select_product_pos", values)
        vals = {
                'partner_id' : pos_order.partner_id.id,
                'posorder_id': pos_order.id,
                'salesperson_id' : pos_order.user_id.id,
                'reason': post['notes'],
                'reason_id' : int(post.get('reason')),
                'create_date' : fields.Date.today(),
                'company_id' : request.env.user.company_id.id,
                'create_date' : fields.Date.today(),
                'return_identify' : str(post['return_identify']),
                'address' : post['address'],
                'shipping_reference' : post['shipping_reference'],
                'is_pos_order' : True,            }
        return_order = request.env['return.order'].sudo().create(vals)
        values.update({'name' : return_order.partner_id.name, 'number' : return_order.number, 'return_order': return_order.id})
        group_msg = _('Customer has sent %s attachments to this product. Name of attachments are: ') % (len(attachment))
        for line in product_return:
            pos_order_line = request.env['pos.order.line'].sudo().browse(int(line))
            if line in return_quantity:
                float_value = 0.0
                if not return_quantity[line]:
                    return_order.unlink()
                    return request.render("pos_return_order_rma.custom_select_product_pos")
                float_value = float(return_quantity[line]) or 0.0
                if pos_order_line.qty < float_value:
                    return_order.unlink()
                    return request.render("pos_return_order_rma.custom_select_product_pos")
                rpl_vals = {
                        'product_id' : pos_order_line.product_id.id,
                        'quantity' : pos_order_line.qty,
                        'return_quantity' : float_value,
                        'uom_id' : pos_order_line.product_id.uom_id.id,
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
                           'name': document.filename,
                       }
                attachment_obj = http.request.env['ir.attachment']
                attach_rec = attachment_obj.sudo().create(attachments)
                group_msg = group_msg + '\n' + document.filename
        group_msg = group_msg + '\n'+ '. You can see the top attachment menu to download attachments.'
        return_order.sudo().message_post(body=group_msg,message_type='comment')
        return request.render("website_request_return_rma_odoo.successful_return_product", values)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
