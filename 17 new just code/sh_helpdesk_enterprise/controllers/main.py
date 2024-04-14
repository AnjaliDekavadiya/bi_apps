# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request, content_disposition
import re


class DownloadReport(http.Controller):
    def _document_check_access(self,
                               model_name,
                               document_id,
                               access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo().exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        if access_token and document_sudo.report_token and access_token == document_sudo.report_token:
            return document_sudo
        else:
            raise AccessError(
                _("Sorry, you are not allowed to access this document."))

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))
        report_sudo = request.env.ref(report_ref).sudo()
        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(
                _("%s is not the reference of a report", report_ref))
        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)(report_ref,[model.id],
                                                   data={
                                                       'report_type':
                                                       report_type
        })[0]
        reporthttpheaders = [
            ('Content-Type',
             'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-',
                                          model._get_report_base_filename()))
            reporthttpheaders.append(
                ('Content-Disposition', content_disposition(filename)))
            return request.make_response(report, headers=reporthttpheaders)

    @http.route(['/download/ht/<int:ticket_id>'],
                type='http',
                auth="public",
                website=True)
    def download_ticket(self,
                        ticket_id,
                        report_type=None,
                        access_token=None,
                        message=False,
                        download=False,
                        **kw):
        try:
            ticket_sudo = self._document_check_access(
                'helpdesk.ticket', ticket_id, access_token=access_token)
        except (AccessError, MissingError):
            return '<br/><br/><center><h1><b>Oops Invalid URL! Please check URL and try again!</b></h1></center>'
        report_type = 'pdf'
        download = True

        return self._show_report(
            model=ticket_sudo,
            report_type=report_type,
            report_ref='sh_helpdesk_enterprise.sh_action_report_helpdesk_ticket',
            download=download)


class HelpdeskTicketFeedbackController(http.Controller):
    @http.route('/ticket/feedback/<ticket_id>',
                type="http",
                auth="public",
                website=True)
    def helpdesk_ticket_feedback(self, ticket_id, **kw):
        return http.request.render('sh_helpdesk_enterprise.helpdesk_ticket_feedback_page',
                                   {'ticket': ticket_id})

    @http.route('/helpdesk/ticket/feedback/<ticket_id>',
                type="http",
                auth="public",
                website=True,
                csrf=False)
    def helpdesk_ticket_feedback_thanks(self, ticket_id, **kw):
        dic = {}
        if kw.get('smiley') != '':
            dic.update({
                'priority_new': kw.get('smiley'),
            })
        if kw.get('comment') != '':
            dic.update({
                'customer_comment': kw.get('comment'),
            })
        ticket = request.env['helpdesk.ticket'].sudo().search(
            [('id', '=', int(ticket_id))], limit=1)
        if ticket:
            ticket.sudo().write(dic)
        return http.request.render('sh_helpdesk_enterprise.ticket_feedback_thank_you', {})
