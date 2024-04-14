from odoo import models, fields, api, exceptions, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    lunch_pin = fields.Char(string="PIN",copy=False,
        help="PIN used to order lunch in the Kiosk Mode of the Lunch application")
    user_faces = fields.One2many("res.users.faces", "user_id", "Faces")

    def action_users_lunch_kiosk_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'name': 'Confirm',
            'tag': 'lunch_kiosk_mode_adv.lunch_kiosk_confirm',
            'user_id': self.id,
            'user_name': self.name,
            'kiosk_mode': True,
        }
    
    def action_users_lunch_recognition_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'name': 'Confirm',
            'tag': 'lunch_kiosk_mode_adv.lunch_recognition_confirm',
            'user_id': self.id,
            'user_name': self.name,
            'kiosk_mode': True,
        }
    
    def order_lunch_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        
        if entered_pin is not None and entered_pin == self.sudo().lunch_pin:
            return self._lunch_action(next_action)
        if not self.user_has_groups('lunch.group_lunch_user'):
            return {'warning': _('You must have access right in the Lunch app / incorrect PIN entered. Please contact your administrator.')}
        return {'warning': _('Wrong PIN')}
    
    def order_lunch_recognition(self, next_action):
        self.ensure_one()
        if self.id:
            return self._lunch_action(next_action)
        return {'warning': _('Wrong PIN')}
    
    def _lunch_action(self, next_action):
        self.ensure_one()
        user = self.sudo()
        next_action = self.env["ir.actions.actions"]._for_xml_id("lunch_kiosk_mode_adv.lunch_product_action_order_kiosk")
        context = self._context.copy()
        next_action['context'] = context
        next_action['context'].update({
            'default_user_id': self.id,
            'user_id': self.id,
            'user_name': self.name,
            'kiosk_mode': True,
        })
        return {'action': next_action}
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['user_faces']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['user_faces']

class ResUsersFaces(models.Model):
    _name = "res.users.faces"
    _description = "Face Recognition Images"
    _inherit = ['image.mixin']
    _order = 'id'

    user_id = fields.Many2one("res.users", "User", index=True, ondelete='cascade')
    login = fields.Char(related="user_id.login", string="User Login", readonly=True, store=True)
    name = fields.Char("Name", related='user_id.name')
    image = fields.Binary("Images")
    descriptor = fields.Text(string='Face Descriptor')
    has_descriptor = fields.Boolean(string="Has Face Descriptor",default=False, compute='_compute_has_descriptor', readonly=True, store=True)
    
    @api.depends('descriptor')
    def _compute_has_descriptor(self):
        for rec in self:
            rec.has_descriptor = True if rec.descriptor else False

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'user_id',
            'login',
            'name',
            'image',
            'descriptor',
            'has_descriptor',
        ]
        
    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'user_id',
            'login',
            'name',
            'image',
            'descriptor',
            'has_descriptor',
        ]
