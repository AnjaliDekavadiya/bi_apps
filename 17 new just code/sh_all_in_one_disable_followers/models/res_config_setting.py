# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        if self.env.company.sh_disable_follower_salesperson and self._name == 'sale.order':
            return True
        if self.env.company.sh_disable_follower_pr_purchase and self._name == 'purchase.order':
            return True
        if self.env.company.sh_disable_follower_responsible_picking and self._name == 'stock.picking':
            return True
        if self.env.company.sh_disable_follower_salesperson_account and self._name == 'account.move':
            return True
        return super(MailThread, self)._message_auto_subscribe(updated_values, followers_existing_policy)


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_disable_follower_confirm_sale = fields.Boolean(
        string='Disable to add Followers by Confirm Quotation'
    )

    sh_disable_follower_validate_invoice = fields.Boolean(
        string='Disable to add Followers by Validate Invoice/Bill'
    )

    sh_disable_follower_email = fields.Boolean(
        string='Disable to add Followers by Send by Email'
    )

    sh_disable_follower_create_picking = fields.Boolean(
        string='Disable to add Followers by Create/Update Picking'
    )
    sh_disable_follower_salesperson = fields.Boolean(
        string='Disable to add Salesperson as followers',
    )
    sh_disable_follower_pr_purchase = fields.Boolean(
        string='Disable to add Buyer as followers',
    )
    sh_disable_follower_responsible_picking = fields.Boolean(
        string='Disable to add Responsible as followers',
    )
    sh_disable_follower_salesperson_account = fields.Boolean(
        string='Disable to add Salesperson as followers ',
    )
    sh_disable_follower_confirm_rfq = fields.Boolean(
        string='Disable to add Followers by Confirm RFQ',
    )


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_disable_follower_confirm_sale = fields.Boolean(
        string='Disable to add Followers by Confirm Quotation',
        related='company_id.sh_disable_follower_confirm_sale',
        readonly=False
    )

    sh_disable_follower_validate_invoice = fields.Boolean(
        string='Disable to add Followers by Validate Invoice/Bill',
        related='company_id.sh_disable_follower_validate_invoice',
        readonly=False
    )

    sh_disable_follower_email = fields.Boolean(
        string='Disable to add Followers by Send by Email',
        related='company_id.sh_disable_follower_email',
        readonly=False
    )

    sh_disable_follower_create_picking = fields.Boolean(
        string='Disable to add Followers by Create/Update Picking',
        related='company_id.sh_disable_follower_create_picking',
        readonly=False
    )
    sh_disable_follower_salesperson = fields.Boolean(
        string='Disable to add Salesperson as followers',
        related='company_id.sh_disable_follower_salesperson',
        readonly=False
    )
    sh_disable_follower_pr_purchase = fields.Boolean(
        string='Disable to add Buyer as followers',
        related='company_id.sh_disable_follower_pr_purchase',
        readonly=False
    )
    sh_disable_follower_responsible_picking = fields.Boolean(
        string='Disable to add Responsible as followers',
        related='company_id.sh_disable_follower_responsible_picking',
        readonly=False
    )
    sh_disable_follower_salesperson_account = fields.Boolean(
        string='Disable to add Salesperson as followers ',
        related='company_id.sh_disable_follower_salesperson_account',
        readonly=False
    )

    sh_disable_follower_confirm_rfq = fields.Boolean(
        string='Disable to add Followers by Confirm RFQ',
        related='company_id.sh_disable_follower_confirm_rfq',
        readonly=False
    )
