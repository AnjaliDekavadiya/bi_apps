# -*- coding: utf-8 -*-

from odoo import models, fields,api


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    # def search(self, args, **kwargs):
    #     print("111111111111111111111111111111111")
    #     if self.env.context.get('website_id'):
    #         print("222222222222222222222222222222222")
    #         shop_visibility = self.env['public.shop.visibility']
    #         print("33333333333333333333333333",shop_visibility)
    #         visibility = shop_visibility.sudo().search([])
    #         print("visibility:--------------------",visibility)
    #         public_user = self.env.user.has_group('base.group_public')
    #         if not public_user:
    #             print("4444444444444444444444444444")
    #             if self.env.user.partner_id.custom_visibility_category_ids:
    #                 args += [('id', 'in', self.env.user.partner_id.custom_visibility_category_ids.ids)]
    #         else:
    #             if not visibility.all_category:
    #                 print("5555555555555555555555555")
    #                 args += [('id', 'in', visibility.category_ids.ids)]
    #     return super(ProductPublicCategory, self).search(args, **kwargs)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('website_id'):
            shop_visibility = self.env['public.shop.visibility']
            visibility = shop_visibility.sudo().search([])
            public_user = self.env.user.has_group('base.group_public')
            if not public_user:
                if self.env.user.partner_id.custom_visibility_category_ids:
                    args += [('id', 'in', self.env.user.partner_id.custom_visibility_category_ids.ids)]
            else:
                if not visibility.all_category:
                    args += [('id', 'in', visibility.category_ids.ids)]
        # return super(ProductPublicCategory, self)._search(args, offset, limit, order, count, access_rights_uid)
        return super(ProductPublicCategory, self)._search(args, offset, limit, order, count)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
