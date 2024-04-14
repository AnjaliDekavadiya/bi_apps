# -*- coding: utf-8 -*-


import logging
import xml.etree.ElementTree as ET

from pathlib import Path

_logger = logging.getLogger(__name__)

try:
    import six
    from owncloud import Client as OwncloudClient, FileInfo, ShareInfo, HTTPResponseError
    from six.moves.urllib import parse
except ImportError as e:
    _logger.error(e)
    OwncloudClient = object
    FileInfo = object
    ShareInfo = object

# under no circumstnaces do not add spaces after or before xml
PROPFIND_DATA = """<?xml version="1.0"?>
    <d:propfind xmlns:d="DAV:" xmlns:nc="http://nextcloud.org/ns" xmlns:oc="http://owncloud.org/ns">
        <d:prop>
            <oc:fileid />
            <d:getcontenttype />
        </d:prop>
    </d:propfind>"""


class FileInfo(FileInfo):
    """
    Re-write class to add methods
    """
    def get_file_id(self):
        """
        The method to get OwnCloud ID
        """
        return self.attributes.get("{http://owncloud.org/ns}fileid")

    def get_file_dict(self):
        """
        The method to retrieve essential for connector params:
         * id, file_name, url, path

        Returns:
         * dict of values
        """
        result = {
            "id": self.get_file_id(),
            "name": self.name,
            "path": self.path,
            "mimetype": self.file_type == "dir" and self.file_type or self.attributes.get("{DAV:}getcontenttype"),
        }
        return result


class PatchedClient(OwncloudClient):
    """
    Re-write class to extend / replace its methods

    Extra info:
     * The method "SEARCH" for requests is not implemented (501) for owncloud (but for nextcloud seemingly does)
     * The method "REPORT" is not totally fine for that
    """
    _cache = []

    def list_owncloud_fix_28341(self, path, first_path=False):
        """
        Recursion method to get all children
           The method is introduced due to quite old bug which is seemed to be fixed, but we anyway support that
           List_o doesn't work properly with depth > 1 in OwnCloud.
           Look at the issue: https://github.com/owncloud/core/issues/28341
           So, if ID is repeated, we just get through all children what is drastically bad for peformace
           Seemed to be fixed very long ago to keep its support (from the v.10.1.0 about nov 2018)

        Args:
         * path - char
         * first_path - bool - True if it is the first recursion

        Methods:
         * list_owncloud_fix_28341

        Returns:
         * list of dict
        """
        headers = {"Depth": str(1)}
        res = self._make_dav_request(
            "PROPFIND",
            path,
            headers=headers,
            data=PROPFIND_DATA,
        )
        if not first_path:
            res = res[1:] # to avoid including current path to the list; the very root however should be inside
        result = []
        for child in res:
            child_file_info = child.get_file_dict()
            result.append({
                "id": child_file_info.get("id"),
                "path": child_file_info.get("path"),
                "name": child_file_info.get("name"),
                "mimetype": child_file_info.get("mimetype"),
                "child_items": [],
                "parent_id": False,
            })
            if path != child_file_info.get("path") and child_file_info.get("mimetype") == "dir":
                child_res = self.list_owncloud_fix_28341(child_file_info.get("path"))
                result += child_res
        return result

    def list_owncloud(self, path, depth="infinity"):
        """
        The method to return all items within the root folder to find proper pathes by id
        Since we cannot work with real ID of id, we list all of those to construct the list of dicts
         * "item_ID": [{}, {}]
        Our best wish in such a sense becomes to do that only once and user in all snapshots checks afterwards

        Args:
         * path - char
         * depth - "infinity" (char) or integer

        Methods:
         * list_owncloud_fix_28341

        Returns:
         * dict
        """
        if not path.endswith("/"):
            path += "/"

        headers = {}
        if isinstance(depth, int) or depth == "infinity":
            headers["Depth"] = str(depth)
        result = []
        try:
            res = self._make_dav_request(
                "PROPFIND",
                path,
                headers=headers,
                data=PROPFIND_DATA,
            )
            checked_ids = [] # introduced only for the issue list_owncloud_fix_28341
            for child in res:
                child_file_info = child.get_file_dict()
                if child_file_info.get("id") in checked_ids:
                    # introduced only for the issue list_owncloud_fix_28341
                    result = self.list_owncloud_fix_28341(path, True)
                    break
                result.append({
                    "id": child_file_info.get("id"),
                    "path": child_file_info.get("path"),
                    "name": child_file_info.get("name"),
                    "mimetype": child_file_info.get("mimetype"),
                    "child_items": [],
                    "parent_id": False,
                })
                checked_ids.append(child_file_info.get("id"))
        except:
            result = self.list_owncloud_fix_28341(path, True)
        # format dict to list of dicts by id and calculate parent
        # we do that in a separate loop to avoid too many conversions from file info to dict
        result_dict = {}
        for child in result:
            own_path = child.get("path")
            parent_path = str(Path(own_path).parent)
            if not parent_path.endswith("/"):
                parent_path += "/"
            for second_search in result:
                if second_search.get("path") == parent_path:
                    second_search["child_items"].append(child.get("id"))
                    child["parent_id"] = second_search.get("id")
                    break
            result_dict.update({child.get("id"): child})
        return result_dict

    def file_info_owncloud(self, path):
        """
        Copy method file_info to format dav request to proper dict

        Args:
         * path - char

        Methods:
         * get_file_dict

        Returns:
         * file info for the given remote file (class:`FileInfo`)
        """
        res = self._make_dav_request("PROPFIND", path, headers={"Depth": "0"}, data=PROPFIND_DATA)
        result = None
        if res:
            result_fileinfo = res[0]
            result = result_fileinfo.get_file_dict()
            if self.share_urls:
                url = self.get_url(path=result.get("path"))
            else:
                url = "{}index.php/f/{}".format(self.url, result.get("id"))
            result.update({"url": url})
        return result

    def find_item_by_cloud_key(self, path, cloud_key):
        """
        The method to find path by cloud_key

        Args:
         * path - char - "Odoo" folder path
         * cloud_key - char

        Methods:
         * list_owncloud

        Returns:
         * dict
        """
        all_children = self.list_owncloud(path, "infinity")
        citem = all_children.get(cloud_key)
        return citem

    def _parse_dav_element(self, dav_response):
        """
        The method is repeated to add FileInfo methods
        It is absolutely the same as in the lib

        Return an instance of the modified FileInfo class
        """
        href = parse.unquote(
            self._strip_dav_path(dav_response.find("{DAV:}href").text)
        )
        if six.PY2:
            href = href.decode("utf-8")
        file_type = "file"
        if href[-1] == "/":
            file_type = "dir"
        file_attrs = {}
        attrs = dav_response.find("{DAV:}propstat")
        attrs = attrs.find("{DAV:}prop")
        for attr in attrs:
            file_attrs[attr.tag] = attr.text
        return FileInfo(href, file_type, file_attrs)

    def get_url(self, path):
        """
        The method to generate a share url if public links are turned on
        """
        existing_shares = self.get_shares(path)
        if existing_shares:
            res = existing_shares[0].get_link()
        else:
            res = self.share_file_with_link_o(path).get_link()
        return res

    def share_file_with_link_o(self, path, **kwargs):
        """
        Have own method to construct share, since library has the bug of parsing data for NextCloud
        """
        path = self._normalize_path(path)
        post_data = {"shareType": self.OCS_SHARE_TYPE_LINK, "path": self._encode_string(path)}
        res = self._make_ocs_request(
            "POST",
            self.OCS_SERVICE_SHARE,
            "shares",
            data=post_data
        )
        if res.status_code == 200:
            tree = ET.fromstring(res.content)
            self._check_ocs_status(tree)
            data_el = tree.find("data")
            return ShareInfo({"id": data_el.find("id").text, "path": path, "url": data_el.find("url").text})
        raise HTTPResponseError(res)
