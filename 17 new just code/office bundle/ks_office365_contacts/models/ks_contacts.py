from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import requests
import json


class Contacts(models.Model):
    _inherit = "res.users"

    ks_import_office365_contact = fields.Boolean("Import Contact", default=True, readonly=True)
    ks_export_office365_contact = fields.Boolean("Export Contact", default=True, readonly=True)
    ks_sync_using_name = fields.Boolean(string='Name:', default=True, readonly=True)
    ks_sync_using_email = fields.Boolean(string='Email:', default=True, readonly=True)
    ks_sync_using_mobile = fields.Boolean(string='Mobile:')
    ks_contact_sync_days_before = fields.Integer(string="Sync contacts from last", default=1,
                                                 help="This will allow you to sync only those contacts that are created "
                                                      "or updated in the given days. Here 0 days means Today.")
    ks_contact_sync_using_days = fields.Boolean(default=True)
    ks_contact_filter_domain = fields.Char("Contact Filter Domain",
                                           help="This filter domain is only applicable while syncing "
                                                "from Odoo to office 365.")
    ks_sync_deleted_contact = fields.Boolean("Sync deleted contact", default=True)
    ks_is_manager_contacts = fields.Boolean("Is Manager", compute="_ks_is_manager_contacts", default=False)

    def _ks_is_manager_contacts(self):
        for rec in self:
            if self.env.user.has_group("ks_office365_base.office_manager_group_id"):
                rec.ks_is_manager_contacts = True
            else:
                rec.ks_is_manager_contacts = False

    def ks_get_contacts(self):
        try:
            if self.ks_contact_sync_using_days:
                _days = str(self.ks_contact_sync_days_before)
                if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
                    return self.ks_show_error_message(
                        _("Days can only be in numbers less than 999 and greater than or equal 0."))
            res = self._ks_get_contacts()
            return res
        except Exception as ex:
            if type(ex) is requests.exceptions.ConnectionError:
                ex = "Internet Connection Failed"
            self.env.cr.commit()
            ks_current_job = self.env["ks.office.job"].search([('ks_records', '>=', 0),
                                                               ('ks_status', '=', 'in_process'),
                                                               ('ks_job', '=', 'contact_import'),
                                                               ('create_uid', '=', self.env.user.id)])
            if ks_current_job:
                ks_current_job.write({'ks_status': 'error', 'ks_error_text': ex})
            self.ks_create_log("contact", "Error", "", 0, datetime.today(), "office_to_odoo",
                               False, "failed", str(ex) +
                               "\nCheck Jobs to know how many records have been processed.")
            return self.ks_has_sync_error()

    def _ks_get_contacts(self):
        ks_current_job = self.ks_is_job_completed("contact_import", "contact")
        if not ks_current_job:
            return self.ks_show_error_message(_('Process Is Already Running.'))
        else:
            ks_current_job.write({'ks_status': 'in_process', 'ks_error_text': False})

        ks_current_datatime = datetime.today()
        ks_sync_contacts_from_date = datetime.min.date().replace(year=1900)
        if self.ks_contact_sync_using_days:
            ks_days = self.ks_contact_sync_days_before
            ks_sync_contacts_from_date = ks_current_datatime.date() + relativedelta(days=-ks_days)

        ks_auth_token = self.ks_auth_token
        if not ks_auth_token:
            self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "office_to_odoo",
                               "authentication", "failed",
                               "Generate Authentication Token")
            return self.ks_show_error_message(_("Generate Authentication Token"))

        head = {
            "Authorization": ks_auth_token,
            "Host": "graph.microsoft.com"
        }

        ks_contact_imported = ks_current_job.ks_records
        ks_api_endpoint = "https://graph.microsoft.com/v1.0/me/contacts?$top=1000000&$skip=" + str(ks_contact_imported)
        ks_api_endpoint += "&$filter=lastModifiedDateTime ge " + str(ks_sync_contacts_from_date)

        ks_response = requests.get(ks_api_endpoint, headers=head)
        ks_json_data = json.loads(ks_response.text)

        # For finding duplicate contacts in office 365
        ks_all_response = requests.get("https://graph.microsoft.com/v1.0/me/contacts?$top=1000000", headers=head)
        ks_json_all_data = json.loads(ks_all_response.text)
        if 'error' in ks_json_data or 'error' in ks_json_all_data:
            if ks_json_data["error"]['code'] == 'InvalidAuthenticationToken':
                self.refresh_token()
                head['Authorization'] = self.ks_auth_token
                ks_response = requests.get(ks_api_endpoint, headers=head)
                ks_json_data = json.loads(ks_response.text)
                ks_all_response = requests.get("https://graph.microsoft.com/v1.0/me/contacts?$top=1000000",
                                               headers=head)
                ks_json_all_data = json.loads(ks_all_response.text)
                if 'error' in ks_json_data or 'error' in ks_json_all_data:
                    self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "office_to_odoo",
                                       "authentication", "failed", ks_json_data["error"]['code'])
                    return self.ks_show_error_message(
                        _("Some error occurred! \nPlease check logs for more information."))
            else:
                self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "office_to_odoo",
                                   "authentication", "failed", ks_json_data["error"]['code'])
                return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for more information."))

        ks_sync_error = False
        ks_office_contacts = ks_json_data['value']

        # All the contacts in the office365 without filters to find any duplicates present.
        ks_all_office_contacts = ks_json_all_data['value']

        ks_syncing_field = self.ks_get_contact_syncing_fields()
        if not len(ks_syncing_field):
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_show_error_message(_("Please select one of the field to sync contacts."))

        # checking duplicates in office
        ks_duplicate_office_mobiles = set()
        if "mobile" in ks_syncing_field and "name" not in ks_syncing_field and "email" not in ks_syncing_field:
            _mobiles = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not c['mobilePhone']:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime,
                                           "office_to_odoo",
                                           False, "failed",
                                           "Mobile number for the contact name \'" + ks_fullname +
                                           " \' doesn't exists in Office 365.\nNote: This contact is being synced with respect to "
                                           "mobile number.")
                        ks_sync_error = True
                else:
                    if _mobiles.count(c['mobilePhone']) == 1:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                           ks_current_datatime, "office_to_odoo", False, "failed",
                                           "Multiple contacts with the same mobile number\'" + c['mobilePhone'] +
                                           "\'(in Office 365).\nNote: This contact is being synced with respect to "
                                           "mobile number.")
                        ks_duplicate_office_mobiles.add(c['mobilePhone'])
                    _mobiles.append(c['mobilePhone'])

        ks_duplicate_office_names = set()
        if "name" in ks_syncing_field and "mobile" not in ks_syncing_field and "email" not in ks_syncing_field:
            _names = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not ks_fullname:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime, "office_to_odoo",
                                           False, "failed", _("Contact without name cannot be created"))
                if _names.count(ks_fullname) == 1:
                    self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                       ks_current_datatime, "office_to_odoo", False, "failed",
                                       "Multiple contacts for the contact name \'" + ks_fullname +
                                       "\' (in Office 365).\nNote: This contact is being synced with respect to name.")
                    ks_duplicate_office_names.add(ks_fullname)
                _names.append(ks_fullname)

        ks_duplicate_office_name_mobile_id = set()
        if "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" not in ks_syncing_field:
            _name_mobiles = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not ks_fullname:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime, "office_to_odoo",
                                           "create", "failed", _("Contact without name cannot be created"))
                elif not c['mobilePhone']:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime,
                                           "office_to_odoo", False, "failed",
                                           "Mobile number for the contact name \'" + ks_fullname +
                                           " \' doesn't exists in Office 365.\nNote: This contact is being synced with "
                                           "respect to name and mobile.")
                        ks_sync_error = True
                else:
                    if _name_mobiles.count((ks_fullname, c['mobilePhone'])) == 1:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                           ks_current_datatime, "office_to_odoo", False, "failed",
                                           "Multiple contacts with the same name\'" + ks_fullname +
                                           "\' and mobile number \'" + c['mobilePhone'] +
                                           "\'(in Office 365).\nNote: This contact is being synced with respect to "
                                           "name and mobile.")
                        for dup_c in ks_office_contacts:
                            fn = self.ks_get_full_name(dup_c['givenName'], dup_c['middleName'], dup_c['surname'])
                            if dup_c['mobilePhone'] == c['mobilePhone'] and fn == ks_fullname:
                                ks_duplicate_office_name_mobile_id.add(dup_c['id'])
                    _name_mobiles.append((ks_fullname, c['mobilePhone']))

        ks_duplicate_office_name_email_id = set()
        if "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" not in ks_syncing_field:
            _name_email = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not ks_fullname:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime, "office_to_odoo",
                                           False, "failed", _("Contact without name cannot be created"))
                elif not c['emailAddresses']:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime,
                                           "office_to_odoo",
                                           False, "failed", "Email for the contact name \'" + ks_fullname +
                                           " \' doesn't exists in Office 365.\nNote: This contact is being synced with respect to "
                                           "name and email.")
                        ks_sync_error = True
                else:
                    for a in c['emailAddresses']:
                        if _name_email.count((ks_fullname, a['address'])) == 1:
                            self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                               ks_current_datatime, "office_to_odoo", False, "failed",
                                               "Multiple contacts with the same email\'" + a[
                                                   'address'] + "\' and name \'" + ks_fullname +
                                               "\'(in Office 365).\nNote: This contact is being synced with respect to "
                                               "name and email.")
                            ks_duplicate_office_name_email_id.add(c['id'])
                        _name_email.append((ks_fullname, a['address']))

        ks_duplicate_office_mobile_email_id = set()
        if "mobile" in ks_syncing_field and "email" in ks_syncing_field and "name" not in ks_syncing_field:
            _mobile_email = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not c['emailAddresses'] or not c['mobilePhone']:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime,
                                           "office_to_odoo",
                                           False, "failed",
                                           "Email or Mobile for the contact name \'" + ks_fullname +
                                           " \' doesn't exists in Office 365.\nNote: This contact is being synced with respect to "
                                           "mobile and email.")
                        ks_sync_error = True
                else:
                    for a in c['emailAddresses']:
                        if _mobile_email.count((c['mobilePhone'], a['address'])) == 1:
                            self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                               ks_current_datatime, "office_to_odoo", False, "failed",
                                               "Multiple contacts with the same email\'" + a['address'] +
                                               "\' and mobile \'" + c['mobilePhone'] +
                                               "\'(in Office 365).\nNote: This contact is being synced with respect to "
                                               "mobile and email.")
                            ks_duplicate_office_mobile_email_id.add(c['id'])
                        _mobile_email.append((c['mobilePhone'], a['address']))

        ks_duplicate_office_name_mobile_email_id = set()
        if "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" in ks_syncing_field:
            _name_mobile_email = []
            for c in ks_all_office_contacts:
                ks_fullname = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not ks_fullname:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime, "office_to_odoo",
                                           False, "failed", _("Contact without name cannot be created"))
                elif not c['emailAddresses'] or not c['mobilePhone']:
                    if c['id'] in [k['id'] for k in ks_office_contacts]:
                        self.ks_create_log("contact", ks_fullname, c['id'], 0, ks_current_datatime,
                                           "office_to_odoo", "update", "failed",
                                           "Email or Mobile for the contact name \'" + ks_fullname +
                                           " \' doesn't exists in Office 365.\nNote: This contact is being synced "
                                           "with respect to name, mobile and email.")
                        ks_sync_error = True
                else:
                    for a in c['emailAddresses']:
                        if _name_mobile_email.count((ks_fullname, c['mobilePhone'], a['address'])) == 1:
                            self.ks_create_log("contact", ks_fullname, c['id'], 0,
                                               ks_current_datatime, "office_to_odoo", False, "failed",
                                               "Multiple contacts with the same name \'" + ks_fullname + ", email\'" +
                                               a['address'] + "\' and mobile \'" + c['mobilePhone'] +
                                               "\'(in Office 365).\nNote: This contact is being synced with respect to "
                                               "name, mobile and email.")
                            ks_duplicate_office_name_mobile_email_id.add(c['id'])
                        _name_mobile_email.append((ks_fullname, c['mobilePhone'], a['address']))

        # Checking empty fields in odoo
        ks_res_partner = self.env['res.partner'].sudo().search(
            [('is_company', '=', False), ('ks_user_id', '=', self.id), ('type', 'in', ['contact'])])
        if "name" in ks_syncing_field and "mobile" not in ks_syncing_field and "email" not in ks_syncing_field:
            ks_existing_contacts_name = ks_res_partner.mapped('name')

        ks_existing_contacts_email = []
        if "email" in ks_syncing_field and "name" not in ks_syncing_field and "mobile" not in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.email:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Email for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "email.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_email.append(ks_c.email)

        ks_existing_contacts_mobile = []
        if "mobile" in ks_syncing_field and "name" not in ks_syncing_field and "email" not in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.mobile:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Mobile number for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "mobile.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_mobile.append(ks_c.mobile)

        ks_existing_contacts_name_mobile = []
        if "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" not in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.mobile:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Mobile number for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "name and mobile.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_name_mobile.append((ks_c.name, ks_c.mobile))

        ks_existing_contacts_name_email = list()
        if "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" not in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.email:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Email for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "name and email.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_name_email.append((ks_c.name, ks_c.email))

        ks_existing_contacts_mobile_email = []
        if "mobile" in ks_syncing_field and "email" in ks_syncing_field and "name" not in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.email or not ks_c.mobile:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Mobile or Email for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "mobile and email.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_mobile_email.append((ks_c.mobile, ks_c.email))

        ks_existing_contacts_name_mobile_email = []
        if "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" in ks_syncing_field:
            for ks_c in ks_res_partner:
                if not ks_c.email or not ks_c.mobile:
                    self.ks_create_log("contact", (ks_c.name or ''), "", ks_c.id, ks_current_datatime, "office_to_odoo",
                                       "update", "failed", "Mobile or email for the contact name \'" + (ks_c.name or '') +
                                       " \' doesn't exists exists in Odoo.\nNote: This contact is being synced with respect to "
                                       "name, mobile and email.")
                    ks_sync_error = True
                else:
                    ks_existing_contacts_name_mobile_email.append((ks_c.name, ks_c.mobile, ks_c.email))

        for contact in ks_office_contacts:
            ks_contact_imported += 1

            """ Syncing deleted Contacts """
            if self.ks_sync_deleted_contact:
                is_deleted = self.ks_sync_contacts_deleted_in_odoo(contact, head)
                if is_deleted:
                    continue

            ks_contact_id = contact['id']
            ks_title = self.ks_get_contact_title(contact['title'])
            ks_state_id = None
            ks_country_id = None
            ks_other_country_id = None
            ks_other_state_id = None
            ks_business_country_id = None
            ks_business_state_id = None
            child_contacts = []
            if contact['homeAddress']:
                if contact['homeAddress'].get('state'):
                    ks_state_id = self.ks_get_state_id(contact['homeAddress']['state'], contact, 'homeAddress')
                if contact['homeAddress'].get('countryOrRegion'):
                    # ks_country_id = self.ks_get_country_id(contact['homeAddress']['countryOrRegion'])
                    ks_country_id = ks_state_id['country_id'] if ks_state_id['country_id'] else None
            if contact['otherAddress']:
                if contact['otherAddress'].get('state'):
                    ks_other_state_id = self.ks_get_state_id(contact['otherAddress']['state'], contact, 'otherAddress')
                if contact['otherAddress'].get('countryOrRegion'):
                    # ks_country_id = self.ks_get_country_id(contact['homeAddress']['countryOrRegion'])
                    ks_other_country_id = ks_other_state_id['country_id'] if ks_other_state_id['country_id'] else None
            if contact['businessAddress']:
                if contact['businessAddress'].get('state'):
                    ks_business_state_id = self.ks_get_state_id(contact['businessAddress']['state'], contact, 'businessAddress')
                if contact['businessAddress'].get('countryOrRegion'):
                    # ks_country_id = self.ks_get_country_id(contact['homeAddress']['countryOrRegion'])
                    ks_business_country_id = ks_business_state_id['country_id'] if ks_business_state_id['country_id'] else None
            ks_parent_id = self.ks_get_company(contact)
            ks_email = contact['emailAddresses'][0]['address'] if len(contact['emailAddresses']) else ""
            ks_fullname = self.ks_get_full_name(contact['givenName'], contact['middleName'], contact['surname'])
            other_child_partner = dict()
            business_child_partner = dict()
            if contact['otherAddress']:
                other_child_partner = {
                    "street": contact['otherAddress']['street'] if 'street' in contact['otherAddress'] else False,
                    "zip": contact['otherAddress']['postalCode'] if 'postalCode' in contact['otherAddress'] else False,
                    "city": contact['otherAddress']['city'] if 'city' in contact['otherAddress'] else False,
                    "state_id": ks_other_state_id.id if ks_other_state_id else None,
                    "country_id": ks_other_country_id.id if ks_other_country_id else None,
                    "type": 'other',
                    "email": ks_email,
                    "name": ks_fullname,
                }
                contact_exist = self.env['res.partner'].search([('ks_office_contact_id', '=', ks_contact_id), ("ks_user_id", '=', self.id)], limit=1)
                if contact_exist:
                    if contact_exist.child_ids:
                        for data in contact_exist.child_ids:
                            if data.type == 'other':
                                data.update(other_child_partner)
                                child_contacts.append(data.id)
                    else:
                        data = self.env['res.partner'].create(other_child_partner)
                        child_contacts.append(data.id)
                else:
                    data = self.env['res.partner'].create(other_child_partner)
                    child_contacts.append(data.id)
            if contact['businessAddress']:
                business_child_partner = {
                    "street": contact['businessAddress']['street'] if 'street' in contact['businessAddress'] else False,
                    "zip": contact['businessAddress']['postalCode'] if 'postalCode' in contact['businessAddress'] else False,
                    "city": contact['businessAddress']['city'] if 'city' in contact['businessAddress'] else False,
                    "state_id": ks_business_state_id.id if ks_business_state_id else None,
                    "country_id": ks_business_country_id.id if ks_business_country_id else None,
                    "type": 'business',
                    "email": ks_email,
                    "name": ks_fullname,
                }
                contact_exist = self.env['res.partner'].search([('ks_office_contact_id', '=', ks_contact_id), ("ks_user_id", '=', self.id)], limit=1)
                if contact_exist:
                    if contact_exist.child_ids:
                        for data in contact_exist.child_ids:
                            if data.type == 'business':
                                data.update(business_child_partner)
                                child_contacts.append(data.id)
                    else:
                        data = self.env['res.partner'].create(business_child_partner)
                        child_contacts.append(data.id)
                else:
                    data = self.env['res.partner'].create(business_child_partner)
                    child_contacts.append(data.id)
            if ks_res_partner:
                for res in ks_res_partner:
                    vals = {
                        "ks_office_contact_id": ks_contact_id,
                        "ks_user_id": self.id,
                        "title": ks_title.id if ks_title else None,
                        "name": ks_fullname,
                        "is_company": False,
                        "comment": contact['personalNotes'] or False,
                        "mobile": contact['mobilePhone'] or False,
                        "phone": contact['homePhones'][0] if len(contact['homePhones']) else False,
                        "email": ks_email or False,
                        "street": contact['homeAddress']['street'] if 'street' in contact['homeAddress'] else res.street,
                        "zip": contact['homeAddress']['postalCode'] if 'postalCode' in contact['homeAddress'] else res.zip,
                        "city": contact['homeAddress']['city'] if 'city' in contact['homeAddress'] else res.city,
                        "state_id": ks_state_id.id if ks_state_id else res.state_id.id,
                        "country_id": ks_country_id.id if ks_country_id else res.country_id.id,
                        "function": contact['jobTitle'] or False,
                        "parent_id": ks_parent_id.id if ks_parent_id else None,
                        "website": contact['businessHomePage'] or False,
                    }
                    if child_contacts:
                        vals.update({
                            'child_ids': [(6, 0, child_contacts)],
                        })
            else:
                vals = {
                    "ks_office_contact_id": ks_contact_id,
                    "ks_user_id": self.id,
                    "title": ks_title.id if ks_title else None,
                    "name": ks_fullname,
                    "is_company": False,
                    "comment": contact['personalNotes'] or False,
                    "mobile": contact['mobilePhone'] or False,
                    "phone": contact['homePhones'][0] if len(contact['homePhones']) else False,
                    "email": ks_email or False,
                    "street": contact['homeAddress']['street'] if 'street' in contact['homeAddress'] else False,
                    "zip": contact['homeAddress']['postalCode'] if 'postalCode' in contact['homeAddress'] else False,
                    "city": contact['homeAddress']['city'] if 'city' in contact['homeAddress'] else False,
                    "state_id": ks_state_id.id if ks_state_id else False,
                    "country_id": ks_country_id.id if ks_country_id else False,
                    "function": contact['jobTitle'] or False,
                    "parent_id": ks_parent_id.id if ks_parent_id else None,
                    "website": contact['businessHomePage'] or False,
                }
                if child_contacts:
                    vals.update({
                    'child_ids': [(6, 0, child_contacts)],
                    })

            ks_existing_contacts_id = self.env['res.partner'] \
                .search([('is_company', '=', False), ('ks_user_id', '=', self.id)]).mapped('ks_office_contact_id')

            if ks_contact_id in ks_existing_contacts_id:
                if "email" in ks_syncing_field and "name" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                    if not ks_email:
                        continue
                elif "mobile" in ks_syncing_field and "name" not in ks_syncing_field and "email" not in ks_syncing_field:
                    if not contact['mobilePhone'] or contact['mobilePhone'] in ks_duplicate_office_mobiles:
                        continue
                elif "name" in ks_syncing_field and "email" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                    if ks_fullname in ks_duplicate_office_names:
                        continue
                elif "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" not in ks_syncing_field:
                    if not contact['emailAddresses'][0]['address'] or \
                            contact['id'] in ks_duplicate_office_name_email_id:
                        continue
                elif "mobile" in ks_syncing_field and "email" in ks_syncing_field and "name" not in ks_syncing_field:
                    if not contact['emailAddresses'][0]['address'] or not contact['mobilePhone'] or \
                            contact['id'] in ks_duplicate_office_mobile_email_id:
                        continue
                elif "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" not in ks_syncing_field:
                    if not contact['mobilePhone'] or contact['id'] in ks_duplicate_office_name_mobile_id:
                        continue
                elif "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" in ks_syncing_field:
                    if not contact['emailAddresses'][0]['address'] or not contact['mobilePhone'] or \
                            contact['id'] in ks_duplicate_office_name_mobile_email_id:
                        continue
                ks_contact = self.env['res.partner'].sudo().search([('ks_office_contact_id', '=', ks_contact_id)])
                if len(ks_contact) > 1:
                    self.ks_create_log("contact", ks_contact.mapped('name'), ks_contact_id, ks_contact.mapped('id'),
                                       ks_current_datatime, "office_to_odoo", "update", "failed",
                                       "Multiple contacts with same office id \'" + ks_contact_id +
                                       "\' exists (in Odoo).")
                    continue
                try:
                    ks_contact.write(vals)
                    ks_current_job.write({'ks_records': ks_contact_imported})
                    self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id, ks_contact.id,
                                       ks_current_datatime, "office_to_odoo", "update", "success",
                                       "Record updated!")
                except Exception as ex:
                    self.ks_create_log("contact", ks_contact.name, ks_contact_id, ks_contact.id,
                                       ks_current_datatime, "office_to_odoo", "update", "failed", ex)
                    ks_sync_error = True

            elif "email" in ks_syncing_field and "name" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                if not ks_email:
                    continue
                if ks_email in ks_existing_contacts_email:
                    ks_contact = self.env['res.partner'].sudo().search([('email', '=', ks_email)])
                    if len(ks_contact) > 1:
                        self.ks_create_log("contact", ks_contact.name, ks_contact_id, ks_contact.id,
                                           ks_current_datatime, "office_to_odoo", "update", "failed",
                                           "Multiple contacts with same email \'" + ks_email + "\' exists (in Odoo).")
                        ks_sync_error = True
                    else:
                        ks_contact.write(vals)
                        ks_current_job.write({'ks_records': ks_contact_imported})
                        self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                           ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                           "success", "Record updated!")
                else:
                    ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                    ks_current_job.write({'ks_records': ks_contact_imported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "mobile" in ks_syncing_field and "name" not in ks_syncing_field and "email" not in ks_syncing_field:
                if not contact['mobilePhone'] or contact['mobilePhone'] in ks_duplicate_office_mobiles:
                    continue
                if contact['mobilePhone'] in ks_existing_contacts_mobile:
                    ks_contact = self.env['res.partner'].sudo().search([('mobile', '=', contact['mobilePhone'])])
                    if len(ks_contact) > 1:
                        self.ks_create_log("contact", ks_contact.name, ks_contact_id, ks_contact.id,
                                           ks_current_datatime, "office_to_odoo", "update", "failed",
                                           "Multiple contacts with same mobile \'" + contact['mobilePhone'] +
                                           "\' exists (in Odoo). \nNote: This contact is being synced "
                                           "with respect to mobile.")
                        ks_sync_error = True
                    else:
                        ks_contact.write(vals)
                        ks_current_job.write({'ks_records': ks_contact_imported})
                        self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                           ks_contact.id,
                                           ks_current_datatime, "office_to_odoo", "update", "success",
                                           "Record updated! \nNote: This contact is being synced with respect to "
                                           "mobile number.")
                else:
                    ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                    ks_current_job.write({'ks_records': ks_contact_imported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "name" in ks_syncing_field and "email" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                if not ks_fullname or ks_fullname in ks_duplicate_office_names:
                    continue
                if ks_fullname in ks_existing_contacts_name:
                    ks_contact = self.env['res.partner'].sudo().search([('name', '=', ks_fullname)])
                    if len(ks_contact) > 1:
                        self.ks_create_log("contact", ks_fullname, ks_contact_id, 0,
                                           ks_current_datatime, "office_to_odoo", "update", "failed",
                                           "Multiple contacts with same name \'" + ks_fullname +
                                           "\' exists (in Odoo). \nNote: This contact is being synced with "
                                           "respect to name.")
                        ks_sync_error = True
                    else:
                        ks_contact.write(vals)
                        ks_current_job.write({'ks_records': ks_contact_imported})
                        self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                           ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                           "success", "Record updated! \nNote: This contact is being synced with "
                                                      "respect to name.")

                else:
                    ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                    ks_current_job.write({'ks_records': ks_contact_imported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" not in ks_syncing_field:
                if not ks_fullname or not contact['emailAddresses'] or not contact['emailAddresses'][0]['address'] or \
                        contact['id'] in ks_duplicate_office_name_email_id:
                    continue
                else:
                    ks_email = contact['emailAddresses'][0]
                    if (ks_fullname, ks_email['address']) in ks_existing_contacts_name_email:
                        ks_contact = self.env['res.partner'].search(
                            [('name', '=', ks_fullname), ('email', '=', ks_email['address'])])
                        if len(ks_contact) > 1:
                            self.ks_create_log("contact", ks_fullname, ks_contact_id, 0,
                                               ks_current_datatime, "office_to_odoo", "update", "failed",
                                               "Multiple contacts with same name \'" + ks_fullname + "\' and email \'" +
                                               ks_email['address'] +
                                               "\' exists (in Odoo). \nNote: This contact is being synced with "
                                               "respect to name and email.")
                            ks_sync_error = True
                        else:
                            ks_contact.write(vals)
                            ks_current_job.write({'ks_records': ks_contact_imported})
                            self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                               ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                               "success",
                                               "Record updated! \nNote: This contact is being synced with "
                                               "respect to name and email.")
                    else:
                        ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                        ks_current_job.write({'ks_records': ks_contact_imported})
                        if ks_some_error:
                            ks_sync_error = True

            elif "mobile" in ks_syncing_field and "email" in ks_syncing_field and "name" not in ks_syncing_field:
                if not contact['emailAddresses'] or not contact['emailAddresses'][0]['address'] or \
                        not contact['mobilePhone'] or contact['id'] in ks_duplicate_office_mobile_email_id:
                    continue
                else:
                    for ks_email in contact['emailAddresses']:
                        if (contact['mobilePhone'], ks_email['address']) in ks_existing_contacts_mobile_email:
                            ks_contact = self.env['res.partner'].search(
                                [('mobile', '=', contact['mobilePhone']), ('email', '=', ks_email['address'])])
                            if len(ks_contact) > 1:
                                self.ks_create_log("contact", ks_fullname, ks_contact_id, 0,
                                                   ks_current_datatime, "office_to_odoo", "update", "failed",
                                                   "Multiple contacts with same mobile \'" + contact[
                                                       'mobilePhone'] + "\' and email \'" + ks_email['address'] +
                                                   "\' exists (in Odoo). \nNote: This contact is being synced with "
                                                   "respect to mobile and email.")
                                ks_sync_error = True
                            else:
                                ks_contact.write(vals)
                                ks_current_job.write({'ks_records': ks_contact_imported})
                                self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                                   ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                                   "success",
                                                   "Record updated! \nNote: This contact is being synced with "
                                                   "respect to mobile and email.")
                        else:
                            ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                            ks_current_job.write({'ks_records': ks_contact_imported})
                            if ks_some_error:
                                ks_sync_error = True

            elif "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" not in ks_syncing_field:
                if not ks_fullname or not contact['mobilePhone'] or contact['id'] in ks_duplicate_office_name_mobile_id:
                    continue
                elif (ks_fullname, contact['mobilePhone']) in ks_existing_contacts_name_mobile:
                    ks_contact = self.env['res.partner'].search(
                        [('name', '=', ks_fullname), ('mobile', '=', contact['mobilePhone'])])
                    if len(ks_contact) > 1:
                        self.ks_create_log("contact", ks_fullname, ks_contact_id, 0,
                                           ks_current_datatime, "office_to_odoo", "update", "failed",
                                           "Multiple contacts with same name \'" + ks_fullname + "\' and mobile \'" +
                                           contact['mobilePhone'] +
                                           "\' exists (in Odoo). \nNote: This contact is being synced with "
                                           "respect to name and mobile.")
                        ks_sync_error = True
                    else:
                        ks_contact.write(vals)
                        ks_current_job.write({'ks_records': ks_contact_imported})
                        self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                           ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                           "success",
                                           "Record updated! \nNote: This contact is being synced with "
                                           "respect to name and mobile.")
                else:
                    ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                    ks_current_job.write({'ks_records': ks_contact_imported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "name" in ks_syncing_field and "mobile" in ks_syncing_field and "email" in ks_syncing_field:
                if not ks_fullname or not contact['emailAddresses'] or not contact['emailAddresses'][0]['address'] or \
                        not contact['mobilePhone'] or contact['id'] in ks_duplicate_office_name_mobile_email_id:
                    continue
                else:
                    for ks_email in contact['emailAddresses']:
                        if (ks_fullname, contact['mobilePhone'], ks_email['address']) in \
                                ks_existing_contacts_name_mobile_email:
                            ks_contact = self.env['res.partner'].sudo().search([('mobile', '=', contact['mobilePhone']),
                                                                                ('email', '=', ks_email['address']),
                                                                                ('name', '=', ks_fullname)])
                            if len(ks_contact) > 1:
                                self.ks_create_log("contact", ks_fullname, ks_contact_id, 0,
                                                   ks_current_datatime, "office_to_odoo", "update", "failed",
                                                   "Multiple contacts with same name \'" + ks_fullname +
                                                   "\' and mobile \'" + contact['mobilePhone'] + "\' and email \'" +
                                                   ks_email[
                                                       'address'] + "\' exists (in Odoo). \nNote: This contact is "
                                                                    "being synced with respect to name, mobile and email.")
                                ks_sync_error = True
                            else:
                                ks_contact.write(vals)
                                ks_current_job.write({'ks_records': ks_contact_imported})
                                self.ks_create_log("contact", ks_contact.name, ks_contact.ks_office_contact_id,
                                                   ks_contact.id, ks_current_datatime, "office_to_odoo", "update",
                                                   "success",
                                                   "Record updated! \nNote: This contact is being synced with "
                                                   "respect to name, mobile and email.")
                        else:
                            ks_some_error = self.ks_create_new_contact(vals, ks_fullname, contact['id'])
                            ks_current_job.write({'ks_records': ks_contact_imported})
                            if ks_some_error:
                                ks_sync_error = True

        if not ks_sync_error:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_no_sync_error()
        else:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_has_sync_error()

    def ks_sync_contacts_deleted_in_odoo(self, ks_office_contact, header):
        if self.env['res.partner'].sudo().search([('ks_office_contact_id', '=', ks_office_contact['id']),
                                                  ('ks_user_id', '=', self.id)]):
            return False
        ks_del_event = self.env['ks.deleted'].sudo().search([('ks_office_id', '=', ks_office_contact['id']),
                                                             ('ks_user_id', '=', self.id)], limit=1)
        if ks_del_event:
            url = "https://graph.microsoft.com/v1.0/me/contacts/%s" % ks_office_contact['id']
            response = requests.delete(url, headers=header)
            if response.status_code == 204:
                self.ks_create_log("contact", ks_office_contact['displayName'], ks_office_contact['id'], 0,
                                   datetime.today(), "office_to_odoo", "delete", "success",
                                   _("Contact deleted from outlook Contacts"))
                return True
            else:
                self.ks_create_log("contact", ks_office_contact['displayName'], ks_office_contact['id'], 0,
                                   datetime.today(), "office_to_odoo", "delete", "failed",
                                   _("Contact not deleted from outlook Contacts \nReason: %s") %
                                   response['error']['message'])
        return False

    def ks_create_new_contact(self, vals, ks_fullname, office_id):
        ks_some_error = False
        try:
            vals.update({'ks_user_id': self.id})
            ks_cont = self.env['res.partner'].create(vals)
            self.ks_create_log("contact", ks_cont.name, ks_cont.ks_office_contact_id, ks_cont.id.__str__(),
                               datetime.today(), "office_to_odoo", "create", "success", "Record created!")
        except Exception as ex:
            self.ks_create_log("contact", ks_fullname, office_id, "0", datetime.today(), "office_to_odoo", "create",
                               "failed", "Record not created created! \nReason: " + str(ex))
            ks_some_error = True
        return ks_some_error

    def ks_get_search_domain(self, ks_domain, ks_sync_contacts_from_date):
        ks_search_domain = [('is_company', '=', False), ('ks_user_id', '=', self.id), ('type', 'not in', ['business', 'other'])]
        if ks_domain:
            for d in eval(ks_domain):
                if type(d) is list:
                    ks_search_domain.append(tuple(d))

        # res_config = self.sudo().env['res.config.settings'].search([])
        # if res_config:
        #     if res_config[-1].group_multi_company and not res_config[-1].company_share_partner:
        #         ks_search_domain.append(('company_id', '=', self.env.user.company_id.id))

        ks_search_domain.append(('write_date', '>=', ks_sync_contacts_from_date))
        return ks_search_domain

    def ks_get_contact_syncing_fields(self):
        ks_syncing_field = list()
        if self.ks_sync_using_name:
            ks_syncing_field.append("name")
        if self.ks_sync_using_mobile:
            ks_syncing_field.append("mobile")
        if self.ks_sync_using_email:
            ks_syncing_field.append("email")
        return ks_syncing_field

    def ks_post_contacts(self):
        try:
            if self.ks_contact_sync_using_days:
                _days = str(self.ks_contact_sync_days_before)
                if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
                    return self.ks_show_error_message(
                        _("Days can only be in numbers less than 999 and greater than or equal 0."))
            res = self._ks_post_contacts()
            return res
        except Exception as ex:
            if type(ex) is requests.exceptions.ConnectionError:
                ex = "Internet Connection Failed"
            self.env.cr.commit()
            ks_current_job = self.env["ks.office.job"].sudo().search([('ks_records', '>=', 0),
                                                                      ('ks_status', '=', 'in_process'),
                                                                      ('ks_job', '=', 'contact_export'),
                                                                      ('create_uid', '=', self.env.user.id)])
            if ks_current_job:
                ks_current_job.write({'ks_status': 'error', 'ks_error_text': ex})
            self.ks_create_log("contact", "Error", "", 0, datetime.today(), "odoo_to_office",
                               False, "failed", str(ex) +
                               "\nCheck Jobs to know how many records have been processed.")
            return self.ks_has_sync_error()

    def _ks_post_contacts(self):
        ks_current_job = self.ks_is_job_completed("contact_export", "contact")
        if not ks_current_job:
            return self.ks_show_error_message(_('Process Is Already Running.'))
        else:
            ks_current_job.write({'ks_status': 'in_process'})

        ks_current_datatime = datetime.today()
        ks_sync_contacts_from_date = datetime.min.date().replace(year=1900)
        if self.ks_contact_sync_using_days:
            ks_days = self.ks_contact_sync_days_before
            ks_sync_contacts_from_date = ks_current_datatime.date() + relativedelta(days=-ks_days)

        ks_api_endpoint = "https://graph.microsoft.com/v1.0/me/contacts?$top=1000000"

        ks_auth_token = self.ks_auth_token

        if not ks_auth_token:
            self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "odoo_to_office",
                               "authentication", "failed", "Generate Authentication Token")
            return self.ks_show_error_message(_("Generate Authentication Token"))

        head = {
            "Authorization": ks_auth_token,
            "Content-Type": "application/json"
        }

        ks_search_domain = self.ks_get_search_domain(self.ks_contact_filter_domain, ks_sync_contacts_from_date)

        # Contacts to be synced
        ks_odoo_contacts = self.env['res.partner'].search(ks_search_domain)

        # Contacts to verify duplicates
        ks_odoo_all_contacts = self.env['res.partner'].search(ks_search_domain[0:-1])

        ks_office_contacts = requests.get(ks_api_endpoint, headers=head)
        ks_office_contacts_json_data = json.loads(ks_office_contacts.text)

        if 'error' in ks_office_contacts_json_data:
            if ks_office_contacts_json_data["error"]['code'] == 'InvalidAuthenticationToken':
                self.refresh_token()
                head['Authorization'] = self.ks_auth_token
                ks_response = requests.get(ks_api_endpoint, headers=head)
                ks_office_contacts_json_data = json.loads(ks_response.text)
                if 'error' in ks_office_contacts_json_data:
                    self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "office_to_odoo",
                                       "authentication", "failed", ks_office_contacts_json_data["error"]['code'])
                    ks_current_job.write({'ks_status': 'completed'})
                    return self.ks_show_error_message(
                        _("Some error occurred! \nPlease check logs for more information."))
            else:
                self.ks_create_log("contact", "Authentication", "", 0, ks_current_datatime, "odoo_to_office",
                                   "authentication", "failed", ks_office_contacts_json_data["error"]['code'])
                ks_current_job.write({'ks_status': 'completed'})
                return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for more information."))

        ks_syncing_field = self.ks_get_contact_syncing_fields()
        if not len(ks_syncing_field):
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_show_error_message(_("Please select one of the field to sync contacts."))

        ks_unique_office_contacts = ks_office_contacts_json_data['value']

        # Checking for empty or duplicate fields in odoo
        ks_duplicate_odoo_name = set()
        if "name" in ks_syncing_field and "mobile" not in ks_syncing_field and "email" not in ks_syncing_field:
            _name = [c.name for c in ks_odoo_all_contacts]
            for n in _name:
                if _name.count(n) > 1:
                    ks_duplicate_odoo_name.add(n)

            for n in ks_duplicate_odoo_name:
                self.ks_create_log("contact", n, "", 0, ks_current_datatime, "odoo_to_office", False, "failed",
                                   "Multiple contacts with same name \'" + n + "\' exists (in Odoo).\nNote: This contact "
                                                                               "is being synced with respect to name.")

        ks_duplicate_odoo_email = set()
        if "email" in ks_syncing_field and "mobile" not in ks_syncing_field and "name" not in ks_syncing_field:
            _email = []
            for c in ks_odoo_all_contacts:
                if not c.email:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Email for the contact name \'" + c.name +
                                           "\' doesn't exists exists in Odoo.\nNote: This contact is being synced with "
                                           "respect to email.")
                else:
                    if _email.count(c.email) == 1:
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed", "Multiple contacts with same email \'"
                                           + c.email + "\' exists (in Odoo). \nNote: This contact is being synced "
                                                       "with respect to Email Address.")
                    _email.append(c.email)
            for e in _email:
                if _email.count(e) > 1:
                    ks_duplicate_odoo_email.add(e)

        ks_duplicate_odoo_mobile = set()
        if "mobile" in ks_syncing_field and "email" not in ks_syncing_field and "name" not in ks_syncing_field:
            _mobile = []
            for c in ks_odoo_all_contacts:
                if not c.mobile:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Mobile number for the contact name \'" + c.name +
                                           "\' doesn't exists exists in Odoo. \nNote: This contact is being synced "
                                           "with respect to mobile number.")
                else:
                    if _mobile.count(c.mobile) == 1:
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Multiple contacts with same mobile number \'"
                                           + c.mobile + "\' exists (in Odoo). \nNote: This contact is being synced with respect to mobile number.")
                    _mobile.append(c.mobile)

            for m in _mobile:
                if _mobile.count(m) > 1:
                    ks_duplicate_odoo_mobile.add(m)

        ks_duplicate_odoo_email_mobile_id = list()
        if "email" in ks_syncing_field and "mobile" in ks_syncing_field and "name" not in ks_syncing_field:
            _email_mobile = []
            for c in ks_odoo_all_contacts:
                if not c.email or not c.mobile:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Email or Mobile for the contact name \'" + c.name +
                                           "\' doesn't exists exists (in Odoo).\nNote: This contact is being synced with "
                                           "respect to email and mobile.")
                else:
                    if _email_mobile.count((c.mobile, c.email)) == 1:
                        _dup = self.env['res.partner'].sudo().search(
                            [('email', '=', c.email), ('mobile', '=', c.mobile)])
                        _all_names = str()
                        for ks_c in _dup:
                            _all_names += ks_c.name + ", "
                        self.ks_create_log("contact", _all_names[:-2], c.ks_office_contact_id, c.id,
                                           ks_current_datatime,
                                           "odoo_to_office", False, "failed", "Multiple contacts with same email \'"
                                           + c.email + "\' & Mobile \'" + c.mobile + "\' exists (in Odoo). \nNote: This contact is being synced "
                                                                                     "with respect to email and mobile.")
                        ks_duplicate_odoo_email_mobile_id.extend(_dup.ids)
                    _email_mobile.append((c.mobile, c.email))

        ks_duplicate_odoo_email_name_id = list()
        if "email" in ks_syncing_field and "name" in ks_syncing_field and "mobile" not in ks_syncing_field:
            _email_name = []
            for c in ks_odoo_all_contacts:
                if not c.email or not c.name:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Email for the contact name \'" + c.name +
                                           "\' doesn't exists exists (in Odoo).\nNote: This contact is being synced with "
                                           "respect to name and email.")
                else:
                    if _email_name.count((c.email, c.name)) == 1:
                        _dup = self.env['res.partner'].sudo().search([('name', '=', c.name), ('email', '=', c.email)])
                        _all_names = str()
                        for ks_c in _dup:
                            _all_names += ks_c.name + ", "
                        self.ks_create_log("contact", _all_names[:-2], c.ks_office_contact_id, c.id,
                                           ks_current_datatime,
                                           "odoo_to_office", False, "failed", "Multiple contacts with same Name \'"
                                           + c.name + "\' & Email \'" + c.email + "\' exists (in Odoo). \nNote: This contact is being synced "
                                                                                  "with respect to name and mobile.")
                        ks_duplicate_odoo_email_name_id.extend(_dup.ids)
                    _email_name.append((c.email, c.name))

        ks_duplicate_odoo_mobile_name_id = list()
        if "mobile" in ks_syncing_field and "name" in ks_syncing_field and "email" not in ks_syncing_field:
            _mobile_name = []
            for c in ks_odoo_all_contacts:
                if not c.mobile or not c.name:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Name or Mobile for the contact name \'" + c.name +
                                           "\' doesn't exists exists (in Odoo).\nNote: This contact is being synced with "
                                           "respect to name and mobile.")
                else:
                    if _mobile_name.count((c.mobile, c.name)) == 1:
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id,
                                           ks_current_datatime,
                                           "odoo_to_office", False, "failed", "Multiple contacts with same Name \'"
                                           + c.name + "\' & Mobile \'" + c.mobile + "\' exists (in Odoo). \nNote: This contact is being synced "
                                                                                    "with respect to name and mobile.")
                        ks_duplicate_odoo_mobile_name_id.extend(_dup.ids)
                    _mobile_name.append((c.mobile, c.name))

        ks_duplicate_odoo_name_email_mobile_id = list()
        if "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" in ks_syncing_field:
            _name_email_mobile = []
            for c in ks_odoo_all_contacts:
                if not c.mobile or not c.name or not c.email:
                    if c.id in ks_odoo_contacts.mapped('id'):
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id, ks_current_datatime,
                                           "odoo_to_office", False, "failed",
                                           "Name, Email or Mobile for the contact name \'" + c.name +
                                           "\' doesn't exists exists (in Odoo).\nNote: This contact is being synced with "
                                           "respect to name, email and mobile.")
                else:
                    if _name_email_mobile.count((c.name, c.email, c.mobile)) == 1:
                        _dup = self.env['res.partner'].search(
                            [('name', '=', c.name), ('email', '=', c.email), ('mobile', '=', c.mobile)])
                        _all_names = str()
                        self.ks_create_log("contact", c.name, c.ks_office_contact_id, c.id,
                                           ks_current_datatime, "odoo_to_office", False, "failed",
                                           "Multiple contacts with same Name \'" + c.name + "\',  Email \'" + c.email +
                                           "\' & Mobile \'" + c.mobile + "\' exists (in Odoo). \nNote: This contact is "
                                                                         "being synced with respect to name, email and mobile.")
                        ks_duplicate_odoo_name_email_mobile_id.extend(_dup.ids)
                    _name_email_mobile.append((c.name, c.email, c.mobile))

        ks_office_contacts_name = []
        ks_office_contacts_mobile = []
        ks_office_contacts_email = []
        ks_office_contacts_name_mobile = []
        ks_office_contacts_name_email = []
        ks_office_contacts_mobile_email = []
        ks_office_contacts_name_mobile_email = []

        # Checking for empty fields in office
        for c in ks_unique_office_contacts:
            if "name" in ks_syncing_field and "mobile" not in ks_syncing_field and "email" not in ks_syncing_field:
                if c['surname']:
                    if c['middleName']:
                        ks_office_contacts_name.append(
                            c['givenName'] + " " + c['middleName'] + " " + c['surname'])
                    else:
                        ks_office_contacts_name.append(c['givenName'] + " " + c['surname'])
                else:
                    ks_office_contacts_name.append(c['givenName'])

            elif "email" in ks_syncing_field and "mobile" not in ks_syncing_field and "name" not in ks_syncing_field:
                if not len(c['emailAddresses']):
                    ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Email for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to email.")
                else:
                    for a in c['emailAddresses']:
                        ks_office_contacts_email.append(a['address'])

            elif "mobile" in ks_syncing_field and "email" not in ks_syncing_field and "name" not in ks_syncing_field:
                if not c['mobilePhone']:
                    ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Mobile number for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to mobile number.")
                else:
                    ks_office_contacts_mobile.append(c['mobilePhone'])

            elif "email" in ks_syncing_field and "mobile" in ks_syncing_field and "name" not in ks_syncing_field:
                if not c['mobilePhone'] or not len(c['emailAddresses']):
                    ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Mobile or Email for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to mobile and email.")
                else:
                    for a in c['emailAddresses']:
                        ks_office_contacts_mobile_email.append((c['mobilePhone'], a['address']))

            elif "email" in ks_syncing_field and "name" in ks_syncing_field and "mobile" not in ks_syncing_field:
                ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not len(c['emailAddresses']):
                    # if not contact.ks_office_contact_id:
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Email for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to email and name.")
                else:
                    for a in c['emailAddresses']:
                        ks_office_contacts_name_email.append((ks_fn, a['address']))

            elif "mobile" in ks_syncing_field and "name" in ks_syncing_field and "email" not in ks_syncing_field:
                ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not c['mobilePhone']:
                    # if not contact.ks_office_contact_id:
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Mobile for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to name and mobile.")
                else:
                    ks_office_contacts_name_mobile.append((ks_fn, c['mobilePhone']))

            elif "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" in ks_syncing_field:
                ks_fn = self.ks_get_full_name(c['givenName'], c['middleName'], c['surname'])
                if not c['mobilePhone'] or not len(c['emailAddresses']):
                    # if not contact.ks_office_contact_id:
                    self.ks_create_log("contact", ks_fn, c['id'], 0, ks_current_datatime, "odoo_to_office",
                                       False, "failed", "Mobile or Email for the contact name \'" + ks_fn +
                                       "\' doesn't exists exists in Office365. \nNote: This contact is being "
                                       "synced with respect to name, mobile and email.")
                else:
                    for a in c['emailAddresses']:
                        ks_office_contacts_name_mobile_email.append((ks_fn, c['mobilePhone'], a['address']))

        ks_sync_error = False

        ks_contact_exported = ks_current_job.ks_records
        for contact in ks_odoo_contacts[ks_contact_exported:]:
            ks_contact_exported += 1
            ks_home_address = {
                "city": contact.city if contact.city else "",
                "street": contact.street + "," + contact.street2 if contact.street2 else contact.street if contact.street else "",
                "countryOrRegion": contact.country_id.name if contact.country_id.name else "",
                "postalCode": contact.zip if contact.zip else "",
                "state": contact.state_id.name if contact.state_id.name else ""
            }
            ks_business_address = dict()
            ks_other_address = dict()
            if contact.child_ids:
                for childs in contact.child_ids:
                    if childs.type == 'other':
                        ks_other_address = {
                            "city": childs.city if childs.city else "",
                            "street": childs.street + "," + childs.street2 if childs.street2 else childs.street if contact.street else "",
                            "countryOrRegion": childs.country_id.name if childs.country_id.name else "",
                            "postalCode": childs.zip if childs.zip else "",
                            "state": childs.state_id.name if childs.state_id.name else ""
                        }
                    if childs.type == 'business':
                        ks_business_address = {
                            "city": childs.city if childs.city else "",
                            "street": childs.street + "," + childs.street2 if childs.street2 else childs.street if contact.street else "",
                            "countryOrRegion": childs.country_id.name if childs.country_id.name else "",
                            "postalCode": childs.zip if childs.zip else "",
                            "state": childs.state_id.name if childs.state_id.name else ""
                        }
            ks_fullname = contact.name.split(' ')
            ks_email_addresses = [{
                "address": contact.email if contact.email else "",
                "name": contact.name
            }]
            ks_bussiness_address = dict()
            # if contact.parent_id:
            #     ks_bussiness_address = {
            #         "city": contact.parent_id.city if contact.parent_id.city else "",
            #         "street": contact.parent_id.street + "," + contact.parent_id.street2 if contact.parent_id.street2
            #         else contact.parent_id.street if contact.parent_id.street else "",
            #         "countryOrRegion": contact.parent_id.country_id.name if contact.parent_id.country_id.name else "",
            #         "postalCode": contact.parent_id.zip if contact.parent_id.zip else "",
            #         "state": contact.parent_id.state_id.name if contact.parent_id.state_id.name else ""
            #     }
            #     ks_home_address = {}

            ks_data = {
                "title": contact.title.name if contact.title.name else "",
                "givenName": ks_fullname[0],
                "middleName": self.ks_get_middle_name(ks_fullname),
                "surname": ks_fullname[-1] if len(ks_fullname) > 1 else "",
                "mobilePhone": contact.mobile if contact.mobile else "",
                "personalNotes": contact.comment if contact.comment else "",
                "homeAddress": ks_home_address,
                "homePhones": [contact.phone] if contact.phone else [],
                "businessAddress": ks_business_address,
                "otherAddress": ks_other_address,
                "jobTitle": contact.function if contact.function else "",
                "companyName": contact.parent_id.name if contact.parent_id else "",
                "emailAddresses": ks_email_addresses,
                "businessHomePage": contact.website if contact.website else "",
            }

            if contact.ks_office_contact_id != "":
                if 'name' in ks_syncing_field and 'mobile' not in ks_syncing_field and 'email' not in ks_syncing_field:
                    if contact.name in ks_duplicate_odoo_name:
                        continue
                elif 'mobile' in ks_syncing_field and 'name' not in ks_syncing_field and 'email' not in ks_syncing_field:
                    if not contact.mobile or contact.mobile in ks_duplicate_odoo_mobile:
                        continue
                elif 'email' in ks_syncing_field and 'mobile' not in ks_syncing_field and 'name' not in ks_syncing_field:
                    if not contact.email or contact.email in ks_duplicate_odoo_email:
                        continue
                elif 'name' and 'email' in ks_syncing_field and 'mobile' not in ks_syncing_field:
                    if not contact.email or not contact.name or contact.id in ks_duplicate_odoo_email_name_id:
                        continue
                elif 'name' and 'mobile' in ks_syncing_field and 'email' not in ks_syncing_field:
                    if not contact.mobile or not contact.name or contact.id in ks_duplicate_odoo_mobile_name_id:
                        continue
                elif 'mobile' and 'email' in ks_syncing_field and 'name' not in ks_syncing_field:
                    if not contact.email or not contact.mobile or contact.id in ks_duplicate_odoo_email_mobile_id:
                        continue
                elif 'name' and 'mobile' and 'email' in ks_syncing_field:
                    if not contact.email or not contact.mobile or contact.id in ks_duplicate_odoo_name_email_mobile_id:
                        continue
                office_id = contact.ks_office_contact_id
                ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                ks_current_job.write({'ks_records': ks_contact_exported})
                if ks_some_error:
                    ks_sync_error = True

            elif "email" in ks_syncing_field and "name" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                if not contact.email or contact.email in ks_duplicate_odoo_email:
                    continue
                elif contact.email in ks_office_contacts_email:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        if len(con['emailAddresses']):
                            for add in con['emailAddresses']:
                                if add['address'] == contact.email:
                                    ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same email \'" + contact.email +
                                           "\' exists (in Office 365). \nNote: This contact is being synced with "
                                           "respect to email address.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "mobile" in ks_syncing_field and "name" not in ks_syncing_field and "email" not in ks_syncing_field:
                if not contact.mobile or contact.mobile in ks_duplicate_odoo_mobile:
                    continue
                elif contact.mobile in ks_office_contacts_mobile:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        if con['mobilePhone'] == contact.mobile:
                            ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same mobile number \'" + contact.mobile +
                                           "\' exists (in Office 365). \nNote: This contact is being synced with "
                                           "respect to mobile number.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "name" in ks_syncing_field and "email" not in ks_syncing_field and "mobile" not in ks_syncing_field:
                if contact.name in ks_duplicate_odoo_name:
                    continue
                elif contact.name in ks_office_contacts_name:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        if con['givenName'] == contact.name:
                            ks_office_contact_id.append(con['id'])
                        elif con['surname'] and not con['middleName']:
                            if (con['givenName'] + ' ' + con['surname']) == contact.name:
                                ks_office_contact_id.append(con['id'])
                        elif con['middleName'] and not con['surname']:
                            if (con['givenName'] + ' ' + con['middleName']) == contact.name:
                                ks_office_contact_id.append(con['id'])
                        elif con['middleName']:
                            if (con['givenName'] + ' ' + con['middleName'] + ' ' + con['surname']) == contact.name:
                                ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same name \'" + contact.name +
                                           "\' exists (in Office 365). \nNote: This contact is being synced with "
                                           "respect to name.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "email" in ks_syncing_field and "mobile" in ks_syncing_field and "name" not in ks_syncing_field:
                if not contact.email or not contact.mobile or contact.id in ks_duplicate_odoo_email_mobile_id:
                    continue
                elif (contact.mobile, contact.email) in ks_office_contacts_mobile_email:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        if len(con['emailAddresses']):
                            for add in con['emailAddresses']:
                                if add['address'] == contact.email and con['mobilePhone'] == contact.mobile:
                                    ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same email \'" + contact.email +
                                           "\' and mobile number \'" + contact.mobile + "exists (in Office 365). "
                                                                                        "\nNote: This contact is "
                                                                                        "being synced with "
                                                                                        "respect to email and mobile.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "email" in ks_syncing_field and "name" in ks_syncing_field and "mobile" not in ks_syncing_field:
                if not contact.email or not contact.name or contact.id in ks_duplicate_odoo_email_name_id:
                    continue
                elif (contact.name, contact.email) in ks_office_contacts_name_email:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        ks_fn = self.ks_get_full_name(con['givenName'], con['middleName'], con['surname'])
                        if len(con['emailAddresses']):
                            for add in con['emailAddresses']:
                                if add['address'] == contact.email and ks_fn == contact.name:
                                    ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same email \'" + contact.email +
                                           "\' and mobile number \'" + contact.mobile + "exists (in Office 365). "
                                                                                        "\nNote: This contact is "
                                                                                        "being synced with "
                                                                                        "respect to email and name.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "mobile" in ks_syncing_field and "name" in ks_syncing_field and "email" not in ks_syncing_field:
                if not contact.mobile or not contact.name or contact.id in ks_duplicate_odoo_mobile_name_id:
                    continue
                elif (contact.name, contact.mobile) in ks_office_contacts_name_mobile:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        ks_fn = self.ks_get_full_name(con['givenName'], con['middleName'], con['surname'])
                        if con['mobilePhone']:
                            if con['mobilePhone'] == contact.mobile and ks_fn == contact.name:
                                ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same name \'" + contact.name +
                                           "\' and mobile number \'" + contact.mobile + "\'exists (in Office 365). "
                                                                                        "\nNote: This contact is "
                                                                                        "being synced with "
                                                                                        "respect to mobile and name.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

            elif "name" in ks_syncing_field and "email" in ks_syncing_field and "mobile" in ks_syncing_field:
                if not contact.email or not contact.mobile or contact.id in ks_duplicate_odoo_name_email_mobile_id:
                    continue
                elif (contact.name, contact.mobile, contact.email) in ks_office_contacts_name_mobile_email:
                    ks_office_contact_id = []
                    for con in ks_unique_office_contacts:
                        ks_fn = self.ks_get_full_name(con['givenName'], con['middleName'], con['surname'])
                        if len(con['emailAddresses']):
                            for add in con['emailAddresses']:
                                if add['address'] == contact.email and \
                                        con['mobilePhone'] == contact.mobile and \
                                        ks_fn == contact.name:
                                    ks_office_contact_id.append(con['id'])

                    if len(ks_office_contact_id) > 1:
                        self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id,
                                           ks_current_datatime, "odoo_to_office", "update", "failed",
                                           "Multiple contacts with same email \'" + contact.email +
                                           "\' and mobile number \'" + contact.mobile + "exists (in Office 365). "
                                                                                        "\nNote: This contact is "
                                                                                        "being synced with "
                                                                                        "respect to email address.")
                        continue
                    elif len(ks_office_contact_id):
                        office_id = ks_office_contact_id[0]
                        ks_some_error = self.ks_update_office_contact(office_id, contact, ks_data, head)
                        ks_current_job.write({'ks_records': ks_contact_exported})
                        if ks_some_error:
                            ks_sync_error = True
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    ks_current_job.write({'ks_records': ks_contact_exported})
                    if ks_some_error:
                        ks_sync_error = True

        if not ks_sync_error:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_no_sync_error()
        else:
            ks_current_job.write({'ks_status': 'completed'})
            return self.ks_has_sync_error()

    def ks_update_office_contact(self, office_id, contact, ks_data, head):
        ks_some_error = False
        ks_api_endpoint = "https://graph.microsoft.com/v1.0/me/contacts/" + office_id
        ks_response = requests.patch(ks_api_endpoint, headers=head, json=ks_data)
        ks_json_data = json.loads(ks_response.text)
        if 'error' in ks_json_data:
            if ks_response.status_code == 404:
                if self.ks_sync_deleted_contact:
                    del_event = {"name": contact.name, "office_id": contact.ks_office_contact_id, "id": contact.id}
                    try:
                        contact.unlink()
                        self.ks_create_log("contact", del_event['name'], del_event["office_id"], del_event["id"],
                                           datetime.today(), "odoo_to_office", "delete", "success",
                                           _("Contact deleted from Odoo Contacts"))
                    except Exception as ex:
                        self.ks_create_log("contact", del_event['name'], del_event["ks_office_event_id"],
                                           del_event["id"], datetime.today(), "odoo_to_office", "delete",
                                           "failed",
                                           _("Record not be deleted from ODOO Contacts \nReason: %s" % ex))
                else:
                    ks_some_error = self.ks_create_office_contact(head, ks_data, contact)
                    if ks_some_error:
                        ks_some_error = True
            elif 'code' in ks_json_data['error']:
                self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                                   datetime.today(), "odoo_to_office", "create", "failed",
                                   ks_json_data['error']['code'] + "\n" + ks_json_data['error']['message'])
                ks_some_error = True
            else:
                self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                                   datetime.today(), "odoo_to_office", "create", "failed",
                                   ks_json_data['error']['message'])
                ks_some_error = True
        else:
            contact.write({'ks_office_contact_id': office_id})
            self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                               datetime.today(), "odoo_to_office", "update", "success", "Record updated!")

        return ks_some_error

    def ks_create_office_contact(self, head, ks_data, contact):
        ks_some_error = False
        ks_api_endpoint = "https://graph.microsoft.com/v1.0/me/contacts"
        ks_response = requests.post(ks_api_endpoint, headers=head, json=ks_data)
        ks_json_data = json.loads(ks_response.text)
        if 'error' in ks_json_data:
            if 'code' in ks_json_data['error']:
                ks_error = ks_json_data['error']['code'] + "\n" + ks_json_data['error']['message']
            else:
                ks_error = ks_json_data['error']['message']
            self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                               datetime.today(), "odoo_to_office", "create", "failed", ks_error)
            ks_some_error = True
        else:
            try:
                contact.write({"ks_office_contact_id": ks_json_data['id']})
                self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                                   datetime.today(), "odoo_to_office", "create", "success",
                                   "Record created!")
            except Exception as ex:
                self.ks_create_log("contact", contact.name, contact.ks_office_contact_id, contact.id.__str__(),
                                   datetime.today(), "odoo_to_office", "create", "failed",
                                   "Could not assign ks_event ID while syncing.")
                ks_some_error = True

        return ks_some_error

    def ks_get_middle_name(self, ks_fullname):
        ks_middlename = None
        if len(ks_fullname) > 3:
            for n in ks_fullname[1:len(ks_fullname) - 1]:
                if not ks_middlename:
                    ks_middlename = n
                else:
                    ks_middlename += " " + n
        elif len(ks_fullname) == 3:
            ks_middlename = ks_fullname[1]
        return ks_middlename

    def ks_get_full_name(self, fn, mn, ln):
        if mn and ln:
            ks_fullname = fn + " " + mn + " " + ln
        elif fn and ln:
            ks_fullname = fn + " " + ln
        elif fn:
            ks_fullname = fn
        else:
            ks_fullname = ""
        return ks_fullname

    def ks_get_company(self, contact):
        if contact.get('companyName'):
            company = self.env['res.partner'].search(
                [('is_company', '=', True), ('name', '=', contact.get('companyName'))], limit=1)
            if not company:
                if contact.get('businessAddress'):
                    _state = None
                    _country = None
                    if contact['businessAddress'].get('state'):
                        _state = self.ks_get_state_id(contact['businessAddress']['state'], contact, 'businessAddress')
                    # if contact['businessAddress'].get('countryOrRegion'):
                    #     _country = self.ks_get_country_id(contact['businessAddress']['countryOrRegion'])
                    company = self.env['res.partner'].create({
                        'name': contact.get('companyName'),
                        'company_type': 'company',
                        'street': contact['businessAddress']['street'],
                        'city': contact['businessAddress']['city'],
                        'state_id': _state.id if _state else None,
                        'country_id': _state['country_id'].id if (_state and _state['country_id']) else None,
                        'zip': contact['businessAddress']['postalCode'] if 'postalCode' in contact[
                            'businessAddress'] else False,
                    })
                else:
                    company = self.env['res.partner'].create({
                        'name': contact.get('companyName'),
                        'company_type': 'company',
                    })
            else:
                if contact.get('businessAddress'):
                    _state = None
                    _country = None
                    if contact['businessAddress'].get('state'):
                        _state = self.ks_get_state_id(contact['businessAddress']['state'], contact, 'businessAddress')
                    # if contact['businessAddress'].get('countryOrRegion'):
                    #     _country = self.ks_get_country_id(contact['businessAddress']['countryOrRegion'])
                    company.update({
                        'street': contact['businessAddress']['street'],
                        'city': contact['businessAddress']['city'],
                        'state_id': _state.id if _state else None,
                        'country_id': _state['country_id'].id if (_state and _state['country_id']) else None,
                        'zip': contact['businessAddress']['postalCode'] if 'postalCode' in contact[
                            'businessAddress'] else False,
                    })
                else:
                    company.update({
                        'name': contact.get('companyName'),
                        'company_type': 'company',
                    })
            return company
        return None

    def ks_get_country_id(self, country_name):
        country = None
        for c in self.env['res.country'].sudo().search([]).mapped('name'):
            if country_name.lower() == c.lower():
                country = self.env['res.country'].sudo().search([('name', '=', country_name.title())])
        return country

    def ks_get_state_id(self, state_name, contact, addr):
        state = None
        available_states = self.env['res.country.state'].sudo().search([]).mapped('name')
        available_countries = self.env['res.country'].sudo().search([]).mapped('name')
        if state_name in available_states:
            state = self.env['res.country.state'].sudo().search([('name', '=', state_name)], limit=1)
        else:
            if contact[addr].get('countryOrRegion'):
                country_name = contact[addr]['countryOrRegion']
                home_state_name = contact[addr]['state']
                code = home_state_name + '01'
                state_code = code.upper()
                if country_name in available_countries:
                    country = self.env['res.country'].search([('name', '=', country_name)])
                    state = self.env['res.country.state'].create(
                        {"name": home_state_name, "code": state_code, "country_id": country.id})
                else:
                    c_code = country_name + '01'
                    country_code = c_code.upper()
                    country = self.env['res.country'].create({"name": country_name, "code": country_code})
                    state = self.env['res.country.state'].create(
                        {"name": home_state_name, "code": state_code, "country_id": country.id})
            if contact.get('companyName'):
                if contact['businessAddress'].get('countryOrRegion'):
                    country_name = contact['businessAddress']['countryOrRegion']
                    business_state_name = contact['businessAddress']['state']
                    code = business_state_name + '01'
                    state_code = code.upper()
                    if country_name in available_countries:
                        country = self.env['res.country'].sudo().search([('name', '=', country_name)])
                        state_exist = self.env['res.country.state'].search([('country_id', '=', country.id), ("code", '=', state_code)])
                        if not state_exist:
                            state = self.env['res.country.state'].create(
                                {"name": business_state_name, "code": state_code, "country_id": country.id})
                        else:
                            state = state_exist
                    else:
                        c_code = country_name + '01'
                        country_code = c_code.upper()
                        country = self.env['res.country'].create({"name": country_name, "code": country_code})
                        state = self.env['res.country.state'].create(
                            {"name": business_state_name, "code": state_code, "country_id": country.id})
        return state

    def ks_get_phone_numbers(self, phones):
        phone_nos = ""
        for p in phones:
            if phone_nos is "":
                phone_nos = p
            else:
                phone_nos += "," + p
        return phone_nos

    def ks_get_contact_title(self, t):
        ks_available_titles = self.env['res.partner.title'].sudo().search([]).mapped('name')
        ks_available_titles_shortcut = self.env['res.partner.title'].sudo().search([]).mapped('shortcut')
        title = None
        if t:
            if t in ks_available_titles:
                title = self.env['res.partner.title'].sudo().search([('name', '=', t)])
            elif t in ks_available_titles_shortcut:
                title = self.env['res.partner.title'].sudo().search([('shortcut', '=', t)])
            else:
                title = self.env['res.partner.title'].create({"name": t})
        return title

    def ks_has_sync_error(self):
        return {
            'params': {
                'task': 'notify',
                'message': 'Sync Completed!\n Some events could not be synced. \nPlease check log for more information.',
            },
        }

    def ks_no_sync_error(self):
        return {
            'name': 'Office365 logs',
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ks_office365.logs',
            'view_id': False,
            'context': self.env.context,
        }

    def ks_show_error_message(self, message):
        return {
            'params': {
                'task': 'warn',
                'message': message,
            },
        }


class CountryCode(models.Model):
    _inherit = 'res.country'

    code = fields.Char(size=128)
