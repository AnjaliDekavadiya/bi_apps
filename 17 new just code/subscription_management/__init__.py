# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID

def pre_init_check(cr):
    from odoo.release import series
    from odoo.exceptions import ValidationError

    if not('16.0' < series <= '17.0'):
        raise ValidationError('Module support Odoo series 17.0 found {}.'.format(series))


def uninstall_hook(env):
    try:
        subs_journal = env.ref('subscription_management.subscription_sale_journal')
        if subs_journal:
            subs_journal.unlink()
    except:
        pass