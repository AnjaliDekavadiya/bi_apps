# -*- coding: utf8 -*-

from odoo import api, fields, models, _

VKS_ADMIN_EMPLOYEE_ID = 1
VKS_ADMIN_US_ID = 2

#----------------------------Định nghĩa các ký tự đặc biệt dùng chung---------------------------------------------------

VKS_SPLIT_XML_ID_CHAR = '.'
VKS_NORMAL_NEW_LINE_CHAR = '\n'
VKS_HTML_NEW_LINE_CHAR = '<br>'
VKS_XHTML_NEW_LINE_CHAR = '<br/>'
VKS_HTML_ONE_SPACE_CHAR = '&nbsp;'
VKS_HTML_ONE_TAB_CHAR = '&nbsp;&nbsp;&nbsp;&nbsp;'
VKS_HTML_SIGN_NULL_STR = """<p class="vks-report-common-sign-title-to-name"></p>"""
VKS_CURRENCY_RATE_DIGITS = (12, 10)
VKS_MONEY_AMOUNT_DIGITS = (18, 4)
VKS_FLOAT_TIME_FIELD_ROUND_DIGIT = 4
VKS_STR_SPLIT_MANY2MANY_VALUES = ','
VKS_STR_SPLIT_MODULE_IN_PATH = ':::'
VKS_EXPORT_EXCEL_CELL_WIDTH = 31

#----------------------------Định nghĩa các cảnh báo dữ liệu dùng chung---------------------------------------------------
        
VKS_STR_NAME_UNIQUE_ERROR =  _('Name must be unique. Please check again!')
VKS_STR_CODE_UNIQUE_ERROR =  _('Code must be unique. Please check again!')
VKS_STR_DATA_UNIQUE_ERROR =  _('This data has been saved. Please check again!')
VKS_STR_METHOD_NOT_DEF_ERROR =  _('The function %s has not been defined. Please check again!')

#----------------------------Định nghĩa các loại lỗi dùng chung---------------------------------------------------

VKS_STR_WARNING =  _('Warning')
VKS_STR_ERROR =  _('Error')
VKS_STR_VALIDATE_ERROR =  _('Data validation error')
VKS_STR_ATT_NOT_FOUND = _('The file may have been deleted from the system') 
VKS_STR_INVALID_ACTION_ERROR =  _('Invalid action')

#----------------------------Định nghĩa các ghi chú cho việc tạo file import dùng chung---------------------------------------------------

VKS_STR_IMPORT_EMP_CARD_DES = 'Employee code or employee card number'
VKS_STR_IMPORT_APPROVER_DES = 'Employee code or employee card number of approver'
VKS_STR_IMPORT_CAN_REMOVE_COLUMN = 'This column can be removed when importing to avoid data errors and speed up processing'
VKS_STR_IMPORT_COLUMN_REQUIRED = 'Required to enter value'

#----------------------------Định nghĩa help cho các field dùng chung---------------------------------------------------

VKS_STR_ACTIVE_HELP = 'If unchecked, this record is only visible in advanced search mode'

#----------------------------Định nghĩa các selection dùng chung---------------------------------------------------

VKS_STATE_THREAD_LIST = [('to_do', 'Unprocessed'), ('doing', 'Processing'), ('done', 'Done'),('error', 'Error handling')]

VKS_STATUS_PROCESS_COMMON = [('success','Success'),('fail','Fail')]