# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from .common_const import *
import collections
import contextlib

class BaseModel(models.AbstractModel):
    _inherit = 'base'
    
    #Thêm bởi Tuấn - 16/10/2023 - Hàm kiểm tra xem 1 field binary có phải dạng ảnh hay không
    @api.model
    def vks_get_binary_field_export_param(self,m_model_name,m_field_name):
        tmp_b_type = 'unknow'
        tmp_b_mode = 'url'
        tmp_lst = ['image','avatar','picture','thumbnail','icon','logo']
        for child_e in tmp_lst:
            if child_e in m_field_name:
                tmp_b_type = 'image'
                break
        try:
            r_binary_fields = self.env['manage.field.import'].search([('manage_id.model_id.model','=',m_model_name),
                                                                          ('name','=',m_field_name),
                                                                          ('type','=','byte_str')],limit=1)
            if r_binary_fields:
                tmp_b_mode = 'content'
        except Exception as e:
            tmp_b_mode = 'url'
        return {'b_type':tmp_b_type,'b_mode':tmp_b_mode}
    
    #Thêm bởi Tuấn - 14/10/2023 - Hàm lấy chế độ hiển thị khi export của 1 field many2many
    @api.model
    def vks_get_many2many_export_mode(self,m_model_name,m_field_name):
        tmp_mode = 'one_line'
        try:
            tmp_manyline_fields = self.env['manage.field.import'].search([('manage_id.model_id.model','=',m_model_name),
                                                                          ('name','=',m_field_name),
                                                                          ('type','=','many2many')],limit=1)
            if tmp_manyline_fields:
                tmp_mode = 'many_line'
        except Exception as e:
            tmp_mode = 'one_line'
        return tmp_mode
    
    #Thêm bởi Tuấn - 06/11/2023 - Ghi đè hàm của Odoo
    def _export_rows(self, fields, *, _is_toplevel_call=True):
        """ Export fields of the records in ``self``.

        :param list fields: list of lists of fields to traverse
        :param bool _is_toplevel_call:
            used when recursing, avoid using when calling from outside
        :return: list of lists of corresponding values
        """
        import_compatible = self.env.context.get('import_compat', True)
        lines = []
        
        #Biến lưu index bắt đầu chèn dữ liệu cho record mới
        new_line_index = 0
        #Dict định nghĩa cách xuất kiểu many2many
        tmp_many2many_dict = {}
        #Dict định nghĩa cách xuất kiểu binary
        tmp_binary_dict = {}

        def splittor(rs):
            """ Splits the self recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            """
            for idx in range(0, len(rs), 1000):
                sub = rs[idx:idx+1000]
                for rec in sub:
                    yield rec
                sub.invalidate_recordset()
        if not _is_toplevel_call:
            splittor = lambda rs: rs

        # memory stable but ends up prefetching 275 fields (???)
        for record in splittor(self):
            # main line of record, initially empty
            current = [''] * len(fields)
            lines.append(current)
            
            #Đánh dấu sẽ bắt đầu chèn dữ liệu cho record tại dòng current
            new_line_index = len(lines) - 1

            # list of primary fields followed by secondary field(s)
            primary_done = []

            # process column by column
            for i, path in enumerate(fields):
                if not path:
                    continue

                name = path[0]
                if name in primary_done:
                    continue

                if name == '.id':
                    current[i] = str(record.id)
                elif name == 'id':
                    current[i] = (record._name, record.id)
                else:
                    field = record._fields[name]
                    #Nếu là kiểu binary
                    if field.type=='binary':
                        if str(i) not in tmp_binary_dict:
                            tmp_binary_dict[str(i)] = self.vks_get_binary_field_export_param(m_model_name=self._name, m_field_name=name)
                        if tmp_binary_dict[str(i)]['b_mode']=='url':
                            if self._name=='ir.attachment':
                                current[i] = record.url or False
                            else:
                                str_tmp = """
Select url from ir_attachment where res_model = '%s' and res_id = %s and name = '%s'  limit 1
""" % (self._name, record.id, name)
                                vks_this_cr = self._cr
                                vks_this_cr.execute(str_tmp)
                                tmp_row =  vks_this_cr.dictfetchone()
                                current[i] = tmp_row and tmp_row['url'] or False
                                
                            continue
                    #Tiếp tục code gốc
                    value = record[name]

                    # this part could be simpler, but it has to be done this way
                    # in order to reproduce the former behavior
                    if not isinstance(value, BaseModel):
                        current[i] = field.convert_to_export(value, record)
                    else:
                        primary_done.append(name)
                        # recursively export the fields that follow name; use
                        # 'display_name' where no subfield is exported
                        fields2 = [(p[1:] or ['display_name'] if p and p[0] == name else [])
                                   for p in fields]

                        # in import_compat mode, m2m should always be exported as
                        # a comma-separated list of xids or names in a single cell
                        if import_compatible and field.type == 'many2many':
                            #Thay toàn bộ đoạn code ở case này
                            if str(i) not in tmp_many2many_dict:
                                tmp_many2many_dict[str(i)] = self.vks_get_many2many_export_mode(m_model_name=self._name,
                                                                        m_field_name=name)
                            if tmp_many2many_dict[str(i)] == 'one_line':
                                #Nếu là export id thì build dạng id1VKS_STR_SPLIT_MANY2MANY_VALUESid2
                                if len(path) > 1 and path[1] == 'id':
                                    xml_ids = [xid for _, xid in value.__ensure_xml_id()]
                                    current[i] = VKS_STR_SPLIT_MANY2MANY_VALUES.join(xml_ids) or False
                                    continue
                                #Ngược lại nếu là export theo display_name
                                elif len(path)==1:
                                    tmp_disp_name = [tmp_c_record.display_name for tmp_c_record in value]
                                    current[i] = VKS_STR_SPLIT_MANY2MANY_VALUES.join(tmp_disp_name) or False
                                    continue

                        lines2 = value._export_rows(fields2, _is_toplevel_call=False)
                        if lines2:
                            #Thay toàn bộ đoạn code ở case này
                            #Lấy ra vị trí cuối cùng của lines2
                            last_index_line2 = len(lines2) - 1
                            #Lấy ra vị trí cuối cùng của line
                            last_index_line = len(lines) - 1
                            #Khởi gán vị trí bắt đầu chèn dữ liệu
                            start_index_for_insert = new_line_index
                            #Gán biến tạm phục vụ cho vòng while
                            tmp_current_line2_index = 0
                            #Lặp cho đến khi hết các phần tử trong lines2
                            while tmp_current_line2_index <= last_index_line2:
                                #Nếu vị trí cần chèn <= vị trí cuối cùng của lines thì merge dữ liệu giữa 
                                    #dòng tương ứng của lines và lines2
                                if last_index_line >= start_index_for_insert:
                                    for j, val in enumerate(lines2[tmp_current_line2_index]):
                                        #Fix lỗi export dữ liệu nếu số là 0 thì ra kết quả rỗng
                                        try: 
                                            if val or isinstance(val, (int, float)):
                                                lines[start_index_for_insert][j] = val
                                        except:
                                            continue
                                    #--------------------------------End---------------------------------------
                                    start_index_for_insert +=1
                                    tmp_current_line2_index +=1
                                else:
                                    #Ngược lại thì kiểm tra nếu dòng đang xét của lines2 không phải dòng trống thì 
                                        #add vào lines 
                                    while tmp_current_line2_index <= last_index_line2:
                                        tmp_check_list_empty = list(set(lines2[tmp_current_line2_index]))
                                        if len(tmp_check_list_empty) > 1 or tmp_check_list_empty[0] or isinstance(tmp_check_list_empty[0],(int, float)):
                                            lines.append(lines2[tmp_current_line2_index])
                                        tmp_current_line2_index +=1
                                    break
                                
                        else:
                            current[i] = ''

        # if any xid should be exported, only do so at toplevel
        if _is_toplevel_call and any(f[-1] == 'id' for f in fields):
            bymodels = collections.defaultdict(set)
            xidmap = collections.defaultdict(list)
            # collect all the tuples in "lines" (along with their coordinates)
            for i, line in enumerate(lines):
                for j, cell in enumerate(line):
                    if type(cell) is tuple:
                        bymodels[cell[0]].add(cell[1])
                        xidmap[cell].append((i, j))
            # for each model, xid-export everything and inject in matrix
            for model, ids in bymodels.items():
                for record, xid in self.env[model].browse(ids).__ensure_xml_id():
                    for i, j in xidmap.pop((record._name, record.id)):
                        lines[i][j] = xid
            assert not xidmap, "failed to export xids for %s" % ', '.join('{}:{}' % it for it in xidmap.items())

        return lines