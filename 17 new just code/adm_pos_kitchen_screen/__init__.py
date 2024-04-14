from . import models

def setup_default_kitchen_config(env):
  for user in env['res.users'].search([]):
    user.kitchen_category_ids = [(6, 0, env['pos.category'].search([]).ids)]
    user.pos_config_ids = [(6, 0, env['pos.config'].search([]).ids)]