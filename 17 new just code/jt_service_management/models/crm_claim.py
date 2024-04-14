# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
import time
from datetime import date
import datetime
import calendar
from odoo.exceptions import UserError
import warnings

STAGES = [
    ('new', 'New'),
    ('logged', 'Assigned'),
    ('in_diagnosis', 'In Diagnosis'),
    ('diagnosed', 'Diagnosed'),
    ('waiting_for_spares', 'Waiting Confirmation'),
    ('repaired', 'Repaired'),
    ('unrepairable', 'Unrepairable'),
    ('ready_for_collection', 'Ready for Collection'),
    ('collected', 'Collected'),
]


class CrmClaimStage(models.Model):
    """Model for claim stages. This models the main stages of a claim
    management flow. Main CRM objects (leads, opportunities, project
    issues, ...) will now use only stages, instead of state and stages.
    Stages are for example used to display the kanban view of records.
    """
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _order = "sequence"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer(
        'Sequence',
        help="Used to order stages. Lower is better.",
        default=1
    )
    team_ids = fields.Many2many(
        'crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id',
        string='Teams',
        help="Link between stages and sales teams. When set, this limits the current stage"
             "to the selected sales teams."
    )
    case_default = fields.Boolean(
        'Common to All Teams',
        help="If you check this field, this stage will be proposed by default on each sales team."
             "It will not assign this stage to existing teams."
    )


class CrmClaim(models.Model):
    _name = "crm.claim"
    _description = "After Sales"
    _order = "priority, date desc"
    _inherit = ['mail.thread']

    @api.model
    def _get_service_center(self):
        """
        Set default service center of the login user inside the ticket.
        :return: service center.
        """
        return self.env.user.service_center_id.id or False

    def _valid_field_parameter(self, field, name):
        return (
            name in ('date', 'service_engineer_id', \
                'stage', 'start_date_warranty', 'end_date_warranty', 'start_date_sup_warranty', 'end_date_sup_warranty')
            or super()._valid_field_parameter(field, name)
        )

    product_id = fields.Many2one('product.product', 'Product', copy=False)
    name = fields.Char('Ticket Number', index=True, readonly=True, default='New', copy=False)
    # active = fields.Boolean('Active', default=True)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    resolution = fields.Text('Resolution')
    date_deadline = fields.Date('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Ticket Date', default=fields.Datetime.now, tracking=True) #, track_visibility='always'
    serial_number = fields.Char('Serial Num')
    categ_id = fields.Many2one('crm.claim.category', 'Category')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority')
    action_type_id = fields.Many2one('service.action.type', 'Action Type')
    service_engineer_id = fields.Many2one('res.users', 'Service Engineer', tracking=True) #, track_visibility='always'
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', help="Responsible sales team. Define Responsible user and Email account for mail gateway.",
                              default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid))
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env['res.company']._company_default_get('crm.team'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    email_cc = fields.Text('Watchers Emails',
                           help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma",
                           copy=False)
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.", copy=False)
    partner_phone = fields.Char('Phone', copy=False)
    stage = fields.Selection(STAGES, 'Stage', copy=False, default='new', tracking=True) #, track_visibility='onchange'
    cause = fields.Text('Root Cause', copy=False)
    details_ids = fields.One2many('service.parts.info.one', 'new_part_id', 'Equipment Details', copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Total Receptions', default=0, copy=False)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False)
    sale_id = fields.Many2one('sale.order', string='Quotation', copy=False)
    sale_ref = fields.Char(related='sale_id.name', string="Order Reference", store=True)
    sale_count = fields.Integer(string='Sale Count', default=0)
    invoice_id = fields.Many2one('account.move', string='Invoice Status')
    quotation = fields.Boolean('Quote Created')
    parts_confirmed = fields.Boolean('Parts Confirmed', default=False)
    invoice_created = fields.Boolean('Invoice Created')
    product_brand_id = fields.Many2one('product.brand', related='product_id.brand_id', string="Brand", store=True)
    date_sold = fields.Date('Date Sold')
    quote_state = fields.Selection([('to_quote', 'To Quote'), ('quoted', 'Quoted'), ('not_quoted', 'Not Quoted'),
                                    ('quoted_confirmed', 'Repair Confirmed'),
                                    ('order_confirmed', 'Confirmed Order')], 'Quote State', copy=False)
    service_center_id = fields.Many2one('service.center', string='Service Center', default=_get_service_center)
    ready_collection_date = fields.Date('Ready for Collection Date')
    repair_date = fields.Datetime("Repair Date")
    start_date_warranty = fields.Date('Warranty Start Date', tracking=True) #, track_visibility='onchange'
    end_date_warranty = fields.Date('Warranty End Date', tracking=True) #, track_visibility='onchange'
    warranty_periods = fields.Selection([('under_warranty', 'Under Warranty'),
                                         ('warranty_expired', 'Expired'),
                                         ('warranty_extended', 'Void')],
                                        string="Warranty Status")
    start_date_sup_warranty = fields.Date('Supplier Warranty Start Date', tracking=True) #, track_visibility='onchange'
    end_date_sup_warranty = fields.Date('Supplier Warranty End Date', tracking=True) #, track_visibility='onchange'
    sup_warranty_periods = fields.Selection([('under_warranty', 'Under Warranty'),
                                             ('warranty_expired', 'Expired'),
                                             ('warranty_extended', 'Void')],
                                            string="Supplier Warranty Status")
    do_reference = fields.Char("Delivery Order reference number")
    date_collected = fields.Date('Date Collected', copy=False)
    is_send_noti_collected = fields.Boolean("Is Send Notification Collected", copy=False, default=False)
    is_send_noti_created = fields.Boolean("Is Send Notification Created", copy=False, default=False)
    ticket_created_mail_id = fields.Many2one('mail.mail', string='Ticket Created Mail')
    warranty_state_void = fields.Text(string="Warranty void reason")

    def update_status_of_wt(self):
        for ticket in self:
            for part in ticket.details_ids:
                for move in part.move_ids:
                    part.status_of_wt = move.state

    def update_do_ref(self):
        """
        Used from a server action to blank Do Reference.
        """
        for ticket in self:
            ticket.do_reference = ''

    def action_diagnosed(self):
        self.ensure_one()
        self.stage = 'diagnosed'

    def write(self, vals):
        """
        This function sends mail when a ticket is collected, repaired, and unrepairable.
        Updates warranty details based on the lot number.
        :param vals:
        :return:
        """
        result = super(CrmClaim, self).write(vals)
        seq_obj = self.env['ir.sequence'].sudo()
        for ticket in self:
            ir_mail_server_obj = self.env['ir.mail_server'].sudo()

            # Template IDs
            collected_template_id = self.env.ref('jt_service_management.email_notification_ticket_collected')

            # Mail Server ID
            mail_server_id = ir_mail_server_obj.search([], limit=1)

            if vals.get('stage'):
                if vals.get('stage') == 'collected' and 'from_report' not in self._context:
                    ticket.do_reference = seq_obj.next_by_code('crm.claim.do') or _('New')
                if vals.get('stage') == 'collected':
                    ticket.date_collected = datetime.datetime.today().date()

            service_center_mail = ir_mail_server_obj.sudo().search([], limit=1)
            if vals.get('stage') == 'repaired':
                ticket.repair_date = fields.Datetime.now()

            if vals.get('serial_number'):
                serial_no = vals.get('serial_number')
                product_id = ticket.product_id.id if ticket.product_id else vals.get('product_id')
                stock_production_lot = self.env['stock.lot'].search([
                    ('name', '=', serial_no),
                    ('product_id', '=', product_id)
                ])
                if stock_production_lot:
                    ticket.start_date_warranty = stock_production_lot.start_date_warranty
                    ticket.end_date_warranty = stock_production_lot.end_date_warranty
                    ticket.start_date_sup_warranty = stock_production_lot.start_date_sup_warranty
                    ticket.end_date_sup_warranty = stock_production_lot.end_date_sup_warranty

                    if stock_production_lot.warranty_periods in ('under_warranty', 'warranty_expired'):
                        ticket.warranty_periods = stock_production_lot.warranty_periods

                    if stock_production_lot.sup_warranty_periods in ('under_warranty', 'warranty_expired'):
                        ticket.sup_warranty_periods = stock_production_lot.sup_warranty_periods
        return result

    @api.model
    def send_notification_to_service_center(self):
        """
        This function sends a weekly reminder to the service center for Repaired, Ready for collection, Waiting
        confirmation, New, Assigned, and In Diagnosis tickets of the last 1, 2, and 3 months.
        :return:
        """
        mail_server_id = self.env['ir.mail_server'].sudo().search([], limit=1)
        if not mail_server_id:
            raise warnings.warn("Please configure the email server!")

        template_id = self.env.ref('jt_service_management.email_temp_notification_for_service_center')
        crm_claim = self.env['crm.claim']
        for service_center in crm_claim.search([]).mapped('service_center_id'):
            current_date = datetime.datetime.today()
            last_month = current_date.month - 1 if current_date.month > 1 else 12
            last_year = current_date.year - 1
            last_month_days = calendar.monthrange(last_year, last_month)[1]

            last_two_month = current_date.month - 2 if current_date.month > 1 else 12
            last_two_year = current_date.year - 2
            last_two_month_days = calendar.monthrange(last_two_year, last_two_month)[1]

            one_mon_over_date = datetime.datetime.today() - datetime.timedelta(days=last_month_days)
            two_mon_over_date = datetime.datetime.today() - datetime.timedelta(days=last_two_month_days + last_month_days)

            domain_1_month = ('date', '>=', str(one_mon_over_date)), ('date', '<=', str(current_date))
            domain_2_month = ('date', '>=', str(two_mon_over_date)), ('date', '<=', str(one_mon_over_date))
            domain_3_month = ('date', '<=', str(two_mon_over_date))
            service_center_domain = ('service_center_id', '=', service_center.id)

            repaired_domain = ('stage','=','repaired')
            repaired_over_1_mon = crm_claim.search([service_center_domain, repaired_domain, domain_1_month[0], domain_1_month[1]])
            repaired_over_2_mon = crm_claim.search([service_center_domain, repaired_domain, domain_2_month[0], domain_2_month[1]])
            repaired_over_3_mon = crm_claim.search([service_center_domain, repaired_domain, domain_3_month])

            ready_domain = ('stage','=','ready_for_collection')
            ready_over_1_mon = crm_claim.search([service_center_domain, ready_domain, domain_1_month[0], domain_1_month[1]])
            ready_over_2_mon = crm_claim.search([service_center_domain, ready_domain, domain_2_month[0], domain_2_month[1]])
            ready_over_3_mon = crm_claim.search([service_center_domain, ready_domain, domain_3_month])

            waiting_domain = ('stage','=','waiting_for_spares')
            waiting_over_1_mon = crm_claim.search([service_center_domain, waiting_domain, domain_1_month[0], domain_1_month[1]])
            waiting_over_2_mon = crm_claim.search([service_center_domain, waiting_domain, domain_2_month[0], domain_2_month[1]])
            waiting_over_3_mon = crm_claim.search([service_center_domain, waiting_domain, domain_3_month])

            new_domain = ('stage','=','new')
            new_over_1_mon = crm_claim.search([service_center_domain, new_domain, domain_1_month[0], domain_1_month[1]])
            new_over_2_mon = crm_claim.search([service_center_domain, new_domain, domain_2_month[0], domain_2_month[1]])
            new_over_3_mon = crm_claim.search([service_center_domain, new_domain, domain_3_month])

            assigned_domain = ('stage','=','logged')
            assigned_over_1_mon = crm_claim.search([service_center_domain, assigned_domain, domain_1_month[0], domain_1_month[1]])
            assigned_over_2_mon = crm_claim.search([service_center_domain, assigned_domain, domain_2_month[0], domain_2_month[1]])
            assigned_over_3_mon = crm_claim.search([service_center_domain, assigned_domain, domain_3_month])

            diagnosis_domain = ('stage','=','in_diagnosis')
            diagnosis_over_1_mon = crm_claim.search([service_center_domain, diagnosis_domain, domain_1_month[0], domain_1_month[1]])
            diagnosis_over_2_mon = crm_claim.search([service_center_domain, diagnosis_domain, domain_2_month[0], domain_2_month[1]])
            diagnosis_over_3_mon = crm_claim.search([service_center_domain, diagnosis_domain, domain_3_month])

            if template_id or repaired_over_1_mon or repaired_over_2_mon or repaired_over_3_mon or \
                ready_over_1_mon or ready_over_2_mon or ready_over_3_mon or \
                waiting_over_1_mon or waiting_over_2_mon or waiting_over_3_mon or \
                new_over_1_mon or new_over_2_mon or new_over_3_mon or \
                assigned_over_1_mon or assigned_over_2_mon or assigned_over_3_mon or \
                diagnosis_over_1_mon or diagnosis_over_2_mon or diagnosis_over_3_mon :
                
                template_id.with_context(repaired_over_1_mon=repaired_over_1_mon,
                repaired_over_2_mon=repaired_over_2_mon, repaired_over_3_mon=repaired_over_3_mon,
                ready_over_1_mon=ready_over_1_mon, ready_over_2_mon=ready_over_2_mon,
                ready_over_3_mon=ready_over_3_mon, waiting_over_1_mon=waiting_over_1_mon,
                waiting_over_2_mon=waiting_over_2_mon, waiting_over_3_mon=waiting_over_3_mon,
                new_over_1_mon=new_over_1_mon, new_over_2_mon=new_over_2_mon, new_over_3_mon=new_over_3_mon,
                assigned_over_1_mon=assigned_over_1_mon, assigned_over_2_mon=assigned_over_2_mon,
                assigned_over_3_mon=assigned_over_3_mon, diagnosis_over_1_mon=diagnosis_over_1_mon,
                diagnosis_over_2_mon=diagnosis_over_2_mon, diagnosis_over_3_mon=diagnosis_over_3_mon,
                email_from=mail_server_id.smtp_user, email_to=service_center.partner_id.email, service_center=service_center,
                current_date=datetime.datetime.now().date()).send_mail(self.id)

    def action_view_sale(self):
        """
        This function returns the quotation tree view with the ticket quotation.
        :return: Quotation tree view of ticket sale.
        """
        domain = [("id", "=", self.sale_id.id)]
        tree_id = self.env.ref("sale.view_quotation_tree", raise_if_not_found=False)
        form_id = self.env.ref("sale.view_order_form", raise_if_not_found=False)

        return {
            "name": _("Quotation"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree, form",
            "views": [(tree_id.id, "tree"), (form_id.id, "form")],
            "res_model": "sale.order",
            "target": "current",
            "domain": domain,
            "action": "sale.action_quotations",
        }

    def action_view_diagnosis(self):
        """
        This function returns the popup to select the diagnosis state.
        :return: Wizard to select the diagnosis state.
        """
        if self.details_ids:
            form_id = self.env.ref("jt_service_management.view_diagnosis_action_state_form", raise_if_not_found=False)
            return {
                "name": _("Diagnosis State"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "views": [(form_id.id, "form")],
                "res_model": "diagnosis.action.state",
                "target": "new",
                "context": {"ticket_id": self.id},
                "action": "jt_service_management.action_diagnosis_action_state"
            }
        else:
            raise UserError(_("Please add spare parts"))

    def action_view_picking(self):
        """
        This function returns an action that displays existing picking orders of given purchase order ids.
        When only one is found, show the picking immediately.
        """
        action = self.env.ref("jt_service_management.action_picking_tree_all_picking")
        result = action.read()[0]

        # Override the context to get rid of the default filtering on picking type
        result.pop("id", None)
        result["context"] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])

        # Choose the view_mode accordingly
        if len(pick_ids) > 1:
            result["domain"] = "[('id','in',[" + ",".join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref("jt_service_management.view_picking_form_ticket", raise_if_not_found=False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = pick_ids and pick_ids[0] or False

        return result
    
    @api.depends("details_ids.move_ids")
    def _compute_picking(self):
        """
        This function counts the pickings of the ticket.
        """
        for order in self:
            pickings = self.env["stock.picking"]
            for line in order.details_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                moves = line.move_ids | line.move_ids.mapped("returned_move_ids")
                # moves = moves.filtered(lambda r: r.state != 'cancel')
                pickings |= moves.mapped("picking_id")
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    def action_reset_draft(self):
        """
        This function changes the stage to new when resetting the ticket.
        :return: new stage of the ticket.
        """
        self.stage = 'new'

    def action_log(self):
        """
        This function changes the stage to Assigned when assigning the ticket and raises a warning if the service engineer or
        category is not selected.
        :return: Assigned stage and warning if the service engineer or category is not selected.
        """
        self.stage = 'logged'
        if not self.service_engineer_id:
            raise UserError(_('Please select Service Engineer'))

        if not self.categ_id:
            raise UserError(_('Please select Category'))

    def action_confirm_repair(self):
        """
        This function changes the stage to In Diagnosis and sets the Quote state 'Quoted and Confirmed' when confirming
        repair.
        :return: In Diagnosis and Quote state 'Quoted and Confirmed'.
        """
        self.stage = 'in_diagnosis'
        self.quote_state = 'quoted_confirmed'

    def action_ready_for_collection(self):
        """
        This function changes the stage to 'Ready for Collection', sets the ready for collection date, and raises a warning if
        the quotation is not created and confirmed.
        :return: Ready for collection stage, set date of ready for collection and warning if quotation is not created
         and confirmed.
        """
        if self.stage == 'repaired' and not self.sale_id:
            raise UserError(_('Ticket cannot be made ready for collection until a quotation is created and confirmed.'))
        if self.stage == 'repaired' and self.sale_id:
            if self.sale_id.state in ['draft', 'sent', 'cancel']:
                raise UserError(_('Ticket cannot be made ready for collection until the related order is confirmed.'))
        self.stage = 'ready_for_collection'
        self.ready_collection_date = date.today().strftime('%Y-%m-%d')

    def action_collected(self):
        """
        This function changes the stage to 'Collected'.
        :return: Collected stage.
        """
        self.stage = 'collected'

    def action_repaired(self):
        """
        This function changes the stage to 'Repaired'.
        :return: Repaired stage.
        """
        self.stage = 'repaired'
        if not self.cause:
            raise UserError(_('Please Enter Description of Action taken'))

    def action_unrepairable(self):
        """
        This function changes the stage to 'Unrepaired'.
        :return: Unrepaired stage.
        """
        self.stage = 'unrepairable'

    def action_start_diagnosis(self):
        """
        This function changes the stage to 'In Diagnosis'.
        :return:
        """
        self.stage = 'in_diagnosis'
    
    def create_quotation(self):
        """
        This function creates a quotation for the ticket, changes Quote state to Quoted, and adds the sale ID of the created quotation.
        :return: Sale order ID.
        """
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']
        
        quotation = sale_order.search([('partner_id', '=', self.partner_id.id),
                                       ('state', '=', 'draft'),
                                       ('team_id', '=', self.service_engineer_id.service_center_id.sales_team_id.id)],
                                      limit=1)
        
        if not self.service_engineer_id.service_center_id:
            raise UserError(_("The Service Center is not attached to the User record and this is required for creating the Picking List. Please contact the administrator or service manager"))
        
        service_center = self.service_engineer_id.service_center_id
        
        if not quotation:
            price_list = self.partner_id.property_product_pricelist
            data = {'name': self.env['ir.sequence'].sudo().next_by_code('sale.order') or _('New'),
                    'partner_id': self.partner_id.id,
                    'state': 'draft',
                    'pricelist_id': price_list.id if price_list else False,
                    'currency_id': price_list.currency_id.id if price_list else False}
            
            if service_center:
                data.update({'team_id': service_center.sales_team_id.id})
                data.update({'warehouse_id': service_center.picking_type_id.warehouse_id.id} if service_center.picking_type_id and service_center.picking_type_id.warehouse_id else {})
            quotation = sale_order.create(data)
        
        if quotation:
            if service_center:
                quotation.team_id = service_center.sales_team_id.id
                quotation.warehouse_id = service_center.picking_type_id.warehouse_id.id if service_center.picking_type_id and service_center.picking_type_id.warehouse_id else False
            
            for detail_id in self.details_ids:
                group = f"{self.name}-[{self.product_id.default_code}]-{self.serial_number}" if self.product_id.default_code else f"{self.name}-[]-{self.serial_number}"
                sale_order_line.create({
                    'name': detail_id.product_id.name,
                    'order_id': quotation.id,
                    'group': group,
                    'product_id': detail_id.product_id.id,
                    'product_uom_qty': detail_id.quantity
                    })
            
            self.sale_id = quotation.id
        
        self.quote_state = 'quoted'
        self.sale_count = 1

    def action_add_ticket_to_quotation(self):
        """
        This function checks quotations for the related customer of the ticket. If no quotation exists, raise a warning;
        otherwise, open a wizard to select and add quotations related to the ticket.
        :return: wizard with related quotations of the ticket and raise a warning if no quotation exists.
        """
        self.ensure_one()

        if self.partner_id.is_company:
            quotations = self.env['sale.order'].search([('state', 'in', ('draft', 'sent')),
                                                        '|', ('partner_id', '=', self.partner_id.id),
                                                        ('partner_id', 'in', self.partner_id.child_ids.ids)])
        elif self.partner_id.parent_id:
            quotations = self.env['sale.order'].search([('state', 'in', ('draft', 'sent')),
                                                        '|', ('partner_id', '=', self.partner_id.parent_id.id),
                                                        ('partner_id', 'in', self.partner_id.parent_id.child_ids.ids)])
        else:
            quotations = self.env['sale.order'].search([('state', 'in', ('draft', 'sent')),
                                                        ('partner_id', '=', self.partner_id.id)])
        if quotations:
            form_id = self.env.ref('jt_service_management.add_ticket_to_quotation_form', False)
            if form_id:
                return {
                    'name': _('Add Ticket to Quotation'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(form_id.id, 'form')],
                    'res_model': 'ticket.quotations',
                    'target': 'new',
                    'action': 'jt_service_management.action_add_ticket_to_quotation'
                }
        else:
            partner_name = self.partner_id.parent_id.name if self.partner_id.parent_id else self.partner_id.name
            raise warnings.warn("No quotation available for %s, please choose 'Create Quotation' button option." % partner_name)

    @api.onchange('product_id')
    def _onchange_product(self):
        """
        This function changes the brand of the product when the product changes.
        :return: Product brand
        """
        self.product_brand_id = self.product_id.brand_id.id if self.product_id and self.product_id.brand_id else False
    
    def cron_update_warranty(self):
        current_date = fields.Datetime.now.strftime("%Y-%m-%d %H:%M:%S")
        crm_claim_obj = self.env['crm.claim']

        under_warranty_tickets = crm_claim_obj.search([
            ('end_date_warranty', '>=', current_date),
            ('warranty_periods', 'in', ('warranty_expired', 'under_warranty'))
        ])

        expired_tickets = crm_claim_obj.search([
            ('end_date_warranty', '<', current_date),
            ('warranty_periods', 'in', ('warranty_expired', 'under_warranty'))
        ])

        for ticket in expired_tickets:
            ticket.warranty_periods = 'warranty_expired'

        for ticket in under_warranty_tickets:
            ticket.warranty_periods = 'under_warranty'

        under_sup_warranty_tickets = crm_claim_obj.search([
            ('end_date_sup_warranty', '>=', current_date),
            ('warranty_periods', 'in', ('warranty_expired', 'under_warranty'))
        ])

        sup_warranty_expiry_tickets = crm_claim_obj.search([
            ('end_date_sup_warranty', '<', current_date),
            ('warranty_periods', 'in', ('warranty_expired', 'under_warranty'))
        ])

        for ticket in sup_warranty_expiry_tickets:
            ticket.sup_warranty_periods = 'warranty_expired'

        for ticket in under_sup_warranty_tickets:
            ticket.sup_warranty_periods = 'under_warranty'

    @api.onchange('serial_number', 'product_id')
    def onchange_serial_number(self):
        """This function returns value of partner address based on partner."""
        stock_production_lot = self.env['stock.lot'].search([('name', '=', self.serial_number)], limit=1)
        if stock_production_lot:
            warranty_status = stock_production_lot.warranty_periods
            partner = stock_production_lot.partner_id
            return {
                'value': {
                    'email_from': partner.email or False,
                    'partner_phone': partner.phone or False,
                    'product_id': stock_production_lot.product_id.id or False,
                    'partner_id': partner.id or False,
                    'warranty_periods': warranty_status or 'under_warranty',
                    'start_date_warranty': stock_production_lot.start_date_warranty,
                    'end_date_warranty': stock_production_lot.end_date_warranty,
                    'start_date_sup_warranty': stock_production_lot.start_date_sup_warranty,
                    'end_date_sup_warranty': stock_production_lot.end_date_sup_warranty,
                    'sup_warranty_periods': stock_production_lot.sup_warranty_periods or 'under_warranty',
                    'product_brand_id': stock_production_lot.product_id and
                                       stock_production_lot.product_id.brand_id and
                                       stock_production_lot.product_id.brand_id.id,
                    'date_sold': stock_production_lot.delivery_date or False
                }
            }

    def message_new(self, msg_dict, custom_values=None):
        """Overrides mail_thread message_new that is called by the mailgateway
        through message_process. This override updates the document according to the email."""
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg_dict.get('body')) if msg_dict.get('body') else ''
        defaults = {
            'name': msg_dict.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg_dict.get('from'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('priority'):
            defaults['priority'] = msg_dict.get('priority')
        defaults.update(custom_values)
        return super().message_new(msg_dict, custom_values=defaults)

    # @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('crm.claim') or _('New')
        if vals.get('serial_number'):
            serial_no = vals.get('serial_number')
            stock_production_lot = self.env['stock.lot'].search([('name', '=', serial_no),
                                                                 ('product_id', '=', vals.get('product_id'))])
            if stock_production_lot:
                vals['start_date_warranty'] = stock_production_lot.start_date_warranty
                vals['end_date_warranty'] = stock_production_lot.end_date_warranty
                vals['start_date_sup_warranty'] = stock_production_lot.start_date_sup_warranty
                vals['end_date_sup_warranty'] = stock_production_lot.end_date_sup_warranty
                if stock_production_lot.warranty_periods in ('under_warranty', 'warranty_expired'):
                    vals['warranty_periods'] = stock_production_lot.warranty_periods
                if stock_production_lot.sup_warranty_periods in ('under_warranty', 'warranty_expired'):
                    vals['sup_warranty_periods'] = stock_production_lot.sup_warranty_periods
        new_ticket = super(CrmClaim, self).create(vals)
        return new_ticket

    @api.model
    def send_noti_digest_notification_ticket(self):
        mail_server_id = self.env['ir.mail_server'].sudo().search([], limit=1)
        template_id = self.env.ref('jt_service_management.email_noti_digest_notification_ticket')

        if not template_id:
            _logger.info('Template not found...')

        if not mail_server_id:
            raise warnings.warn("Please configure the email server!")

        if template_id:
            tickets = self.env['crm.claim'].search([('stage', 'in', ('in_diagnosis', 'diagnosed', 'waiting_for_spares'))])
            for service_center in tickets.mapped('service_center_id'):
                data = []
                for line in tickets.filtered(lambda t: t.service_center_id.id == service_center.id).details_ids.filtered(lambda x: x.product_id and x.product_id.type != 'service'):
                    sc_qty = 0
                    location_ids = self.env['stock.location'].sudo().search([('is_dxb_stock', '=', True)])
                    
                    if location_ids:
                        sc_qty = line.product_id and line.product_id.with_context(location=location_ids.ids).qty_available or 0
                        
                    data.append({
                        'ticket_number': line.new_part_id.name,
                        'product_code': line.product_id and line.product_id.default_code or "",
                        'product_name': line.product_id and line.product_id.name or "",
                        'qty_needed': line.quantity,
                        'qty_in_hand': line.product_id and line.product_id.qty_available or "",
                        'qty_sc': sc_qty,
                        'po_qty': line.po_qty,
                    })

                if data:
                    template_id.with_context(
                        list=data,
                        email_from=mail_server_id.smtp_user,
                        email_to=service_center.partner_id.email,
                        service_center=service_center,
                    ).send_mail(self.id, force_send=True)

    def send_noti_collected_ticket(self):
        mail_server_id = self.env['ir.mail_server'].sudo().search([], limit=1)
        template_id = self.env.ref('jt_service_management.email_notification_ticket_collected')

        if not template_id:
            _logger.info('Template not found...')

        if not mail_server_id:
            raise warnings.warn("Please configure the email server!")

        if template_id:
            today_date = fields.Date.today()
            tickets = self.env['crm.claim'].search([('service_center_id', '!=', False),('date_collected', '=', today_date),
                                                        ('is_send_noti_collected', '=', False)])
            for service_center in tickets.mapped('service_center_id'):
                data = []
                for ticket in tickets.filtered(lambda t: t.service_center_id.id == service_center.id):
                    partner_name = ticket.partner_id and ticket.partner_id.name or ''
                    
                    if ticket.partner_id.parent_id:
                        partner_name = ticket.partner_id.parent_id.name
                        
                    data.append({
                        'ticket_number': ticket.name,
                        'product_name': ticket.product_id and ticket.product_id.display_name or "",
                        'serial_number': ticket.serial_number or "",
                        'customer': partner_name,
                        'status': "Collected",
                    })
                    ticket.is_send_noti_collected = True

                if data:
                    template_id.with_context(
                        list=data,
                        email_from=mail_server_id.smtp_user,
                        email_to=service_center.partner_id.email,
                        service_center=service_center,
                        service_center_name=service_center.name
                    ).send_mail(self.id, force_send=True)

    def ticket_create_notification(self, template_id, email_from, all_ticket_ids, subject, ticket_message):
        service_center_ids = all_ticket_ids.mapped('service_center_id')
        for service_center_id in service_center_ids:
            service_center_ticket_ids = all_ticket_ids.filtered(lambda x: x.service_center_id.id == service_center_id.id)
            partner_ids = service_center_ticket_ids.mapped('partner_id')
            for partner in partner_ids:
                data = []
                for ticket in service_center_ticket_ids.filtered(lambda x: x.partner_id.id == partner.id):
                    partner_name = ticket.partner_id and ticket.partner_id.name or ''
                    if ticket.partner_id.parent_id:
                        partner_name = ticket.partner_id.parent_id.name
                    data.append({
                        'ticket_number': ticket.name,
                        'product_name': ticket.product_id and ticket.product_id.display_name or "",
                        'serial_number': ticket.serial_number or "",
                        'status': ticket.stage.upper(),
                        'customer': partner_name,
                        'description': ticket.description,
                        'action_taken': ticket.action_type_id and ticket.action_type_id.name or "",
                        'action_desc': ticket.cause,
                        'sale_order': ticket.sale_id and ticket.sale_id.name or "",
                    })
                    ticket.is_send_noti_created = True

                if data:
                    mail_id = template_id.with_context(
                        list=data,
                        email_from=email_from,
                        email_to=service_center_id.partner_id.email,
                        customer=partner_name,
                        street=service_center_id and service_center_id.partner_id.street or False,
                        street2=service_center_id and service_center_id.partner_id.street2 or False,
                        city=service_center_id and service_center_id.partner_id.city or False,
                        country=service_center_id.partner_id.country_id.name or False,
                        subject="Subject: " + str(service_center_id.name) + " - Ticket(s) " + subject,
                        ticket_message=ticket_message + ' ' + str(service_center_id.name) + ': ',
                        service_center=service_center_id,
                    ).sudo().send_mail(self.id, force_send=True)

    @api.model
    def send_noti_ticket_created(self):
        mail_server_id = self.env['ir.mail_server'].sudo().search([], limit=1)
        template_id = self.env.ref('jt_service_management.email_notification_ticket_created')

        if not template_id:
            _logger.info('Template not found...')

        if not mail_server_id:
            raise warnings.warn("Please configure the email server!")

        if template_id:
            from_datetime = time.strftime('%Y-%m-%d 00:00:00')
            to_datetime = time.strftime('%Y-%m-%d 23:59:59')

            # Ticket Created
            all_ticket_ids = self.env['crm.claim'].search([('date', '>=', from_datetime), ('date', '<', to_datetime), ('is_send_noti_created', '=', False)])
            self.ticket_create_notification(template_id, mail_server_id.smtp_user, all_ticket_ids, "Created", 'Service Center new ticket(s) were created at ')
            
            # Ticket Repaired 
            all_ticket_ids = self.env['crm.claim'].search([('repair_date', '>=', from_datetime), ('repair_date', '<', to_datetime), ('is_send_noti_created', '=', False)])
            self.ticket_create_notification(template_id, mail_server_id.smtp_user, all_ticket_ids, "Repaired", 'Service Center ticket(s) were Repaired at ')

            # Ticket Collected 
            from_datetime = time.strftime('%Y-%m-%d')
            to_datetime = time.strftime('%Y-%m-%d')
            all_ticket_ids = self.env['crm.claim'].search([('date_collected', '>=', from_datetime), ('date_collected', '<=', to_datetime), ('is_send_noti_created', '=', False)])
            self.ticket_create_notification(template_id, mail_server_id.smtp_user, all_ticket_ids, "Collected", 'Service Center ticket(s) were Collected at ')


class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"

    name = fields.Char(string='Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', string='Sales Team')


class ServiceCenter(models.Model):
    _name = 'service.center'
    _description = 'Service Center'

    name = fields.Char(string='Service Center', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    source_location_id = fields.Many2one('stock.location', string='Default Source Location', copy=False, required=True, domain=[('usage', '=', 'internal')])
    destination_location_id = fields.Many2one('stock.location', string='Default Destination Location', copy=False, required=True, domain=[('usage', 'in', ['internal', 'production'])]) 
    # active = fields.Boolean(string='Active', default=True)
    partner_id = fields.Many2one('res.partner', string='Address', required=True)
    sales_team_id = fields.Many2one('crm.team', string='Sales Team')
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', domain=[('code', '=', 'outgoing')])


class ServiceActionType(models.Model):
    _name = 'service.action.type'
    _description = "Service Action Type"
    
    name = fields.Char(string='Name', required=True)
