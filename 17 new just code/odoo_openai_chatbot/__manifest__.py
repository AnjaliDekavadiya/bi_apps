# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

{
    'name': 'Odoo Website Shopping Assistant ( Odoo Chatbot ) using OpenAI',
    'summary': '''Chatbot Using OpenAI (ChatGPT) LLM enhances the functionality of your Odoo chatbot. 
                    It’s built on a GPT-3.5-turbo/GPT-4 model which understands the natural human language. It’s trained in Large Language Model. 
                    The Odoo app improves your query response time and solves almost every problem related to the Odoo data.
                ''',
    'description': """
                            Odoo Chatbot Using OpenAI (ChatGPT) LLM takes your Odoo chatbot to a more efficient and productive level. With the help of a vector database, it can answer any of the customer queries related to the product.
                            Odoo Chatbot Using OpenAI (ChatGPT) LLM
                            Chatbot Using OpenAI (ChatGPT) LLM
                            openAI
                            Open AI
                            AI
                            Chatbot
                            Odoo chatbot
                            gpt-3
                            gpt-3.5
                            gpt-4
                            chatgpt
                            chat bot
                            openAI chatgpt
                            LLM
                            chatbot
                            Odoo Website Shopping Assistant ( Odoo Chatbot ) using OpenAI

    """,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    'version': '1.0.0',
    'category': 'Productivity/Discuss',
    'depends': ['mail_bot', 'website_livechat', 'product'],
    "website":  "https://store.webkul.com/odoo-website-shopping-assistant-odoo-chatbot-using-openai.html",
    "live_test_url":  "http://odoodemo.webkul.com/demo_feedback?module=odoo_openai_chatbot",
    "data":  [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/im_livechat_channel_views.xml',
        'views/ai_bot_config_view.xml',
        'views/templates.xml',

    ],
    'demo': [
        'data/res_users_demo.xml',
        'data/livechat_channel_demo.xml',
    ],
    'assets': {

        'im_livechat.assets_embed_core':  [
            '/odoo_openai_chatbot/static/src/js/public_livechat.js',
            '/odoo_openai_chatbot/static/src/scss/chat.scss',
            '/odoo_openai_chatbot/static/src/xml/**/*',
        ],
    },
    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "currency":  "USD",
    "price":  249,
    "pre_init_hook":  "pre_init_check",

}
