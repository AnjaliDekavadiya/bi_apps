# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo WhatsApp Chat Integration",
  "summary"              :  """Allows to enable WhatsApp Live chat support for customers using support team members.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  20,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-WhatsApp-Chat-Integration.html",
  "description"          :  """Odoo WhatsApp Chat Integration
  Whatsapp Support
  Whatsapp Live Chat
  Live Chat""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_whatsapp_live_chat&lifetime=60&lout=0&custom_url=/",
  "depends"              :  ['website'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/whatsapp_template.xml',
                             'views/res_partner_view.xml',
                             'views/whatsapp_member_type.xml',
                             'views/whatsapp_settings.xml',
                             'data/whatsapp_live_config_data.xml',
                            ],
  "assets"              :{
        'web.assets_frontend':['odoo_whatsapp_live_chat/static/src/css/chatbot.css',
                                'odoo_whatsapp_live_chat/static/src/js/chatbot.js',
                                ],
                          },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['phonenumbers']},
}
