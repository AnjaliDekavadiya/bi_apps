# -*- coding: utf-8 -*-

from . import common_const
from . import base_model
from . import common_method
from . import base
from . import mail
from . import manage_object_import
from . import import_data

import odoo
from odoo.http import request
tmp_val = False
tmp_check_cr = odoo.sql_db.db_connect(request.db).cursor()
try:
    try:
        tmp_check_cr.execute("""Select state from ir_module_module where name = 'analytic' limit 1""")
        tmp_val = tmp_check_cr.dictfetchall()[0]['state']
    except:
        tmp_val = 'unknow'
    if tmp_val == 'installed':
        from . import analytic
except Exception as e:
    pass
finally:
    del tmp_val
    tmp_check_cr.close()
    del tmp_check_cr 