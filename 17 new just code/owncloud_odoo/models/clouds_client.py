# -*- coding: utf-8 -*-

import werkzeug.exceptions

from odoo import api, fields, models

from ..libs.owncloud_service import PatchedClient as OwncloudClient

ROOT_404 = "404: The root folder was not found in the clouds"
FOLDER_404 = "404: The folder was not found in the clouds"
ATTACHMENT_404 = "404: The attachment was not found in the clouds"
FILE_404 = "404: The file was not found in the clouds"


class clouds_client(models.Model):
    """
    Overwrite to add Dropbox methods
    """
    _inherit = "clouds.client"

    cloud_client = fields.Selection(
        selection_add=[("owncloud", "ownCloud"),("nextcloud", "Nextcloud"),],
        required=True,
        ondelete={"owncloud": "cascade", "nextcloud": "cascade"},
    )
    owncloud_url = fields.Char(string="ownCloud/Nextcloud URL")
    owncloud_login = fields.Char(string="ownCloud/Nextcloud login")
    owncloud_password = fields.Char(string="ownCloud/Nextcloud password")
    owncloud_share_urls = fields.Boolean(
        string="Use public URLs",
        help="""By default, all links from Odoo to ownCloud/Nextcloud are internal. Only real users may access them and\
then generate shared URLs for others.
If this option is checked, links will become 'shared', meaning that everybody will access those files through the\
links. Although such links will be hardly known by external users, there is a slight chance that they become available
as a result of some user actions. Besides, sharing links generation is not fast and might make the sync slower""",
    )

    def action_owncloud_establish_connection(self):
        """
        The method to establish connection for ownCloud/Nextcloud URL

        Methods:
         * _return_specific_client_context
         * _owncloud_root_directory
         * _cloud_log

        Returns:
         * True: updated cloud form would be shown

        Extra info:
         * Expected singleton
        """
        ctx = self.env.context.copy()
        this_client_ctx = self._return_specific_client_context()
        if not this_client_ctx.get("cclients"):
            log_message = "Could not finish authentication since client could not be initiated"
            self._cloud_log(False, log_message)
            self.error_state = log_message
        else:
            ctx.update(this_client_ctx)
            root_dir = self.with_context(ctx)._owncloud_root_directory()
            if not root_dir:
                log_message = "Client was not confirmed since root folder could not be created"
                self._cloud_log(False, log_message)
                self.error_state = log_message
            else:
                self.state = "confirmed"
                self.error_state = False
                self._cloud_log(True, "Client was succesfully confirmed")
        return True

    ####################################################################################################################
    ##################################   API methods   #################################################################
    ####################################################################################################################
    def _owncloud_get_client(self):
        """
        Method to return instance of wrapped ownCloud/Nextcloud instance

        Methods:
         * _cloud_log

        Returns:
         * tuple
          ** OwnCloud instance if initiated.False otherwise
          ** char

        Extra info:
         * Expected singleton
        """
        log_message = ""
        self._cloud_log(True, "The process of initiating the client was started", "DEBUG")
        try:
            api_client = OwncloudClient(self.owncloud_url)
            api_client.login(self.owncloud_login, self.owncloud_password)
            api_client.share_urls = self.owncloud_share_urls
            log_message = "Succesful login"
        except Exception as er:
            api_client = False
            log_message = "The client cannot be initiated. Reason: {}. Try to reconnect".format(er)
        self._cloud_log(api_client and True or False, log_message)
        return api_client, log_message

    def _owncloud_return_root_child_ids(self, client_id):
        """
        The method to return the list of all current items within the root folder

        Args:
         * client_id - instance of OwncloudClient

        Methods:
         * _owncloud_find_odoo_folder_path
         * list_owncloud of OwncloudClient

        Returns:
         * dict:
          ** key - id of a current client
          ** dict - of child elements
         * char

        Extra info:
         * IMPORTANT NOTE: here client is passed in args, not in context, since context is not yet updated
         * Expected singleton
        """
        child_items = {}
        log_message = ""
        odoo_path = self._owncloud_find_odoo_folder_path(client_id, self.root_folder_key)
        if not odoo_path:
            child_items = {}
            log_message = "The client cannot be initiated. Reason: the root folder has been deleted"
        else:
            child_items = client_id.list_owncloud(path=odoo_path, depth="infinity")
        return {self.id: child_items}, log_message

    def _owncloud_check_api_error(self, error):
        """
        The method to get an error type based on response

        Args:
         * error class related to API

        Retunes:
         * int
        """
        error_type = 400
        if (hasattr(error, "status_code") and error.status_code == 404) \
                or (hasattr(error, "code") and error.code == 404):
            error_type = 404
        return error_type

    def _owncloud_find_odoo_folder_path(self, client_id, odoo_key):
        """
        The method to get Odoo folder path based on its key

        Args:
         * client_id - OwnCloud Service
         * odoo_key - char

        Returns:
         * char
        """
        root_children = client_id.list_owncloud(path="/", depth=1)
        return root_children.get(odoo_key) and root_children.get(odoo_key).get("path") or False

    def _owncloud_root_directory(self):
        """
        Method to return root directory name and id (create if not yet)

        Methods:
         * _owncloud_find_odoo_folder_path
         * _check_api_error
         * file_info_o of OwncloudClient
         * mkdir of OwncloudClient
         * _cloud_log

        Returns:
         * key, name - name of folder and key in client
         * False, False if failed
        """
        client = self._context.get("cclients", {}).get(self.id)
        res_id = self.root_folder_key
        res = False
        if res_id:
            try:
                #in try, since the folder might be removed in meanwhile
                odoo_path = self._owncloud_find_odoo_folder_path(client, res_id)
                if odoo_path:
                    res = True
                    self._cloud_log(True, "The root directory {},{} was successfully found".format(
                        self.root_folder_name, self.root_folder_key
                    ))
                else:
                    res_id = False
                    self._cloud_log(
                        False,
                        "The root directory {}{} was removed from the clouds. Creating a new one".format(
                            self.root_folder_name, self.root_folder_key
                        ),
                        "WARNING",
                    )
            except Exception as error:
                if self._check_api_error(error) == 404:
                    # this seems excess since there should not be 404 error while searching the root folder
                    res_id = False # to guarantee creation of item
                    self._cloud_log(
                        False,
                        "The root directory {}{} was removed from the clouds. Creating a new one".format(
                            self.root_folder_name, self.root_folder_key
                        ),
                        "WARNING",
                    )
                else:
                    res_id = True # to guarantee no creation of item
                    res = False
                    self._cloud_log(False, "Unexpected error while searching the root directory {},{}: {}".format(
                        self.root_folder_name, self.root_folder_key, error
                    ))
                    return res
        if not res_id:
            root_path = self.root_folder_name
            try:
                res_id = client.mkdir(root_path)
                metadata = client.file_info_owncloud(root_path)
                self.root_folder_key = metadata.get("id")
                res = res_id
                self._cloud_log(True, "The root directory {} was successfully created".format(self.root_folder_name))
            except Exception as error:
                res = False
                self._cloud_log(
                    False,
                    "Unexpected error during the root directory {} creation: {}".format(self.root_folder_name, error)
                )
        return res and True or False

    def _owncloud_api_get_child_items(self, cloud_key=False):
        """
        The method to retrieve all child elements for a folder
        Note: If folder was removed, all its children were removed as well

        Args:
         * cloud_key - char

        Returns:
         * dict:
          ** folder_ids
          ** attachment_ids
           *** cloud_key - char (cloud key)
           *** name - char
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        attachments = []
        subfolders = []
        this_folder = cclient_items.get(cloud_key)
        if not this_folder:
            raise werkzeug.exceptions.NotFound(FOLDER_404)
        for ckey in this_folder.get("child_items"):
            child = cclient_items.get(ckey) # this should be always there, since child_items are calced simultaneously
            res_vals = {"cloud_key": child.get("id"),"name": child.get("name"),}
            if child.get("parent_id") == cloud_key:
                if child.get("mimetype") == "dir":
                    subfolders.append(res_vals)
                else:
                    attachments.append(res_vals)
        return {"folder_ids": subfolders, "attachment_ids": attachments}

    def _owncloud_upload_attachment_from_cloud(self, folder_id, attachment_id, cloud_key, args):
        """
        Method to upload a file from cloud
        IMPORTANT: the method is assumed to be triggered only stand-alone (outside of the cron), so we do not have
        cclient_items there in context

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * get_file_contents of OwncloudClient
         * _owncloud_find_odoo_folder_path
         * find_item_by_cloud_key of OwncloudClient

        Returns:
         * binary (base64 decoded)
         * False if method failed
        """
        result = False
        client = self._context.get("cclients", {}).get(self.id)
        try:
            result = client.get_file_contents(attachment_id.owncloud_path)
        except:
            root_path = self._owncloud_find_odoo_folder_path(client, self.root_folder_key)
            if not root_path:
                raise werkzeug.exceptions.NotFound(ROOT_404)
            citem = client.find_item_by_cloud_key(root_path, attachment_id.cloud_key)
            if not citem:
                raise werkzeug.exceptions.NotFound(ROOT_404)
            result = client.get_file_contents(citem.get("path"))
        return result

    def _owncloud_prepare_path(self, target_name, parent_key):
        """
        The method to check existing folder children and if duplicate - amend the name

        Args:
         * target_name - char - name of created item
         * parent_key - char - key of parent element

        Methods:
         * _build_path

        Returns:
         * char
        """
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        parent_citem = cclient_items.get(parent_key)
        if not parent_citem:
            raise werkzeug.exceptions.NotFound(ROOT_404)
        existing_children = parent_citem.get("child_items")
        duplicated_paths_check_ids = [cclient_items.get(child).get("path") for child in existing_children]
        new_folder_path = self._build_path([parent_citem.get("path"), target_name])
        itera = 1
        while (new_folder_path in duplicated_paths_check_ids) or (new_folder_path+"/" in duplicated_paths_check_ids):
            new_folder_path = self._build_path([parent_citem.get("path"), "({}) {}".format(itera, target_name)])
            itera += 1
        return new_folder_path

    def _owncloud_update_context_citems(self, operation="add", cdata={}, parent_key=False):
        """
        The method to update citems to be used in further requests

        Args:
         * operation - char: "add", "update", "remove"
         * cdata - dict (fielinfo attriibutes)
         * parent_key - char - id of the parent citem

        Returns:
         * bool

        Extra info:
         * we do all .get checks for extreme cases of concurrent changes in Odoo and clouds (and for safety)
        """
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        if not cdata.get("id"):
            return False
        if operation == "add":
            cclient_items.update({cdata.get("id"): {
                "id": cdata.get("id"),
                "path": cdata.get("path"),
                "name": cdata.get("name"),
                "mimetype": cdata.get("mimetype"),
                "child_items": [],
                "parent_id": parent_key,
            }})
            if cclient_items.get(parent_key) is not None \
                    and cclient_items.get(parent_key).get("child_items") is not None:
                cclient_items[parent_key]["child_items"].append(cdata.get("id"))
        elif cclient_items.get(cdata.get("id")) is not None:
            this_element = cclient_items.get(cdata.get("id"))
            if this_element is None:
                return False
            old_parent_key = this_element["parent_id"]
            if operation == "update":
                this_element.update({
                    "path": cdata.get("path"),
                    "name": cdata.get("name"),
                    "parent_id": parent_key,
                })
                if old_parent_key != parent_key:
                    if old_parent_key and cclient_items.get(old_parent_key) is not None \
                            and cclient_items.get(old_parent_key).get("child_items") is not None \
                            and cdata.get("id") in cclient_items.get(old_parent_key).get("child_items"):
                        cclient_items[old_parent_key]["child_items"].remove(cdata.get("id"))
                    if parent_key and cclient_items.get(parent_key) is not None \
                            and cclient_items.get(parent_key).get("child_items") is not None:
                        cclient_items[parent_key]["child_items"].append(cdata.get("id"))
            elif operation == "remove":
                del this_element
                if old_parent_key and cclient_items.get(old_parent_key) is not None \
                        and cclient_items.get(old_parent_key).get("child_items") is not None \
                        and cdata.get("id") in cclient_items.get(old_parent_key).get("child_items"):
                    cclient_items[old_parent_key]["child_items"].remove(cdata.get("id"))
        return True

    def _owncloud_setup_sync(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to create folder in clouds

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)
         * args should contain "parent_key"

        Methods:
         * _owncloud_prepare_path
         * mkdir of OwncloudClient
         * file_info_owncloud of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
         * dict of values to write in clouds.folder

        Extra info:
         * setup sync assumes that a folder does not exist in client. If a folder was previously deactivated,
           it was just deleted from clouds
        """
        result =  False
        client = self._context.get("cclients", {}).get(self.id)
        parent_key = args.get("parent_key")
        new_folder_path = self._owncloud_prepare_path(folder_id.name, parent_key)
        client.mkdir(new_folder_path)
        cdata = client.file_info_owncloud(new_folder_path)
        result = {"cloud_key": cdata.get("id"), "url": cdata.get("url")}
        self._owncloud_update_context_citems("add", cdata, parent_key)
        return result

    def _owncloud_update_folder(self, folder_id, attachment_id, cloud_key, args):
        """
        Method to update folder in clouds

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)
         * in args we should receive parent_key

        Methods:
         * _owncloud_prepare_path
         * move of OwncloudClient
         * file_info_owncloud of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
         * dict of values to write in clouds folder
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        old_folder = cclient_items.get(folder_id.cloud_key)
        if not old_folder:
            raise werkzeug.exceptions.NotFound(FOLDER_404)
        parent_key = args.get("parent_key")
        new_folder_path = self._owncloud_prepare_path(folder_id.name, parent_key)
        if new_folder_path != old_folder.get("path"):
            client.move(old_folder.get("path"), new_folder_path)
        cdata = client.file_info_owncloud(new_folder_path)
        result = {"cloud_key": cdata.get("id"), "url": cdata.get("url")}
        self._owncloud_update_context_citems("update", cdata, parent_key)
        return result

    def _owncloud_delete_folder(self, folder_id, attachment_id, cloud_key, args):
        """
        Method to delete folder in clouds
        The method is triggered directly from _adapt_folder_reverse (cloud_client does not have _delete_folder)
        UNDER NO CIRCUMSTANCES DO NOT DELETE THIS METHOD

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * delete of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
          * bool
        """
        result = False
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        old_folder = cclient_items.get(folder_id.cloud_key)
        if not old_folder:
            raise werkzeug.exceptions.NotFound(FOLDER_404)
        result = client.delete(old_folder.get("path"))
        self._owncloud_update_context_citems("remove", {"id": folder_id.cloud_key}, False)
        return result and True or False

    def _owncloud_upload_file(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to upload file to clouds

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)
         * args should contain attach_name

        Methods:
         * _owncloud_prepare_path
         * _full_path of ir.attachment
         * put_file of OwncloudClient
         * file_info_owncloud of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
         * dict of values to write in ir.attachment
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        parent_key = folder_id.cloud_key
        new_attachment_path = self._owncloud_prepare_path(args.get("attach_name"), parent_key)
        local_path = attachment_id._full_path(attachment_id.store_fname)
        upload = client.put_file(new_attachment_path, local_path)
        cdata = client.file_info_owncloud(new_attachment_path)
        result = {
            "cloud_key": cdata.get("id"),
            "owncloud_path": cdata.get("path"),
            "url": cdata.get("url"),
            "type": "url",
            "sync_cloud_folder_id": folder_id.id,
            "sync_client_id": self.id,
        }
        self._owncloud_update_context_citems("add", cdata, parent_key)
        return result

    def _owncloud_update_file(self, folder_id, attachment_id, cloud_key, args):
        """
        Method to update file in clouds

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)
         * Args should contain attach_name

        Methods:
         * _owncloud_prepare_path
         * move of OwncloudClient
         * file_info_owncloud of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
         * dict to write in attachment
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        old_attachment = cclient_items.get(attachment_id.cloud_key)
        if not old_attachment:
            raise werkzeug.exceptions.NotFound(ATTACHMENT_404)
        parent_key = folder_id.cloud_key
        new_attachment_path = self._owncloud_prepare_path(args.get("attach_name"), parent_key)
        if new_attachment_path != old_attachment.get("path"):
            client.move(old_attachment.get("path"), new_attachment_path)
        cdata = client.file_info_owncloud(new_attachment_path)
        result = {
            "cloud_key": cdata.get("id"),
            "owncloud_path": cdata.get("path"),
            "url": cdata.get("url"),
            "sync_cloud_folder_id": folder_id.id,
            "sync_client_id": self.id,
        }
        self._owncloud_update_context_citems("update", cdata, parent_key)
        return result

    def _owncloud_delete_file(self, folder_id, attachment_id, cloud_key, args):
        """
        Method to delete file in clouds

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * delete of OwncloudClient
         * _owncloud_update_context_citems

        Returns:
          * bool

        Extra info:
         * for non-documented reasons succesfull deletion results in 204 error. So, missing error is totally fine
        """
        result = False
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        old_attachment = cclient_items.get(attachment_id.cloud_key)
        if not old_attachment:
            raise werkzeug.exceptions.NotFound(ATTACHMENT_404)
        result = client.delete(old_attachment.get("path"))
        self._owncloud_update_context_citems("remove", {"id": attachment_id.cloud_key}, False)
        return result and True or False

    def _owncloud_create_subfolder(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to create clouds.folder in Odoo based on cloud client folder info

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * file_info_owncloud of OwncloudClient

        Returns:
          * dict of clouds.folder values
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        new_folder = cclient_items.get(cloud_key)
        if not new_folder:
            raise werkzeug.exceptions.NotFound(FOLDER_404)
        cdata = client.file_info_owncloud(new_folder.get("path"))
        result = {
            "cloud_key": cloud_key,
            "name": cdata.get("name"),
            "parent_id": folder_id.id,
            "own_client_id": self.id,
            "active": True,
            "url": cdata.get("url"),
        }
        return result

    def _owncloud_create_attachment(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to create ir.attachment in Odoo based on cloud client file info

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * file_info_owncloud of OwncloudClient

        Returns:
          * dict of ir.attachment values
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        new_attachment = cclient_items.get(cloud_key)
        if not new_attachment:
            raise werkzeug.exceptions.NotFound(FILE_404)
        cdata = client.file_info_owncloud(new_attachment.get("path"))
        result = {
            "cloud_key": cloud_key,
            "name": cdata.get("name"),
            "url": cdata.get("url"),
            "owncloud_path": cdata.get("path"),
            "clouds_folder_id": folder_id.id,
            "sync_cloud_folder_id": folder_id.id,
            "sync_client_id": self.id,
            "type": "url",
            "mimetype": cdata.get("mimetype"),
        }
        return result

    def _owncloud_change_attachment(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to write on ir.attachment in Odoo based on cloud client file info

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * file_info_owncloud of OwncloudClient

        Returns:
          * dict of ir.attachment values
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        new_attachment = cclient_items.get(cloud_key)
        if not new_attachment:
            raise werkzeug.exceptions.NotFound(FOLDER_404)
        cdata = client.file_info_owncloud(new_attachment.get("path"))
        result = {
            "name": cdata.get("name"),
            "url": cdata.get("url"),
            "owncloud_path": cdata.get("path"),
        }
        return result

    def _owncloud_attachment_reverse(self, folder_id, attachment_id, cloud_key, args):
        """
        The method to create ir.attachment in Odoo based on cloud client file info

        Args:
         * the same as for _call_api_method of clouds.client (cloud.base)

        Methods:
         * file_info_owncloud of OwncloudClient
         * get_file_contents of OwncloudClient

        Returns:
          * dict of ir.attachment values

        Extra info:
         * IMPORTANT: mimetype should NOT be written here, since we already do that in backward sync creation.
           Otherwise, there might be conflicts
        """
        client = self._context.get("cclients", {}).get(self.id)
        cclient_items = self._context.get("cclient_items", {}).get(self.id)
        new_attachment = cclient_items.get(cloud_key)
        if not new_attachment:
            raise werkzeug.exceptions.NotFound(FILE_404)

        cdata = client.file_info_owncloud(new_attachment.get("path"))
        # IMPORTANT: do not write clouds_folder_id. It would break attachments moves
        result = {
            "cloud_key": False,
            "name": cdata.get("name"),
            "url": False,
            "owncloud_path": False,
            "type": "binary",
            "sync_cloud_folder_id": False,
            "sync_client_id": False,
        }
        binary_content = client.get_file_contents(new_attachment.get("path"))
        result.update({"raw": binary_content})
        return result
