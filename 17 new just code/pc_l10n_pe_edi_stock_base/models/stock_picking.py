from odoo import fields, models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Document Type', default=lambda self: self._get_default_document())
    type_operation_id = fields.Many2one('type.operation.sunat', string='Type Operation', default=lambda self: self._get_default_operation())
    serie = fields.Char('Serie', copy=False)
    number = fields.Char('Number', copy=False)

    @api.model
    def _get_default_document(self):
        if self.picking_type_code:
            return self.env.ref('pc_l10n_pe_edi_stock_base.document_type09').id
            
    @api.model
    def _get_default_operation(self):
        if self.picking_type_code:
            if self.picking_type_code == 'incoming':
                return self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_02').id
            else:
                return self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_01').id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for picking in res:
            if picking.picking_type_code:
                picking.l10n_latam_document_type_id = self.env.ref('pc_l10n_pe_edi_stock_base.document_type09').id
                if picking.picking_type_code == 'incoming':
                    if picking.partner_id and picking.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code == '0':
                        picking.type_operation_id = self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_18').id
                        picking.l10n_latam_document_type_id = self.env.ref('pc_l10n_pe_edi_stock_base.document_type31').id
                    else:
                        if picking.return_id:
                            picking.type_operation_id = self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_05').id
                        else:
                            picking.type_operation_id = self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_02').id
                else:
                    if picking.return_id:
                        picking.type_operation_id = self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_06').id
                    else:
                        picking.type_operation_id = self.env.ref('pc_l10n_pe_edi_stock_base.operation_sunat_01').id
        return res