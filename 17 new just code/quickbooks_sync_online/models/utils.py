# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, _
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tools import unsafe_eval
from odoo.service.model import PG_CONCURRENCY_ERRORS_TO_RETRY

from functools import wraps
from itertools import combinations
from collections import defaultdict, Counter, namedtuple
from decimal import Decimal
import logging

_logger = logging.getLogger(__name__)

try:
    from psycopg2 import OperationalError
    from intuitlib.exceptions import AuthClientError
    from quickbooks.exceptions import QuickbooksException, AuthorizationException
except (ImportError, IOError) as ex:
    _logger.error(ex)


COMPANY_FIELDS_TO_RESET = {
    'qbo_auth_url': False,
    'qbo_csrf_token': False,
    'is_authorized': False,
    'is_authenticated': False,
}
MAPPING_MENUS = {
    'account.tax': '[QuickBooks Online --> Mapping --> Taxes]',
    'account.account': '[QuickBooks Online --> Mapping --> Accounts]',
    'account.journal': '[QuickBooks Online --> Mapping --> Payment Methods]',
    'account.payment.term': '[QuickBooks Online --> Mapping --> Payment Terms]',
}
TAXABLE, NON_TAXABLE = 'TAX', 'NON'
# Product/service marked exempt by its seller (seller accepts full responsibility)
TAX_EXEMPT_LIST = (
    'EUC-99990101-V1-00020000',
    'EUC-99990201-V1-00020000',
)


class IntuitResponse:

    SUCCESS = 0
    GENERAL_ERROR = 1
    MISC_ERROR = 2
    DUPLICATE_NAME = 6240
    INTUIT_TWIN = 62401
    ODOO_TWIN = 62402
    ERROR_HINTS = {
        6240: _(
            '\n- Another "%s" is already using this name in QBO. '
            'Use a different name for "%s" or match it in '
            '[QuickBooks Online --> Mapping --> %s] menu.\n'
        ),
        62401: _(
            '\n- Another object is already using this name in QBO. But it was not fetched due to '
            'it is an object of another model. \nFor example, you are trying to export "Customer" '
            'but there is the same object among "Vendors".\n'
        ),
        62402: _(
            '\n- You are trying to create another one map-model from Odoo object, '
            'but such name must be unique. Define only one Odoo object please.\n'
        ),
        6430: _(
            '\n- Change it in [QuickBooks Online --> Mapping --> Accounts] menu.\n'
        ),
    }

    @classmethod
    def convert_code(cls, code):
        if int(code) == cls.SUCCESS:
            return cls.MISC_ERROR
        return code


def _commit_company_vals(self, company, vals=None):
    with self.env.registry.cursor() as new_cr:
        new_env = api.Environment(new_cr, self.env.uid, self.env.context)
        company.with_env(new_env).write(vals or COMPANY_FIELDS_TO_RESET)


def handle_operational_error(method):
    """Expected inheritance of the `job.transaction.mixin` for `odoo_model`"""
    @wraps(method)
    def _handle_operational_error(odoo_model, *args, **kwargs):
        vals = odoo_model.update_transaction_kwargs()
        kwargs.update(vals)

        try:
            result = method(odoo_model, *args, **kwargs)
        except OperationalError as ex:
            if ex.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                raise ex

            with odoo_model.env.registry.cursor() as new_cr:
                new_env = api.Environment(new_cr, SUPERUSER_ID, dict())
                odoo_model.with_env(new_env).increment_counter()

            raise ex

        return result
    return _handle_operational_error


def expected_one(func):
    def wrapper(self, *args, **kwargs):
        if not self:  # TODO: in case when self is None - func() returns all unmapped records
            pass

        result, error = func(self, *args, **kwargs), False

        if not result:
            error = _(
                '- Match %s "%s" before export please' % (self._description.lower(), self.name)
            )
        elif len(result) > 1:
            error = _(
                '- There are several map-objects %s for %s "%s". Define only one please'
                % (result.mapped('qbo_name'), self._description.lower(), self.name)
            )
        if error:
            menu_path = MAPPING_MENUS.get(self._name, '')
            raise ValidationError('%s: %s.' % (error, menu_path))

        return result
    return wrapper


def _process_request(method, odoo_model, company, *args, sub_query=True, **kwargs):
    try:
        result = method(odoo_model, company, *args, **kwargs)
    except AuthClientError as ex:
        _commit_company_vals(odoo_model, company)
        message = _(
            'Authentication error: %s. \nYou need to re-authorize your app '
            'in Settings <QuickBooks Online>.' % (ex.args)
        )
        _logger.error(message)
        return message, ex.status_code
    except AuthorizationException as ex:
        if sub_query and company._refresh_qbo_access_token():
            _logger.info('Repeated request to Intuit-API.')
            return _process_request(method, odoo_model, company, *args, sub_query=False, **kwargs)

        _commit_company_vals(odoo_model, company)
        message = _(
            'Authorization error: %s, %s. %s. \nYou need to re-authorize your app '
            'in Settings <QuickBooks Online>.' % (ex.error_code, ex.message, ex.detail)
        )
        _logger.error(message)
        return message, IntuitResponse.convert_code(ex.error_code)
    except QuickbooksException as ex:
        message = _('%s, %s. %s.' % (ex.error_code, ex.message, ex.detail))
        _logger.error(message)
        return message, IntuitResponse.convert_code(ex.error_code)
    except Exception as ex:
        message = _('[General Error] %s.') % (ex.args and ex.args[0])
        _logger.error(message)
        return message, IntuitResponse.GENERAL_ERROR

    return result, IntuitResponse.SUCCESS


def catch_exception(method):
    def _catch_exception(odoo_model, company, *args, **kwargs):
        return _process_request(method, odoo_model, company, *args, **kwargs)
    return _catch_exception


class QboClass:
    """QBO Lib class manager."""

    def __init__(self, *args):
        self.storage = {
            klass.qbo_object_name.lower(): klass for klass in args
        }

    def __getitem__(self, key):
        return self.storage.get(key)

    def qbo_types(self):
        return list(self.storage.keys())


class QboCompanyInfo:

    def __init__(self, company, preference, company_info, currency_list):
        self.company = company
        self._preference = preference
        self._company_info = company_info
        self._currencies = currency_list

    @property
    def name(self):
        return self._company_info.CompanyName

    @property
    def address(self):
        return self._company_info.CompanyAddr

    @property
    def country_iso(self):
        return self._company_info.Country

    @property
    def home_currency(self):
        return self._preference.CurrencyPrefs.HomeCurrency.value

    @property
    def multi_currency_enabled(self):
        return self._preference.CurrencyPrefs.MultiCurrencyEnabled

    def preference(self):
        return self._preference.to_dict()

    def company_info(self):
        return self._company_info.to_dict()

    def external_currencies(self):
        return [x.to_dict() for x in self._currencies]

    def currency_codes(self):
        return [self.home_currency] + [x.Code for x in self._currencies]

    def currency_codes_str(self):
        return ', '.join(self.currency_codes())

    def address_format(self):
        return (
            f'{self.name}, {self.address}, {self.country_iso} [{self.currency_codes_str()}]'
        )

    def get_sales_custom_field(self):
        return self._preference.SalesFormsPrefs.CustomField

    def validate_country(self):
        country_iso = self.country_iso
        if country_iso and len(country_iso) == 2 and self.company.country_id.code != country_iso:
            # TODO: `country_iso` is optional field. We really don't know exact 'len'
            return False
        return True

    def validate_home_currency(self):
        return self.company.currency_id.name.lower() == self.home_currency.lower()

    def validate_foreign_currency(self, foreign_currency):
        codes_list_lower = [x.lower() for x in self.currency_codes()]
        return (foreign_currency or '').lower() in codes_list_lower


class RouteParser:
    """RouteParser context manager provides safety extracting 'qbo routes'."""

    def __init__(self, field, route, def_value, dict_to_parse, parsed_vals):
        self.field = field
        self.route = route
        self.extract_value = def_value
        self.dict_to_parse = dict_to_parse
        self.parsed_vals = parsed_vals

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """Any exception will be ignored if returned True."""
        self.parsed_vals[self.field] = self.extract_value
        return True

    def parse(self):
        value = unsafe_eval('self.dict_to_parse%s' % self.route)
        self.extract_value = value or False


class TaxSuiter:

    us_tax = TAXABLE
    us_non_tax = NON_TAXABLE
    tax_exempt_list = TAX_EXEMPT_LIST

    def __init__(self, record):
        self._record = record
        self._lines = self._parse_product_line()
        self._taxes = self._parse_tax_detail()

    @property
    def taxes_for_all(self):
        tax_classes = [x.tax_class for x in self.lines()]
        return len(set(tax_classes)) == 1

    def lines(self):
        return [x for x in self._lines if x.taxable and x.tax_class not in self.tax_exempt_list]

    def taxes(self):
        return [x for x in self._taxes if x.amount and x.percent_based]

    def get_fit_taxes(self):

        if self.taxes_for_all:
            tax_ids = [x.id for x in self.taxes()]

            return {
                line.id: tax_ids for line in self.lines()
            }

        tax_dict = defaultdict(list)
        priorities = self.get_priotities()

        for tax in self.taxes():

            for qty in priorities:
                if self._find_combination(tax, qty, tax_dict):
                    break

        return tax_dict

    def _find_combination(self, tax, qty, tax_dict):
        net_amount = tax.net_amount

        for combination in self.get_combination(qty):
            amount = sum([x.amount for x in combination])

            if str(amount) == net_amount:
                [tax_dict[line.id].append(tax.id) for line in combination]
                return True

        return False

    def get_combination(self, n):
        for x in combinations(self.lines(), n):
            yield x

    def get_priotities(self):
        priority_list = list(range(0, len(self.lines()) + 1))
        priority_list.sort(reverse=True)

        counter = Counter([x.tax_class for x in self.lines()])
        most_common = list(set(dict(counter).values()))
        most_common.sort(reverse=True)

        [priority_list.remove(x) for x in most_common]

        return most_common + priority_list

    def _parse_product_line(self):
        Line = namedtuple('Line', 'id amount tax_class taxable')

        def serialize(line):
            line_num = line['LineNum']
            amount = Decimal(str(line['Amount']))

            tax_class_ref = line['SalesItemLineDetail'].get('TaxClassificationRef', {}) or dict()
            tax_class_ref_value = tax_class_ref.get('value', False)

            tax_code_ref = line['SalesItemLineDetail'].get('TaxCodeRef', {}) or dict()
            value = tax_code_ref.get('value', False)
            taxable = value and value != self.us_non_tax

            return Line(line_num, amount, tax_class_ref_value, bool(taxable))

        product_lines = list()

        for line in self._record.Line:

            line_dict = line.to_dict()
            sale_detail = line_dict.get('SalesItemLineDetail')

            if not sale_detail or not isinstance(sale_detail, dict):
                continue

            product_lines.append(
                serialize(line_dict)
            )

        return product_lines

    def _parse_tax_detail(self):
        Tax = namedtuple('Tax', 'id amount percent_based net_amount')

        def serialize(tax):
            return Tax(
                tax.TaxLineDetail.TaxRateRef.value,
                tax.Amount,
                tax.TaxLineDetail.PercentBased,
                str(tax.TaxLineDetail.NetAmountTaxable),
            )

        tax_detail = self._record.TxnTaxDetail

        if not tax_detail:
            return list()

        return [serialize(x) for x in tax_detail.TaxLine]
