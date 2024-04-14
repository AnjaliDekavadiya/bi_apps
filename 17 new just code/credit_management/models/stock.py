# Copyright 2020-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _hold_picking_search(self, operator, value):
        if operator == "=" and value:
            recs = self.search([]).filtered(
                lambda x: x.hold_delivery_till_payment is True
            )
        elif operator == "!=" and value:
            recs = self.search([]).filtered(
                lambda x: x.hold_delivery_till_payment is not True
            )
        elif operator == "!=" and not value:
            recs = self.search([]).filtered(
                lambda x: x.hold_delivery_till_payment is not False
            )
        return [("id", "in", [x.id for x in recs])]

    hold_delivery_till_payment = fields.Boolean(
        default=False,
        copy=False,
        compute="_compute_check_delivery_hold",
        string="Hold Delivery",
        help="If True, then holds the DO until  \
                                    invoices are paid and equals to the total amount on the SO",
        search=_hold_picking_search,
    )
    show_check_availability_credit_management = fields.Boolean(
        compute="_compute_show_check_availability_credit_management"
    )

    def _compute_show_check_availability_credit_management(self):
        stock_allow_check_availability = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("credit_management.stock_allow_check_availability", False)
        )
        for picking in self:
            picking.show_check_availability_credit_management = True
            if (not picking.hold_delivery_till_payment) or (
                picking.hold_delivery_till_payment and stock_allow_check_availability
            ):
                picking.show_check_availability_credit_management = False

    def button_validate(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                return picking.show_do_hold_warning()
            if partner.credit_hold and not self._context.get("website_order_tx", False):
                raise UserError(_("Credit Hold!\n\nThis customer is on Credit hold."))
        return super().button_validate()

    def action_confirm(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                if picking._context.get("hold_do"):
                    return picking.show_do_hold_warning()
                else:
                    return
            if partner.credit_hold and not self._context.get("website_order_tx", False):
                raise UserError(_("Credit Hold!\n\nThis customer is on Credit hold."))
        return super().action_confirm()

    def action_assign(self):
        stock_allow_check_availability = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("credit_management.stock_allow_check_availability", False)
        )
        unassign_picking = self.browse()
        if (
            len(self) == 1
            and self.hold_delivery_till_payment
            and not stock_allow_check_availability
        ):
            raise UserError(_("Credit Hold!\n\nThis customer is on Credit hold."))
        if (
            len(self) == 1
            and self.partner_id.commercial_partner_id.credit_hold
            and not self._context.get("website_order_tx", False)
        ):
            raise UserError(_("Credit Hold!\n\nThis customer is on Credit hold."))
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if partner.credit_hold and not picking._context.get(
                "website_order_tx", False
            ):
                unassign_picking |= picking
            elif (
                picking.hold_delivery_till_payment
                and not stock_allow_check_availability
            ):
                unassign_picking |= picking
        return super(
            StockPicking, self.filtered(lambda x: x.id not in unassign_picking.ids)
        ).action_assign()

    def _compute_check_delivery_hold(self):
        for picking in self:
            if (
                picking.sale_id.hold_delivery_till_payment
                and not picking.sale_id.check_invoice_fully_paid()
            ):
                picking.hold_delivery_till_payment = True
            else:
                picking.hold_delivery_till_payment = False

    def show_do_hold_warning(self):
        """Raise user warning if the invoice(s) is/are not fully paid."""
        raise UserError(_("Delivery is on hold."))


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        """This method adds hold delivery domain to restrict while checking
        availability during the scheduler run"""
        hold_do_picking = self.env["stock.move"].search(
            [("picking_id.hold_delivery_till_payment", "=", True)]
        )
        stock_allow_check_availability = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("credit_management.stock_allow_check_availability", False)
        )
        domain = super()._get_moves_to_assign_domain(company_id)
        if not stock_allow_check_availability:
            domain = expression.AND([domain, [("id", "not in", hold_do_picking.ids)]])
        return domain
