from . import models
# from odoo.api import Environment, SUPERUSER_ID


def uninstall_hook(env):
    # env = Environment(cr, SUPERUSER_ID, {})
    for user in env['res.users'].search([]):
        if user.ks_office365_channel_inbox:
            channel = env['discuss.channel'].browse(user.ks_office365_channel_inbox.id)
            office_mails = env['mail.message'].search([('res_id', '=', channel.id)])
            office_mails.unlink()
            channel.unlink()
        if user.ks_office365_channel_sentitems:
            channel = env['discuss.channel'].browse(user.ks_office365_channel_sentitems.id)
            office_mails = env['mail.message'].search([('res_id', '=', channel.id)])
            office_mails.unlink()
            channel.unlink()
        if user.ks_office365_channel_archive:
            channel = env['discuss.channel'].browse(user.ks_office365_channel_archive.id)
            office_mails = env['mail.message'].search([('res_id', '=', channel.id)])
            office_mails.unlink()
            channel.unlink()
