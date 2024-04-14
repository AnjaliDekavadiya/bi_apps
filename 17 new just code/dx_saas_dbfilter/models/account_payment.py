from odoo import fields, models, api
import re
from dateutil.relativedelta import relativedelta


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    def is_english(self, s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def generate_domain(self, domain_start, domain):
        check = False
        index = 0
        while check is False:
            if index > 0:
                final_domain = domain_start + str(index) + "." + domain
            else:
                final_domain = domain_start + "." + domain
            check_domain = self.env["dx.saas.dbfilter.subscriptions"].search([("domain", "=", final_domain)])
            if check_domain:
                index = index + 1
            else:
                check = True
                return final_domain

    def action_post(self):
        if self.payment_transaction_id.sale_order_ids:
            for sale_order in self.payment_transaction_id.sale_order_ids:
                for sale_order_line in sale_order.order_line:
                    if sale_order_line.product_id.saas_package:
                        if self.partner_id.company_name and self.is_english(self.partner_id.company_name):
                            domain_start = self.partner_id.company_name
                        elif self.partner_id.name and self.is_english(self.partner_id.name):
                            domain_start = self.partner_id.name
                        else:
                            if "@" in self.partner_id.email:
                                domain_start = self.partner_id.email.split("@")[0]
                            else:
                                domain_start = self.env["ir.config_parameter"].sudo().get_param(
                                    "dx_saas_dbfilter.saas_client_domain_start", "saasclient")
                        domain_start = re.sub(r"[^a-zA-Z0-9]", "", domain_start).lower()
                        domain = self.generate_domain(domain_start,
                                                      sale_order_line.product_id.saas_server.domain_for_new_sub)
                        enable_ssl = self.env["ir.config_parameter"].sudo().get_param(
                            "dx_saas_dbfilter.create_ssl_for_website_purchases", False)
                        sub = self.env["dx.saas.dbfilter.subscriptions"].create({
                            "client_id": self.partner_id.id,
                            "server_id": sale_order_line.product_id.saas_server.id,
                            "domain": domain,
                            "packages_id": sale_order_line.product_id.saas_package,
                            "start_date": sale_order.date_order,
                            "end_date": sale_order.date_order + relativedelta(
                                days=sale_order_line.product_id.saas_valid_for),
                            "users_count": sale_order_line.product_id.saas_users,
                            "login": self.partner_id.email or False,
                            "use_ssl": enable_ssl,
                        })
                        sub.state = "confirm"
                        sub.name = self.env["ir.sequence"].next_by_code("dx.saas.subscription")
                        sub.action_create_client_db()
        return super(AccountPayment, self).action_post()
