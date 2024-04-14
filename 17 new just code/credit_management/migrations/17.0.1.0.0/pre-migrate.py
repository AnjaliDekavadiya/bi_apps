# Copyright 2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

import logging


def migrate(cr, version):
    """pre-migrate script for merging credit_management_on_child code into credit_management"""
    if not version:
        return
    logger = logging.getLogger(__name__)
    query_credit_management_on_child_model_data = (
        "select 1 from ir_model_data where module = 'credit_management_on_child';"
    )
    cr.execute(query_credit_management_on_child_model_data)
    credit_management_on_child_model_data = cr.dictfetchall()
    query_update_credit_management_data = """
        update
            ir_model_data
        set
            module='credit_management'
        where
            module = 'credit_management_on_child' and
            model = 'ir.model.fields'
        returning id;
    """
    if len(credit_management_on_child_model_data):
        cr.execute(query_update_credit_management_data)
        logger.info(str(cr.dictfetchall()))
