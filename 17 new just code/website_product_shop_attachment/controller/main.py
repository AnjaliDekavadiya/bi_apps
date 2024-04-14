import base64
from odoo import http
#from odoo.http import content_disposition, dispatch_rpc, request
from odoo.http import content_disposition, request
from odoo.tools.image import image_guess_size_from_field_name


class ProductAttachment(http.Controller):
    @http.route(['/web/product_attach',
        '/web/product_attach/<string:xmlid>',
        '/web/product_attach/<string:xmlid>/<string:filename>',
        '/web/product_attach/<int:id>',
        '/web/product_attach/<int:id>/<string:filename>',
        '/web/product_attach/<int:id>-<string:unique>',
        '/web/product_attach/<int:id>-<string:unique>/<string:filename>',
        '/web/product_attach/<int:id>-<string:unique>/<path:extra>/<string:filename>',
        '/web/product_attach/<string:model>/<int:id>/<string:field>',
        '/web/product_attach/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
#    def product_attach_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
#                       filename=None, filename_field='name', unique=None, mimetype=None,
#                       download=None, data=None, token=None, access_token=None, **kw):
    def product_attach_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, width=0, height=0, crop=False, nocache=False,**kw):

        try:
            record = request.env['ir.binary']._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary']._get_image_stream_from(
                record, field, filename=filename, filename_field=filename_field,
                mimetype=mimetype, width=int(width), height=int(height), crop=crop,
            )
        except UserError as exc:
            if download:
                raise request.not_found() from exc
            # Use the ratio of the requested field_name instead of "raw"
            if (int(width), int(height)) == (0, 0):
                width, height = image_guess_size_from_field_name(field)
            record = request.env.ref('web.image_placeholder').sudo()
            stream = request.env['ir.binary']._get_image_stream_from(
                record, 'raw', width=int(width), height=int(height), crop=crop,
            )
        
        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        return stream.get_response(**send_file_kwargs)
#        http_obj = request.env['ir.http']
#        if kw.get("product_tmp_id"):
#            product_id = request.env['product.template'].sudo().browse(int(kw.get("product_tmp_id")))
#            print("product_id",product_id)
#            if id in product_id.website_product_attachment.ids:
#                http_obj = request.env['ir.http'].sudo()
#        status, headers, content = http_obj.binary_content(
#            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
#            filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)
#        if status != 200:
#            return request.env['ir.http']._response_by_status(status, headers, content)
#        else:
#            content_base64 = base64.b64decode(content)
#            headers.append(('Content-Length', len(content_base64)))
#            response = request.make_response(content_base64, headers)
#        if token:
#            response.set_cookie('fileToken', token)
#        return response
