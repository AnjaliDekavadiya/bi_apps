from . import models
from . import wizard

def post_init_hook(env):
    env["appraisal"]._create_approval_settings()
    
def uninstall_hook(env):
    env['approval.settings'].get("appraisal").unlink()    