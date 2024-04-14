# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class EventEvent(models.Model):
    """Event"""
    _inherit = 'event.event'

    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False, tracking=True, help="If event has seller then it will consider as marketplace event else it will consider as simple event.")
    status = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], "Marketplace Status", default="draft", copy=False, tracking=True)
    is_seller_event = fields.Boolean(string="Seller's Event")
    user_id = fields.Many2one(
        'res.users', string='Responsible', tracking=True,
        default=lambda self: self.env.user)

    @api.onchange("marketplace_seller_id")
    def onchange_seller_id(self):
        self.status = "draft" if self.marketplace_seller_id and not self.status else False

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            if record.marketplace_seller_id and record.status != 'approved' and not record.website_published:
                raise UserError(_("You cannot publish unapproved events."))
            record.website_published = not record.website_published
    
    def send_mail_to_seller(self, mail_templ_id):
        """ """
        if not mail_templ_id:
            return False
        template_obj = self.env['mail.template'].browse(mail_templ_id)
        template_obj.with_company(self.env.company).send_mail(self.id, True)

    def check_event_state_send_mail(self):
        resConfig = self.env['res.config.settings']
        for rec in self.filtered(lambda o: o.status in ["approved", "rejected"]):
            # Notify to admin by admin when event approved/reject
            if resConfig.get_mp_global_field_value("enable_notify_admin_on_event_approve_reject"):
                temp_id = resConfig.get_mp_global_field_value("notify_admin_on_event_approve_reject_m_tmpl_id")
                if temp_id:
                    self.send_mail_to_seller(temp_id)
            # Notify to Seller by admin  when event approved/reject
            if resConfig.get_mp_global_field_value("enable_notify_seller_on_event_approve_reject"):
                temp_id = resConfig.get_mp_global_field_value("notify_seller_on_event_approve_reject_m_tmpl_id")
                if temp_id:
                    self.send_mail_to_seller(temp_id)

    def auto_approve(self):
        for obj in self:
            auto_product_approve = obj.marketplace_seller_id.get_seller_global_fields('auto_event_approve')
            if auto_product_approve:
                obj.write({"status": "pending"})
                obj.sudo().approved()
            else:
                obj.write({"status": "pending"})
        return True
   
    def approved(self):
        for obj in self:
            if not obj.marketplace_seller_id:
                raise Warning(_("Marketplace seller id is not assign to this event."))
            if obj.marketplace_seller_id.state == "approved":
                obj.sudo().write({"status": "approved"})
                obj.check_event_state_send_mail()
            else:
                raise Warning(
                    _("Marketplace seller of this event is not approved."))
        return True
    
    def reject(self):
        for event_obj in self:
            if event_obj.status in ("draft", "pending", "approved") and event_obj.marketplace_seller_id:
                event_obj.write({
                    "website_published": False,
                    "status": "rejected"
                })
                event_obj.check_event_state_send_mail()
    
    def set_pending(self):
        for rec in self:
            rec.auto_approve()

    def send_to_draft(self):
        for rec in self:
            rec.write({"status": "draft"})

    def get_organizer_n_venue(self):
        user_obj = self.env['res.users'].browse(self._uid)
        if user_obj.seller:
            return ['|',('parent_id','=',user_obj.partner_id.id),('id','=',user_obj.partner_id.id)]
        else:
            return ['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)]

    def get_default_organizer_n_venue(self):
        user_obj = self.env['res.users'].browse(self._uid)
        if user_obj.seller:
            return user_obj.partner_id.id
        else:
            return self.env.company.partner_id

    organizer_id = fields.Many2one(
        'res.partner', string='Organizer', tracking=True,
        default=get_default_organizer_n_venue,
        domain=get_organizer_n_venue)
    
    address_id = fields.Many2one(
        'res.partner', string='Venue', default=get_default_organizer_n_venue,
        tracking=True, domain=get_organizer_n_venue)

class EventRegistration(models.Model):
    _inherit = 'event.registration'
    
    marketplace_seller_id = fields.Many2one(
            related='event_id.marketplace_seller_id', string='Marketplace Seller', store=True, copy=False)

class EventTemplateTicket(models.Model):
    _inherit = 'event.type.ticket'

    def _default_product_id(self):
        user_obj = self.env['res.users'].browse(self._uid)
        if user_obj.seller:
            return False
        else:
            return self.env.ref('event_sale.product_product_event', raise_if_not_found=False)

    def _get_event_product_domain(self):
        user_obj = self.env['res.users'].browse(self._uid)
        if user_obj.seller:
            return [('status','=','approved'),('detailed_type','=','event')]
        else:
            return [("detailed_type", "=", 'event')]

    # product
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain=_get_event_product_domain, default=_default_product_id)