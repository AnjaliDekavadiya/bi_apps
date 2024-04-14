# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class IrAttachmentOdoo(models.Model):
    _inherit = 'ir.attachment'

    doc_version = fields.Float('Document Version', defult=0.0)
    docs_last_name_id = fields.Many2one('ir.attachment', 'Document Previous Version')
    docs_next_name_id = fields.Many2one('ir.attachment', 'Document Next Version')
    attachment_ids = fields.Many2many('ir.attachment', string="attachments", readonly=True, store=False)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(IrAttachmentOdoo,self).create(vals_list)
        for vals in res:
            attachments = self.env['ir.attachment'].search([('name', '=', vals.name)])
            restricts = self.env['restriction.attachment'].search([])

            if restricts:
                for restrict in restricts:
                    for line in restrict.restriction_line:
                        if vals.res_model == line.name:
                            return res

            attachments_list = []
            for attachment in attachments:
                attachments_list.append(attachment.id)
            attachments_list.sort()

            count = 1.0
            attach_count = 0
            attach_list = []
            for attachment in attachments_list:
                attach_list1 = []
                attach = self.env['ir.attachment'].browse(attachment)
                attach_list1.append(attach)
                for val1 in attach_list1:
                    a = val1.write({'doc_version': count})

                if attachment == attachments_list[0]:
                    if len(attachments_list) >= 2:
                        attach_list2 = []
                        attach_next = attachments_list[attach_count + 1]
                        next_attach = self.env['ir.attachment'].browse(attach_next)
                        attach_list2.append(attach)
                        for val2 in attach_list1:
                            val2.write({'doc_version': count})

                if attachment == attachments_list[-1]:
                    if len(attachments_list) >= 2:
                        attach_list3 = []
                        attach_pre = attachments_list[attach_count - 1]
                        pre_attach = self.env['ir.attachment'].browse(attach_pre)
                        pre_attach = self.env['ir.attachment'].browse(attach_pre)
                        attach_list3.append(attach)
                        for val3 in attach_list1:
                            val3.write({'doc_version': count})

                if len(attachments_list) >= 3:
                    if not attachment == attachments_list[0]:
                        if not attachment == attachments_list[-1]:
                            attach_list4 = []
                            attach_pre = attachments_list[attach_count - 1]
                            attach_next = attachments_list[attach_count + 1]
                            next_attach = self.env['ir.attachment'].browse(attach_next)
                            pre_attach = self.env['ir.attachment'].browse(attach_pre)
                            attach_list4.append(attach)
                            for val4 in attach_list1:
                                val4.write({'doc_version': count})
                count = count + 1
                attach_count = attach_count + 1
                attach_list.append(attach)
        return res

    def previous_view(self):
        self.ensure_one()

        if self.doc_version != 0.0:
            attachments = self.env['ir.attachment'].search([('name', '=', self.name)])
            attachments_list = []
            for attach in attachments:
                if self.doc_version > attach.doc_version:
                    if self.res_name == attach.res_name:
                        if not attach.doc_version == 0.0:
                            attachments_list.append(attach.id)

            self.attachment_ids = [(6, 0, attachments_list)]
        return {
            'name': 'Ticket Maintenance Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'res_model': 'ir.attachment',
            'domain': "[('id','in',%s)]" % (self.attachment_ids.ids)
        }

    def next_view(self):
        self.ensure_one()
        if self.doc_version != 0.0:
            attachments = self.env['ir.attachment'].search([('name', '=', self.name)])
            attachments_list = []
            for attach in attachments:
                if attach.doc_version > self.doc_version:
                    attachments_list.append(attach.id)

            self.attachment_ids = [(6, 0, attachments_list)]
        return {
            'name': 'Ticket Maintenance Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'res_model': 'ir.attachment',
            'domain': "[('id','in',%s)]" % (self.attachment_ids.ids)
        }


class RestrictionAttachment(models.Model):
    _name = 'restriction.attachment'
    _description = 'Restrict Attachment'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    restriction_line = fields.One2many('restriction.line', 'restriction_id', string="Restrict Models")


class RestrictionAttachment(models.Model):
    _name = 'restriction.line'
    _description = 'Restrict Line'

    restriction_id = fields.Many2one('restriction.attachment', string="Attachment")
    res_model_id = fields.Many2one('ir.model', 'Model', required=True, select=True, ondelete='cascade',
                                   help="The model this field belongs to")
    name = fields.Char('Model Name', related='res_model_id.model', readonly=True, store=True)
    state = fields.Selection([('manual', 'Custom Object'), ('base', 'Base Object')], string='Type',
                             related='res_model_id.state', readonly=True)
    transient = fields.Boolean(string="Transient Model")
