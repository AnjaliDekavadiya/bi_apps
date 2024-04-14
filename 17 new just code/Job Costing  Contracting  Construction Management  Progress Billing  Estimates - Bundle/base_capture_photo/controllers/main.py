# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo import fields
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route(['/snap/image'], type='json', auth="user", website=True)
    def snap_image_json(self, access_token=None, **kw):
        print("kw-----------------",kw)
        record_id = kw.get('res_id')
        record_model = kw.get('res_model')
        imageDataURLs = kw.get('imageDataURLs')
        if record_id and record_model and imageDataURLs:
            record_obj = request.env[record_model].sudo()
            record_id = record_obj.browse(int(record_id))
            attachments = {
                'res_name': record_id.name,
                'res_model': record_model,
                'res_id': record_id,
                'datas': imageDataURLs.split(',')[1],
                'type': 'binary',
#                'datas_fname': record_id.name, odoo13
                'name': record_id.name,
            }
            attachment_obj = http.request.env['ir.attachment']
            attach = attachment_obj.sudo().create(attachments)
            record_id.sudo().write({
                 'capture_attachment_ids' : [(4,attach.id)],
            })
           
            record_id.sudo().message_post(
                author_id=request.env.user.partner_id.id,
                attachment_ids=[attach.id],
                message_type='comment'
            )
        return True
         

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
