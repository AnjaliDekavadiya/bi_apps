# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
import requests

_logger = logging.getLogger(__name__)

__version__ = '1.0.0'

class ZohoApi:
    def __init__(self, access_token, zoho_organization_id,
            debug='False',
            **extra
        ):
        self.header = {
            "Authorization": f"Zoho-oauthtoken {access_token}"
        }
        self.debug = debug
        self.zoho_organization_id = zoho_organization_id
        self.api_url = f"https://books.zoho.{extra.get('domain')}/api/v3" if extra.get('domain') else "https://books.zoho.com/api/v3"

    def add_organization_id(func):
        def wrapper(self, resource, **kwargs):
            resource_id = kwargs.get('resource_id')
            if resource_id:
                kwargs.update(resource_id = f'{resource_id}?organization_id={self.zoho_organization_id}')
            else:
                resource = f'{resource}?organization_id={self.zoho_organization_id}'
            return func(self, resource, **kwargs)
        return wrapper

    def format_get_error(self, error:str)->str:
        if error.get('message'):
            return f"{error.get('message','')}"
        return f"{error.get('Detail', '')}"
    
    def format_put_error(self, error:str)->str:
        if error.get('message'):
            return error.get('message')
        return f"({error.get('Type')}) {error.get('Elements')[0].get('ValidationErrors')[0].get('Message')}"

    @add_organization_id
    def get(self, resource:str, params={}, resource_id="", headers={})->dict:
        result = {'json':None, "f_error" :"something went wrong ..."}
        try:
            with requests.Session() as s:
                url = self.api_url + f'/{resource}'
                if resource_id:
                    url+=f'/{resource_id}'
                result['url'] = url
                if headers:
                    self.header.update(headers)
                response = s.get(url, headers=self.header, params=params)
                # result['text'] = response.text
                result['status_code'] = response.status_code or ''
                response = response.json()
                if result["status_code"] in  [200, 201]:
                    result['json'] = response
                else:
                    result["f_error"] = self.format_get_error(response)
                    result["error"] = response
                    if self.debug:
                        _logger.info(response)
        except Exception as e:
            result['error'] = result["f_error"] = e.args[0]
        return result
        
    @add_organization_id
    def post(self, resource:str, json={}, fetch_token=False, data='', headers = {})->dict:
        result = {'json':None}
        try:
            with requests.Session() as s:
                if fetch_token:
                    url = self.api_url
                else:
                    url = self.api_url
                url += f'/{resource}'
                result['url'] = url
                if headers:
                    self.header.update(headers)
                response = s.post(url, headers=self.header, json=json, data=data)
                # result['text'] = response.text
                result['status_code'] = response.status_code
                response = response.json()
                if result["status_code"] in [200, 201]:
                    result['json'] = response
                else:
                    result['f_error'] = self.format_put_error(response)
                    result["error"] = response
                    if self.debug:
                        _logger.info(response)
        except Exception as e:
            result['error'] = result['f_error'] = e.args[0]
        return result

    def put(self, resource:str, resource_id="", json={}, data='')->dict:
        result = {'json':None}
        method = 'put'
        try:
            with requests.Session() as s:
                url = self.api_url + f'/{resource}'
                result['url'] = url
                if resource_id:
                    url+=f'/{resource_id}'
                response = getattr(s, method)(url, headers=self.header, json=json, data=data)
                # result['text'] = response.text
                result['status_code'] = response.status_code
                response = response.json()
                if result['status_code'] in [200, 201]:
                    result['json'] = response
                else:
                    result["f_error"] = self.format_put_error(response)
                    result["error"] = response
                    if self.debug:
                        _logger.info(response)
        except Exception as e:
            result['error'] = result['f_error'] = e.args[0]
        return result

    def delete(self, resource:str, resource_id:str)->dict:
        result = {'json':None}
        try:
            with requests.Session() as s:
                url = self.api_url + f'/{resource}'
                result['url'] = url
                if resource_id:
                    url+=f'/{resource_id}'
                response = s.delete(url, headers=self.header)
                # result['text'] = response.text
                result['status_code'] = response.status_code

                if response.status_code in [200, 201]:
                    result['json'] = response.json().get('data')
                else:
                    err_msg = response.json().get('message', '')
        except:
            pass
        return result
