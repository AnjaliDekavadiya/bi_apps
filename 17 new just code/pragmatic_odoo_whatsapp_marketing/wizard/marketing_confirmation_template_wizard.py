from odoo import api, fields, models


class MarketingConfirmationTemplateWizard(models.TransientModel):
    _name = 'marketing.confirmation.template.wizard'
    _description = "Confirmation Template Message"

    @api.model
    def default_get(self, fields):
        res = super(MarketingConfirmationTemplateWizard, self).default_get(fields)
        res.update({
            'message': 'Make sure you have set the correct name, recipient, message body, attachment and Whatsapp instance. As once the template is created, these fields cannot change.',
        })
        return res

    message = fields.Text("Message", readonly=True)

    def action_confirm_create_template_in_odoo(self):
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        whatsapp_marketing_id = self.env['whatsapp.marketing'].browse(active_id)
        if whatsapp_marketing_id.whatsapp_provider == 'whatsapp_chat_api':
            self.chat_api_create_template_in_odoo(whatsapp_marketing_id)
        elif whatsapp_marketing_id.whatsapp_provider == 'gupshup':
            self.gupshup_create_template_in_odoo(whatsapp_marketing_id)

    def chat_api_create_template_in_odoo(self, whatsapp_marketing_id):
        whatsapp_templates_dict = {}
        whatsapp_templates_dict['name'] = whatsapp_marketing_id.name
        whatsapp_templates_dict['marketing_template'] = True
        whatsapp_templates_dict['whatsapp_marketing_id'] = whatsapp_marketing_id.id
        whatsapp_templates_dict['category'] = 'MARKETING'
        whatsapp_templates_dict['template_type'] = 'simple'
        whatsapp_templates_dict['whatsapp_instance_id'] = whatsapp_marketing_id.whatsapp_instance_id.id
        whatsapp_templates_dict['provider'] = whatsapp_marketing_id.whatsapp_instance_id.provider
        if whatsapp_marketing_id.attachment_id:
            if 'image' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_image'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/pos_receipt.jpg'

            elif 'application/pdf' in whatsapp_marketing_id.attachment_id.mimetype or 'text' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_document'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/S00014.pdf'

            elif 'video' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_video'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/pragmatic_core_values.mp4'

        else:
            whatsapp_templates_dict['header'] = 'text'

        whatsapp_templates_dict['model_id'] = whatsapp_marketing_id.whatsapp_model_id.id

        sample_message, template_body = self.create_sample_message_body_for_whatsapp_template(whatsapp_marketing_id)
        whatsapp_templates_dict['sample_message'] = sample_message
        whatsapp_templates_dict['body'] = template_body
        whatsapp_template_id = self.env['whatsapp.templates'].create(whatsapp_templates_dict)
        if len(whatsapp_template_id) > 0:
            whatsapp_marketing_id.whatsapp_template_id = whatsapp_template_id.id

    def gupshup_create_template_in_odoo(self, whatsapp_marketing_id):
        whatsapp_templates_dict = {}
        whatsapp_templates_dict['name'] = whatsapp_marketing_id.name
        whatsapp_templates_dict['marketing_template'] = True
        whatsapp_templates_dict['whatsapp_marketing_id'] = whatsapp_marketing_id.id
        whatsapp_templates_dict['category'] = 'TRANSACTIONAL'
        whatsapp_templates_dict['template_type'] = 'simple'
        whatsapp_templates_dict['whatsapp_instance_id'] = whatsapp_marketing_id.whatsapp_instance_id.id
        whatsapp_templates_dict['provider'] = whatsapp_marketing_id.whatsapp_instance_id.provider
        if whatsapp_marketing_id.attachment_id:
            if 'image' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_image'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/pos_receipt.jpg'

            elif 'application/pdf' in whatsapp_marketing_id.attachment_id.mimetype or 'text' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_document'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/S00014.pdf'

            elif 'video' in whatsapp_marketing_id.attachment_id.mimetype:
                whatsapp_templates_dict['header'] = 'media_video'
                whatsapp_templates_dict['sample_url'] = 'https://www.pragtech.co.in/pdf/whatsapp/pragmatic_core_values.mp4'

        else:
            whatsapp_templates_dict['header'] = 'text'

        whatsapp_templates_dict['gupshup_template_labels'] = whatsapp_marketing_id.name
        whatsapp_templates_dict['model_id'] = whatsapp_marketing_id.whatsapp_model_id.id

        sample_message, template_body = self.create_sample_message_body_for_whatsapp_template(whatsapp_marketing_id)
        gupshup_sample_message = self.create_sample_message_for_gupshup_template(whatsapp_marketing_id)
        whatsapp_templates_dict['body'] = template_body
        whatsapp_templates_dict['gupshup_sample_message'] = gupshup_sample_message
        whatsapp_template_id = self.env['whatsapp.templates'].create(whatsapp_templates_dict)
        if len(whatsapp_template_id) > 0:
            whatsapp_marketing_id.whatsapp_template_id = whatsapp_template_id.id

    def create_sample_message_body_for_whatsapp_template(self, whatsapp_marketing_id):
        res_id = whatsapp_marketing_id._get_remaining_recipients()
        parameters = ['{{ ' + value + ' }}' for value in (whatsapp_marketing_id.message_body).split() if value.startswith('object.')]
        message = ''
        for parameter in parameters:
            bodies = self.env['mail.render.mixin']._render_template(parameter, whatsapp_marketing_id.whatsapp_model_real, res_id, post_process=True)
            key = res_id[0]
            message += bodies[key] + ','
        sample_message = message[:-1]

        template_body = self.create_template_body(whatsapp_marketing_id)
        return sample_message, template_body

    def create_sample_message_for_gupshup_template(self, whatsapp_marketing_id):
        res_ids = whatsapp_marketing_id._get_remaining_recipients()
        gupshup_sample_message = self.env['mail.render.mixin']._render_template(whatsapp_marketing_id.message_body, whatsapp_marketing_id.whatsapp_model_real, res_ids,
                                                                                post_process=True)
        for res_id in res_ids:
            return gupshup_sample_message[res_id]

    def create_template_body(self, whatsapp_marketing_id):
        message_body = whatsapp_marketing_id.message_body
        counter = 1
        whatsapp_template_body = ''
        last_index = len(message_body)
        index = 0
        open_idx, close_idx = 0, 0
        while index <= last_index:
            if not open_idx:
                open_idx = message_body.find('{{')
            else:
                if open_idx != -1:
                    open_idx = message_body.find('{{', close_idx)
                else:
                    open_idx = close_idx = -1
            if open_idx != -1:
                open_idx += 2
                whatsapp_template_body += message_body[close_idx:open_idx]
                close_idx = message_body.find('}}', open_idx)
                if close_idx != -1:
                    whatsapp_template_body += str(counter)
                    counter += 1
                    index = close_idx
            elif close_idx != -1:
                close_idx = message_body.find('}}', index)
                if close_idx:
                    index = close_idx
                    whatsapp_template_body += "}}"
            elif open_idx == -1 and close_idx == -1:
                break
        return whatsapp_template_body
