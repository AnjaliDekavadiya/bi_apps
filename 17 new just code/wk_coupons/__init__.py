#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from . import models

def pre_init_check(cr):
    from odoo.release import series
    from odoo.exceptions import ValidationError

    if series != '17.0':
        raise ValidationError('Module support Odoo series 17.0 found {}.'.format(series))
