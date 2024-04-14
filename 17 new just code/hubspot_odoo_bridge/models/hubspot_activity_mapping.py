from odoo import fields, models

class ActivityMapping(models.Model):

    _name = "hubspot.activity.mapping"

    odoo_id = fields.Many2one('mail.activity','Odoo activity')
    activity_type = fields.Many2one("mail.activity.type", 'Activity Type')
    hubspot_id = fields.Char('Hubspot activity id', required=True)
    activity_object_type = fields.Selection([('partner','Partner'),('company','Company'),('deal','Lead')],string="Object Type")

    # connection_id = fields.Many2one(comodel_name='channel.connection')
    crm_lead_id = fields.Many2one('crm.lead.mapping', 'Lead Mapping')
    crm_partner_id = fields.Many2one('res.partner.mapping', 'Partner Mapping')
