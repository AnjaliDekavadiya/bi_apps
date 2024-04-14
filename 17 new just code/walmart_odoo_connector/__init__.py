# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2021-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from . import models
from . import wizard


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    from odoo.tools.misc import  file_path
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if not 16 < float(server_serie) <= 17:
        raise UserError(
            'Module support Odoo series 17.0 found {}.'.format(server_serie))

    def jre_exists():
        import subprocess
        try:
            subprocess.Popen("java -version",
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
            return True
        except FileNotFoundError:
            path = f'''{file_path('walmart_odoo_connector')}/openlogic-openjdk-jre-8u292-b10-linux-x64/bin/java'''
            subprocess.Popen(path,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
            return True
    if not jre_exists():
        raise UserError(
            '''Java not found in the system. For installation:\n
            https://java.com/en/download/''')
    return True
