from odoo import api, models, fields, _
import json
import base64


class ImportDocument(models.TransientModel):
    _name = "sam.import.document"
    _description = "SAM Import Document"

    name = fields.Char("Name")
    import_doc = fields.Binary("Import Document")
    import_tag = fields.Boolean("Is Import Tag")
    archive = fields.Boolean("Active")
    missing_value = fields.Html("Missing Data")
    is_test = fields.Boolean("Is Test")

    def test_action(self):
        try:
            import_doc = base64.b64decode(self.import_doc).decode('utf-8')
            json_data = json.loads(import_doc)

            user_name = []
            menu_data = []
            model_data = []
            report_action_data = []
            server_data = []
            field_data = []
            button_data = []
            page_data = []
            link_data = []
            filter_data = []
            group_data = []

            for record in json_data.keys():

                # user
                for user in json_data[record]['user_ids']:
                    check_user = self.env['res.users'].with_user(1).search([('email', '=', user['e-mail'])])
                    if not check_user:
                        user_name.append(user['name'])

                # menu
                for menu in json_data[record]['menu']:
                    # check_menu = self.env['ir.ui.menu'].with_user(1).search(
                    #     [('name', '=', menu['name']), ('parent_id.name', '=', menu['parent_id'])])
                    check_menu = self.env['menu.item'].with_user(1).search(
                        [('name', '=', menu['name'])])
                    if not check_menu:
                        menu_data.append(menu['name'])

                # model access
                for model_access_id in json_data[record]['model_access']:
                    check_model = self.env['ir.model'].with_user(1).search([('model', '=', model_access_id['model']['model'])])
                    if check_model:
                        for report_action in model_access_id['report_action_ids']:
                            check_report_action = self.env['action.data'].with_user(1).search([('name', '=', report_action), (
                                'action_id.binding_model_id', '=', model_access_id['model']['name'])])
                            if not check_report_action:
                                report_name = report_action + '(' + model_access_id['model']['name'] + ')'
                                report_action_data.append(report_name)

                        for server_action in model_access_id['server_action_ids']:
                            check_server_action = self.env['action.data'].with_user(1).search([('name', '=', server_action), (
                                'action_id.binding_model_id', '=', model_access_id['model']['name'])])
                            if not check_server_action:
                                server_name = server_action + '(' + model_access_id['model']['name'] + ')'
                                server_data.append(server_name)
                    else:
                        if model_access_id['model']['name'] not in model_data:
                            model_data.append(model_access_id['model']['name'])
                        for report_action in model_access_id['report_action_ids']:
                            report_name = report_action + '(' + model_access_id['model']['name'] + ')'
                            report_action_data.append(report_name)
                        for server_action in model_access_id['server_action_ids']:
                            server_name = server_action + '(' + model_access_id['model']['name'] + ')'
                            server_data.append(server_name)

                # field access
                for field_access_id in json_data[record]['field_access']:
                    check_model = self.env['ir.model'].with_user(1).search([('model', '=', field_access_id['model']['model'])])
                    if check_model:
                        for field in field_access_id['field_id']:
                            check_field = self.env['ir.model.fields'].with_user(1).search(
                                [('model_id.name', '=', field_access_id['model']['name']), ('name', '=', field)])
                            if not check_field:
                                field_name = field + '(' + field_access_id['model']['name'] + ')'
                                field_data.append(field_name)
                    else:
                        if field_access_id['model']['name'] not in model_data:
                            model_data.append(field_access_id['model']['name'])

                        for field in field_access_id['field_id']:
                            field_name = field + '(' + field_access_id['model']['name'] + ')'
                            field_data.append(field_name)

                # domain access
                for domain_access_id in json_data[record]['domain_access']:
                    check_model = self.env['ir.model'].with_user(1).search([('model', '=', domain_access_id['model']['model'])])
                    if not check_model and domain_access_id['model']['name'] not in model_data:
                        model_data.append(domain_access_id['model']['name'])

                # button and tab_access
                for button_tab_access_id in json_data[record]['button_and_tab_access']:
                    new_rec = self.env['hide.view.nodes'].new()
                    new_rec._get_button()

                    check_model = self.env['ir.model'].with_user(1).search([('model', '=', button_tab_access_id['model']['model'])])
                    if check_model:

                        for button in button_tab_access_id['btn_store_model_nodes_ids']:
                            check_button = self.env['store.model.nodes'].with_user(1).search(
                                [('attribute_name', '=', button['name'])])
                            if not check_button:
                                button_name = button['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                                button_data.append(button_name)

                        for page in button_tab_access_id['page_store_model_nodes_ids']:
                            check_page = self.env['store.model.nodes'].with_user(1).search([('attribute_name', '=', page['name'])])
                            if not check_page:
                                page_name = page['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                                page_data.append(page_name)

                        for link in button_tab_access_id['link_store_model_nodes_ids']:
                            check_link = self.env['store.model.nodes'].with_user(1).search([('attribute_name', '=', link['name'])])
                            if not check_link:
                                link_name = link['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                                link_data.append(link_name)
                    else:

                        if button_tab_access_id['model']['name'] not in model_data:
                            model_data.append(button_tab_access_id['model']['name'])

                        for button in button_tab_access_id['btn_store_model_nodes_ids']:
                            button_name = button['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                            button_data.append(button_name)

                        for page in button_tab_access_id['page_store_model_nodes_ids']:
                            page_name = page['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                            page_data.append(page_name)

                        for link in button_tab_access_id['link_store_model_nodes_ids']:
                            link_name = link['string'] + '(' + button_tab_access_id['model']['name'] + ')'
                            link_data.append(link_name)

                # hide filter group by
                for hide_filter_group_by_id in json_data[record]['hide_filter_group_by']:

                    new_rec = self.env['hide.filters.groups'].new()
                    new_rec._get_filter_groups()

                    check_model = self.env['ir.model'].with_user(1).search(
                        [('model', '=', hide_filter_group_by_id['model']['model'])])
                    if check_model:
                        for filter in hide_filter_group_by_id['filters_store_model_nodes_ids']:
                            check_filter = self.env['store.filters.groups'].with_user(1).search(
                                [('attribute_name', '=', filter['name'])])
                            if not check_filter:
                                filter_name = filter['string'] + '(' + hide_filter_group_by_id['model']['name'] + ')'
                                filter_data.append(filter_name)

                        for group in hide_filter_group_by_id['group_store_model_nodes_ids']:
                            check_group = self.env['store.filters.groups'].with_user(1).search(
                                [('attribute_name', '=', group['name'])])
                            if not check_group:
                                group_name = group['string'] + '(' + hide_filter_group_by_id['model']['name'] + ')'
                                group_data.append(group_name)
                    else:
                        if hide_filter_group_by_id['model']['name'] not in model_data:
                            model_data.append(hide_filter_group_by_id['model']['name'])

                        for filter in hide_filter_group_by_id['filters_store_model_nodes_ids']:
                            filter_name = filter['string'] + '(' + hide_filter_group_by_id['model']['name'] + ')'
                            filter_data.append(filter_name)

                        for group in hide_filter_group_by_id['group_store_model_nodes_ids']:
                            group_name = group['string'] + '(' + hide_filter_group_by_id['model']['name'] + ')'
                            group_data.append(group['string'])

                # chatter
                for chatter_id in json_data[record]['chatter']:
                    check_model = self.env['ir.model'].with_user(1).search([('model', '=', chatter_id['model']['model'])])
                    if not check_model and chatter_id['model']['name'] not in model_data:
                        model_data.append(chatter_id['model']['name'])

            missing_data = {
                'user': user_name,
                'menu': menu_data,
                'model': model_data,
                'report_action': report_action_data,
                'server_action': server_data,
                'field': field_data,
                'button': button_data,
                'page': page_data,
                'link': link_data,
                'filter': filter_data,
                'group': group_data,
            }

            missing_value = ''

            for missing_data_key in missing_data.keys():
                if len(missing_data[missing_data_key]) > 0:
                    heading = '<h4> Below ' + missing_data_key + ' are missing </h4> </br>'
                    values = ''
                    for missing_data_value in missing_data[missing_data_key]:
                        values += '<span>' + missing_data_value + ',</span> </br></br>'
                    missing_value += heading + values

            self.missing_value = missing_value
            self.is_test = True

        except Exception as e:
            self.missing_value = e

    @api.onchange('import_doc')
    def onchange_is_test(self):
        self.is_test = False
        self.missing_value = ""

    def import_action(self):
        try:
            import_doc = base64.b64decode(self.import_doc).decode('utf-8')
            json_data = json.loads(import_doc)

            remove_action_obj = self.env['remove.action']
            access_management_obj = self.env['access.management']
            hide_field_obj = self.env['hide.field']
            access_domain_obj = self.env['access.domain.ah']
            hide_chatter_obj = self.env['hide.chatter']
            hide_view_nodes_obj = self.env['hide.view.nodes']
            hide_filters_groups_obj = self.env['hide.filters.groups']

            for record in json_data.keys():

                # user
                user_id = []
                for user in json_data[record]['user_ids']:
                    check_user = self.env['res.users'].with_user(1).search([('email', '=', user['e-mail'])])
                    user_id.append(check_user.id)

                # menu
                menu_ids = []
                for menu in json_data[record]['menu']:
                    # menu_id = self.env['ir.ui.menu'].with_user(1).search(
                    #     [('name', '=', menu['name']), ('parent_id.name', '=', menu['parent_id'])])
                    menu_id = self.env['menu.item'].with_user(1).search(
                        [('name', '=', menu['name'])])
                    if menu_id:
                        menu_ids.append(menu_id.id)

                if self.import_tag:
                    record_name = json_data[record]['name'] + '[import]'
                else:
                    record_name = json_data[record]['name']

                import_record = access_management_obj.create({
                    'name': record_name,
                    'user_ids': [(6, 0, user_id)],
                    'hide_menu_ids': [(6, 0, menu_ids)],
                    'readonly': json_data[record]['readonly'],
                    'disable_debug_mode': json_data[record]['disable_debug_mode'],
                    'active': False if self.archive else True,
                    'hide_chatter': json_data[record]['global'][0]['hide_chatter'],
                    'hide_send_mail': json_data[record]['global'][0]['hide_send_mail'],
                    'hide_log_notes': json_data[record]['global'][0]['hide_log_notes'],
                    'hide_schedule_activity': json_data[record]['global'][0]['hide_schedule_activity'],
                    'hide_import': json_data[record]['global'][0]['hide_import'],
                    'hide_export': json_data[record]['global'][0]['hide_export']

                })

                for model_access_id in json_data[record].get('model_access'):
                    model = self.env['ir.model'].with_user(1).search([('model', '=', model_access_id['model']['model'])])
                    if model:
                        report_action_data = []
                        for report_action in model_access_id['report_action_ids']:
                            report_action_id = self.env['action.data'].with_user(1).search([('name', '=', report_action), (
                                'action_id.binding_model_id.name', '=', model_access_id['model']['name'])])
                            if report_action_id:
                                report_action_data.append(report_action_id.id)

                        server_action_data = []
                        for server_action in model_access_id['server_action_ids']:
                            server_action_id = self.env['action.data'].with_user(1).search([('name', '=', server_action), (
                                'action_id.binding_model_id.name', '=', model_access_id['model']['name'])])
                            if server_action_id:
                                server_action_data.append(server_action_id.id)

                        view_action_data = []
                        for view_action in model_access_id['view_data_ids']:
                            view_action_id = self.env['view.data'].with_user(1).search([('name', '=', view_action)])
                            view_action_data.append(view_action_id.id)

                        remove_action_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'report_action_ids': [(6, 0, report_action_data)],
                            'server_action_ids': [(6, 0, server_action_data)],
                            'view_data_ids': [(6, 0, view_action_data)],
                            'restrict_create': model_access_id['restrict_create'],
                            'restrict_edit': model_access_id['restrict_edit'],
                            'restrict_delete': model_access_id['restrict_delete'],
                            'restrict_archive_unarchive': model_access_id['restrict_archive_unarchive'],
                            'restrict_duplicate': model_access_id['restrict_duplicate'],
                            'restrict_import': model_access_id['restrict_import'],
                            'restrict_export': model_access_id['restrict_export'],
                        })

                for field_access_id in json_data[record].get('field_access'):
                    model = self.env['ir.model'].with_user(1).search([('model', '=', field_access_id['model']['model'])])
                    if model:
                        field_data = []
                        for field in field_access_id['field_id']:
                            field_id = self.env['ir.model.fields'].with_user(1).search(
                                [('model_id.name', '=', field_access_id['model']['name']), ('name', '=', field)])
                            if field_id:
                                field_data.append(field_id.id)

                        hide_field_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'field_id': [(6, 0, field_data)],
                            'invisible': field_access_id['invisible'],
                            'readonly': field_access_id['readonly'],
                            'required': field_access_id['required'],
                            'external_link': field_access_id['external_link'],
                        })

                for domain_access_id in json_data[record]['domain_access']:
                    model = self.env['ir.model'].with_user(1).search([('model', '=', domain_access_id['model']['model'])])
                    if model:
                        access_domain_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'domain': domain_access_id['domain'],
                            'read_right': domain_access_id['read_right'],
                            'create_right': domain_access_id['create_right'],
                            'write_right': domain_access_id['write_right'],
                            'delete_right': domain_access_id['delete_right'],
                        })

                for button_tab_access_id in json_data[record]['button_and_tab_access']:
                    model = self.env['ir.model'].with_user(1).search([('model', '=', button_tab_access_id['model']['model'])])
                    if model:
                        new_rec1 = self.env['hide.view.nodes'].new({'model_id': model.id})
                        new_rec1._get_button()
                        button_data = []
                        for button in button_tab_access_id['btn_store_model_nodes_ids']:
                            button_id = self.env['store.model.nodes'].with_user(1).search(
                                [('model_id', '=', model.id), ('attribute_name', '=', button['name'])], limit=1)
                            if button_id:
                                button_data.append(button_id.id)

                        page_data = []
                        for page in button_tab_access_id['page_store_model_nodes_ids']:
                            page_id = self.env['store.model.nodes'].with_user(1).search(
                                [('model_id', '=', model.id), ('attribute_name', '=', page['name'])], limit=1)
                            if page_id:
                                page_data.append(page_id.id)

                        link_data = []
                        for link in button_tab_access_id['link_store_model_nodes_ids']:
                            link_id = self.env['store.model.nodes'].with_user(1).search(
                                [('model_id', '=', model.id), ('attribute_name', '=', link['name'])], limit=1)
                            if link_id:
                                link_data.append(link_id.id)

                        hide_view_nodes_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'btn_store_model_nodes_ids': [(6, 0, button_data)],
                            'page_store_model_nodes_ids': [(6, 0, page_data)],
                            'link_store_model_nodes_ids': [(6, 0, link_data)],
                        })

                for hide_filter_group_by_id in json_data[record]['hide_filter_group_by']:
                    model = self.env['ir.model'].with_user(1).search([('model', '=', hide_filter_group_by_id['model']['model'])])
                    if model:
                        new_rec = self.env['hide.filters.groups'].new({'model_id': model.id})
                        new_rec._get_filter_groups()
                        filter_data = []
                        for filter in hide_filter_group_by_id['filters_store_model_nodes_ids']:
                            filter_id = self.env['store.filters.groups'].with_user(1).search(
                                [('model_id', '=', model.id), ('attribute_name', '=', filter['name'])], limit=1)
                            if filter_id:
                                filter_data.append(filter_id.id)

                        group_data = []
                        for group in hide_filter_group_by_id['group_store_model_nodes_ids']:
                            group_id = self.env['store.filters.groups'].with_user(1).search(
                                [('model_id', '=', model.id), ('attribute_name', '=', group['name'])], limit=1)
                            if group_id:
                                group_data.append(group_id.id)

                        hide_filters_groups_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'filters_store_model_nodes_ids': [(6, 0, filter_data)],
                            'groups_store_model_nodes_ids': [(6, 0, group_data)],
                        })

                for chatter_id in json_data[record]['chatter']:
                    model = self.env['ir.model'].with_user(1).search([('model', '=', chatter_id['model']['model'])])
                    if model:
                        hide_chatter_obj.create({
                            'access_management_id': import_record.id,
                            'model_id': model.id,
                            'hide_chatter': chatter_id['hide_chatter'],
                            'hide_send_mail': chatter_id['hide_send_mail'],
                            'hide_log_notes': chatter_id['hide_log_notes'],
                            'hide_schedule_activity': chatter_id['hide_schedule_activity'],
                        })

        except Exception as e:
            self.missing_value = e
