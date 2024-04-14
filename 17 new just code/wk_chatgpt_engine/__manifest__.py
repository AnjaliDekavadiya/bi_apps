# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
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
  "name"                 :  "Odoo AI Engine (ChatGPT)",
  "summary"              :  """
                            Odoo AI Engine (ChatGPT) integration allows users to create content based on the desired tone by asking questions. The module also includes a translation feature, enabling users to translate text into another language. The module also assists in grammatically correct sentences and helps in generating SEO meta titles and meta descriptions. This ensures that the generated content maintains proper grammar and readability. Overall, this module enhances the capabilities of Odoo by leveraging the AI engine to generate relevant and high-quality content while setting limits to ensure optimal output.   
                            """,
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-ai-engine-chatgpt.html",
  "description"          :  """
                                Odoo AI Engine (ChatGPT) reduces the need for manual input for adding quality content, grammar corrections, language translations, meta information, etc. by minimal related input.
                                odoo ai engine (chatgpt)
                                ai engine
                                chatgpt
                                ai engine (chatgpt)
                                openai
                                artificial intelligence
                                ai
                                ai content
                                product description by ai
                                chatgpt app
                                open ai chatgpt
                                gpt-3
                                chat gpt-3
                                chat gpt signup
                                chat gpt login
                                how to use chat gpt
                                open ai
                                chat gpt answers
                                odoo
                                odoo apps
                                odoo admin
                                ai in odoo
                            """,
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_chatgpt_engine&custom_url=/",
  "depends"              :  [ 'website_sale' ],
  "data"                 :  [   
                                'security/ir.model.access.csv',
                                'wizard/ai_translate_wizard_views.xml',
                                'views/res_config_settings_views.xml',
                                'views/suggest_seo_views.xml',
                                'views/openai_prompt_instruction_views.xml',
                                'views/openai_prompt_tone_views.xml',
                                'wizard/ai_bulk_content_views.xml',
                                'views/product_views.xml',
                                'wizard/suggest_seo_wizard_views.xml',
                            ],
  "demo"                 :  [
                              'data/openai_demo.xml',
                            ],
  "assets"               :  {
                                'web_editor.assets_wysiwyg': [
                                      'https://cdnjs.cloudflare.com/ajax/libs/sweetalert/2.1.0/sweetalert.min.js',
                                      '/wk_chatgpt_engine/static/src/scss/generate_content.scss',
                                      '/wk_chatgpt_engine/static/src/js/update_content.js',
                                      '/wk_chatgpt_engine/static/src/js/content_dialog.js',
                                      '/wk_chatgpt_engine/static/src/js/content_prompt_dialog.js',
                                      '/wk_chatgpt_engine/static/src/js/content_prompt_dialog.xml',
                                      '/wk_chatgpt_engine/static/src/js/grammar_correction_dialog.js',
                                      '/wk_chatgpt_engine/static/src/js/grammar_correction_dialog.xml',
                                 ],
                            },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
