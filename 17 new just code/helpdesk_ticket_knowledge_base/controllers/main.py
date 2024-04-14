# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


class HelpdeskTicketFAQ(http.Controller):

    @http.route(['/ticket_faq_add'], type='http', auth="user",  website=True)
    def ticket_faq_load(self, **post):
        values = {}
        ticket_id = False
        if post.get("ticket_id", False):
            ticket_id = int(post['ticket_id'])
        values.update({'ticket_id': ticket_id})
        return request.render('helpdesk_ticket_knowledge_base.template_ticket_faq_add',values)

    @http.route(['/helpdesk_ticket_knowledge_base/add'], type='http', auth="user",  website=True)
    def ticket_faq_add(self, **post):
        values = {}
        values.update({
            'question': post.get('question', ''),
            'answer': post.get('content', ''),
            'helpdesk_ticket_id': post.get('ticket_id', False),
        })
        faq = request.env['ticket.faq'].sudo().create(values)
        if faq:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + "/ticket/faq/%s" %(slug(faq))
            faq.write({'question_url': url})
        return request.render('helpdesk_ticket_knowledge_base.ticket_faq_success',{})

    @http.route([
        '/template_ticket_faq_view_all',
         '/ticket/category/<model("ticket.faq.category"):category>',
         '/ticket/category/',
         '/ticket/tags/',
         '/template_ticket_faq_view_all/page/<int:page>',
        ], type='http', auth="user",  website=True)
    def ticket_faq_view_all(self,page=1, category=None,**post):
        domain = []
        if post.get('search', False):
            search = str(post['search'])
            domain += [
                '|', '|','|','|',
                ('question', 'ilike', search),
                ('answer', 'ilike', search),
                ('question_url', 'ilike', search),
                ('category_id', 'ilike', search),
                ('tag_ids', 'ilike', search)
            ]
        if category:
            domain += [('category_id', '=', category.id)]
            
        faq_ids_count = request.env['ticket.faq'].sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url= "/template_ticket_faq_view_all",
            total= faq_ids_count,
            page= page,
            step= 10
        )
        faq_ids = request.env['ticket.faq'].sudo().search(domain, limit=10,  offset=pager['offset'])

        categories = request.env['ticket.faq.category'].sudo().search([])
        values = {
            'faq_ids': faq_ids,
            'categories': categories,
            'pager': pager
        }
        return request.render('helpdesk_ticket_knowledge_base.template_ticket_faq_view_all',values)
    
    @http.route(['/ticket/faq/<model("ticket.faq"):faq>'], type='http', auth="user",  website=True)
    def ticket_faq_view_form(self,faq, **post):
        values = {'faq': faq}
        return request.render('helpdesk_ticket_knowledge_base.template_ticket_faq_view_form',values)
