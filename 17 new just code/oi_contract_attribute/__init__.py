from . import models
from odoo.api import Environment, SUPERUSER_ID


def post_init_hook(env):
    contract_type_id = env['hr.contract.type'].search([], limit=1)
    contracts  = env['hr.contract'].search([('contract_type_id','=', False)])
    contracts.sudo().write({'contract_type_id' : contract_type_id.id})
    env.cr.commit() 
    env.cr.execute('ALTER TABLE "hr_contract" ALTER COLUMN "contract_type_id" SET NOT NULL')