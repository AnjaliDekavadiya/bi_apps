from odoo import fields, models, api, _
import json
import base64


class AccessManagement(models.Model):
    _inherit = "access.management"

    def action_download_file(self):
        # pass
        main_data = {}
      
        for rec in self:

            user_name = []
            for user in rec.user_ids:
                user_name.append({"name": user.name, "e-mail": user.email})

            menu_data = []
            for menu_id in rec.hide_menu_ids:
                menu_data.append({
                    "name": menu_id.name,
                    # "path": menu_id.complete_name,
                    # "parent_id": menu_id.parent_id.name
                })

            model_access_data = []
            for model_access_id in rec.remove_action_ids:
                report_name = []
                server_name = []
                view_name = []

                for report in model_access_id.report_action_ids:
                    report_name.append(report.name)

                for server in model_access_id.server_action_ids:
                    server_name.append(server.name)

                for view in model_access_id.view_data_ids:
                    view_name.append(view.name)

                model_access_data.append({
                    "model": {
                        "name": model_access_id.model_id.name,
                        'model': model_access_id.model_id.model
                    },
                    "report_action_ids": report_name,
                    "server_action_ids": server_name,
                    "view_data_ids": view_name,
                    "restrict_create": True if model_access_id.restrict_create else False,
                    "restrict_edit": True if model_access_id.restrict_edit else False,
                    "restrict_delete": True if model_access_id.restrict_delete else False,
                    "restrict_archive_unarchive": True if model_access_id.restrict_archive_unarchive else False,
                    "restrict_duplicate": True if model_access_id.restrict_duplicate else False,
                    "restrict_import": True if model_access_id.restrict_import else False,
                    "restrict_export": True if model_access_id.restrict_export else False
                })

            field_access = []
            for field_access_id in rec.hide_field_ids:
                field_name = []
                for field in field_access_id.field_id:
                    field_name.append(field.name)

                field_access.append({
                    "model": {
                        "name": field_access_id.model_id.name,
                        'model': field_access_id.model_id.model
                    },
                    "field_id": field_name,
                    "invisible": True if field_access_id.invisible else False,
                    "readonly": True if field_access_id.readonly else False,
                    "required": True if field_access_id.required else False,
                    "external_link": True if field_access_id.external_link else False
                })

            domain_access = []
            for domain_access_id in rec.access_domain_ah_ids:
                domain_access.append({
                    "model": {
                        "name": domain_access_id.model_id.name,
                        'model': domain_access_id.model_id.model
                    },
                    "read_right": True if domain_access_id.read_right else False,
                    "create_right": True if domain_access_id.create_right else False,
                    "write_right": True if domain_access_id.write_right else False,
                    "delete_right": True if domain_access_id.delete_right else False,
                    "apply_domain": True if domain_access_id.apply_domain else False,
                    "domain": domain_access_id.domain,
                })

            button_tab_access = []
            for button_tab_access_rec in rec.hide_view_nodes_ids:
                btns_attribute = []
                pages_attribute = []
                links_attribute = []

                for btn_attribute in button_tab_access_rec.btn_store_model_nodes_ids:
                    btns_attribute.append({
                        "string": btn_attribute.attribute_string,
                        "name": btn_attribute.attribute_name
                    })

                for page_attribute in button_tab_access_rec.page_store_model_nodes_ids:
                    pages_attribute.append({
                        "string": page_attribute.attribute_string,
                        "name": page_attribute.attribute_name
                    })

                for link_attribute in button_tab_access_rec.link_store_model_nodes_ids:
                    links_attribute.append({
                        "string": link_attribute.attribute_string,
                        "name": link_attribute.attribute_name
                    })

                button_tab_access.append({
                    "model": {
                        "name": button_tab_access_rec.model_id.name,
                        'model': button_tab_access_rec.model_id.model
                    },
                    "btn_store_model_nodes_ids": btns_attribute,
                    "page_store_model_nodes_ids": pages_attribute,
                    "link_store_model_nodes_ids": links_attribute,
                })

            hide_filter_group_by = []
            for hide_filter_group_by_rec in rec.hide_filters_groups_ids:
                filters_attribute = []
                groups_attribute = []

                for filter_attribute in hide_filter_group_by_rec.filters_store_model_nodes_ids:
                    filters_attribute.append({
                        "string": filter_attribute.attribute_string,
                        "name": filter_attribute.attribute_name
                    })

                for group_attribute in hide_filter_group_by_rec.groups_store_model_nodes_ids:
                    groups_attribute.append({
                        "string": group_attribute.attribute_string,
                        "name": group_attribute.attribute_name
                    })

                hide_filter_group_by.append({"model": {
                    "name": hide_filter_group_by_rec.model_id.name,
                    'model': hide_filter_group_by_rec.model_id.model},
                    "filters_store_model_nodes_ids": filters_attribute,
                    "group_store_model_nodes_ids": groups_attribute
                })

            chatter = []
            for chatter_rec in rec.hide_chatter_ids:
                chatter.append({
                    "model": {"name": chatter_rec.model_id.name, 'model': chatter_rec.model_id.model},
                    "hide_chatter": True if chatter_rec.hide_chatter else False,
                    "hide_send_mail": True if chatter_rec.hide_send_mail else False,
                    "hide_log_notes": True if chatter_rec.hide_log_notes else False,
                    "hide_schedule_activity": True if chatter_rec.hide_schedule_activity else False,
                })

            data = {
                "name": rec.name,
                "user_ids": user_name,
                "readonly": True if rec.readonly else False,
                "disable_debug_mode": True if rec.disable_debug_mode else False,
                "menu": menu_data,
                "model_access": model_access_data,
                "field_access": field_access,
                "domain_access": domain_access,
                "button_and_tab_access": button_tab_access,
                "hide_filter_group_by": hide_filter_group_by,
                "chatter": chatter,
                "global": [{
                    "hide_chatter": True if rec.hide_chatter else False,
                    "hide_send_mail": True if rec.hide_send_mail else False,
                    "hide_log_notes": True if rec.hide_log_notes else False,
                    "hide_schedule_activity": True if rec.hide_schedule_activity else False,
                    "hide_import": True if rec.hide_import else False,
                    "hide_export": True if rec.hide_export else False
                }]
            }

            main_data.update({rec.name: data})

        json_data = json.dumps(main_data, indent=4)
        binary_data = base64.b64encode(json_data.encode('utf-8'))

        record = self.env['ir.attachment'].create({
            'name': 'simplify.json',
            'type': 'binary',
            'datas': binary_data,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(
                record.id) + "&filename_field=name&field=datas&download=true&name=" + record.name,
            'target': 'self',
        }
    # def xyz(self):
    #     pass
