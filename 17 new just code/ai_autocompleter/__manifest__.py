# -*- coding: utf-8 -*-
{
    'name': 'Editor AI Autocompleter GPT',
    'website': 'https://odoonext.com',
    "version": "17.0.5.0",
    'author': "David Montero Crespo",
    'installable': True,
    'summary': """
 Integrate OpenAI API with Odoo Editor | ChatGPT, GPT, GPT-3, GPT-3.5, GPT-4
 Allows the application to leverage the capabilities of the GPT language model to generate human-like responses,Odoo ChatGPTConnector,Odoo ChatGPT,ChatGPT, chatgpt odoo connector, chatgpt
 Introducing Odoo Editor AI - the groundbreaking app that brings the magic of AI right into Odoo Editor! This app is not just for fun, it can actually boost your performance. With our powerful integration of OpenAI's GPT-3 technology, you can now easily generate content, correct grammar mistakes, translate text, or ask AI anything you can imagine - all from within your Odoo Editor's Powerbox commands. If you love ChatGPT and other GPT AI tools, you will love this module!
This Odoo module uses OpenAI's GPT-3.5 language model to automatically complete text fields in Odoosuch as notes, descriptions, and messages. It also autocompletes email addresses based on previous user inputs. 
CRM Dashboard,
OpenAI's GPT-3.5,
OpenAI,
GPT-3.5
OpenAI's GPT-3.5 language model requires a subscription to OpenAI's text API, which can be costly for some users.
""",

    'description': """
Integrate OpenAI API with Odoo Editor | ChatGPT, GPT, GPT-3, GPT-3.5, GPT-4
Allows the application to leverage the capabilities of the GPT language model to generate human-like responses,Odoo ChatGPTConnector,Odoo ChatGPT,ChatGPT, chatgpt odoo connector, chatgpt
This Odoo module uses OpenAI's GPT-3.5 language model to automatically complete text fields in Odoosuch as notes, descriptions, and messages. It also autocompletes email addresses based on previous user inputs. 
CRM Dashboard,
OpenAI's GPT-3.5,
OpenAI,
GPT-3.5
Inventory Dashboard,
Sales Dashboard,
Account Dashboard,
Invoice Dashboard,
Revamp Dashboard,
Best Dashboard,
OpenAI
Odoo Best Dashboard,
Odoo Apps Dashboard,
Best Ninja Dashboard,
Analytic Dashboard,
Pre-Configured Dashboard, 
Create Dashboard,
Beautiful Dashboard,
 Customized Robust Dashboard,
Predefined Dashboard, 
Multiple Dashboards,
Advance Dashboard,
Beautiful Powerful Dashboards,
 Chart Graphs Table View,
All In One Dynamic Dashboard,
 Accounting Stock Dashboard,
 Pie Chart Dashboard,
Modern Dashboard,
Dashboard Studio,
Dashboard Builder,
GPT language model to generate human-like responses,
Odoo ChatGPTConnector,
Odoo ChatGPT,
ChatGPT,
Dashboard Designer,
Odoo Studio. 
When a user creates or edits a record in Odoo that includes text fields, the AI Text Completion module adds an "Auto-complete" button next to each text field.
When the user clicks on the "Auto-complete" button, the module sends the existing text in the text field to OpenAI's GPT-3.5 language model through its text API and receives completed text suggestions in response.
The module displays a list of completed text suggestions to the user, which the user can select and use to complete the text field.
In addition, when a user starts typing an email address in an email field in Odoo, the AI Text Completion module displays a list of autocompleted email address suggestions based on previous user inputs. The user can select an email address from the list and use it to complete the email field.
Configuration:

To use the AI Text Completion module, users must provide the OpenAI API key in the module's configuration form. This will allow the module to communicate with OpenAI's GPT-3.5 language model through its text API.
Benefits:

Saves time for users by automatically completing text fields, reducing manual workload and increasing efficiency.
Improves the accuracy and quality of completed text fields by using a highly advanced AI language model.
Facilitates email creation by autocompleting email addresses.
Limitations:
Introducing Odoo Editor AI - the groundbreaking app that brings the magic of AI right into Odoo Editor! This app is not just for fun, it can actually boost your performance. With our powerful integration of OpenAI's GPT-3 technology, you can now easily generate content, correct grammar mistakes, translate text, or ask AI anything you can imagine - all from within your Odoo Editor's Powerbox commands. If you love ChatGPT and other GPT AI tools, you will love this module!
OpenAI's GPT-3.5 language model requires a subscription to OpenAI's text API, which can be costly for some users.
 """,
    'category': 'Discuss/Sales/CRM',
    'live_test_url': 'https://youtu.be/EWS3DioHF9A',
    'depends': [
        'contacts',
        'mail',
        'utm',
        'link_tracker',
        'web_editor',
        'social_media',
        'web_tour',
        'digest',
    ],
    'data': [
        'views/res_config_settings.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'ai_autocompleter/static/src/js/ai_autocompleter_widget.js',
            'ai_autocompleter/static/src/style/ai_autocompleter_widget.css',
            # "ai_autocompleter/static/src/js/message_reply.js",
            # "ai_autocompleter/static/src/xml/message_reply.xml",
            'ai_autocompleter/static/src/xml/ai_autocompleter.xml',
        ],
    },
    "images": ["static/ai_completion.gif"],
    'application': True,
    'price': 50,
    'currency': 'EUR',
    'license': 'AGPL-3',

}
