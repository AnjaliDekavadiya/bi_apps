/** @odoo-module **/
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { AccountMoveUploadListRenderer } from "@account/components/bills_upload/bills_upload";
import { useService } from "@web/core/utils/hooks";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { Domain } from "@web/core/domain";
import { localization } from "@web/core/l10n/localization";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
const {
    Component,
    onMounted,
    onPatched,
    onWillStart,
    onWillPatch,
    onWillUpdateProps,
    useExternalListener,
    useRef,
    useState,
    useEffect,
} = owl;

export class QuickSearchCustomize extends Component {
    setup() {
        const self = this;
        this.rpc = useService("rpc");
        this.filters = [];
        this.qsRes = [];
        this.qsCols = [];

        onWillStart(async () => {
            this.qsRes = await this.rpc("/web/dataset/call_kw", {
                model: "quick.search",
                method: "search_read",
                args: [[['model_id.model', '=', this.props.list.resModel]], ['id']],
                kwargs: {
                    context: this.props.context,
                },
            });
            if(this.qsRes.length) {
                this.qsCols = await this.rpc("/web/dataset/call_kw", {
                    model: "quick.search.line",
                    method: "search_read",
                    args: [[['quick_search_id', '=', this.qsRes[0].id]], ['id', 'name', 'field_id', 'field_name', 'field_type', 'operator_id', 'operator_value']],
                    kwargs: {
                        context: this.props.context,
                    },
                });
                $(self.qsCols).each(function(index){
                    if(self.qsCols[index].field_type == 'selection'){
                        self.qsCols[index].selection = self.props.list.fields[self.qsCols[index].field_name].selection;
                    }
                    if(self.qsCols[index].field_type == 'date' || self.qsCols[index].field_type == 'datetime'){
                        self.filters[self.qsCols[index].field_name] = [];
                    }
                });
            }
        });
    }

    onDateTimeChanged(filters, fieldName, valueIndex, date) {
        filters[fieldName][valueIndex] = date;
    }

    onReset() {
        $(".quick_search_form").trigger("reset");
    }

    onSubmit() {
        const self = this;
        let listContent = $(this.props.rootRef.el);
        let quickSearch = listContent.siblings('.quick_search');

        let inputs = $(":input:not(button)", quickSearch),
            fields = $('.quick_search_field', quickSearch);

        $(fields).each(function(){
            let $inputs = $(':input:not(button)', this);
            if($inputs.length > 1) {
                let $input_from = $($inputs[0]),
                    $input_to = $($inputs[1]);
                if($input_from.val() && $input_to.val()) {
                    let $input_from_val = $(this).data('field-type') == "date" ? serializeDate(self.filters[$(this).data('field-name')][0]) : serializeDateTime(self.filters[$(this).data('field-name')][0], { format: localization.dateFormat });
                    let $input_to_val = $(this).data('field-type') == "date" ? serializeDate(self.filters[$(this).data('field-name')][1]) : serializeDateTime(self.filters[$(this).data('field-name')][1], { format: localization.dateFormat });
                    let domain = new Domain([[$(this).data('field-name'), '>=', $input_from_val], [$(this).data('field-name'), '<=', $input_to_val]]).toString();
                    self.env.searchModel.splitAndAddDomain(domain)
                }
            } else {
                let value = $inputs.val();
                if(value){
                    if($(this).data('field-type') == 'boolean') {
                        let value_string = $(this).find('option:selected').html().toLowerCase();
                        let domain = new Domain([[$(this).data('field-name'), value, true]]).toString();
                        self.env.searchModel.splitAndAddDomain(domain)
                    } else {
                        let value_string = $inputs.val();
                        if($(this).data('field-type') == 'selection') {
                            value_string = $inputs.find('option:selected').html();
                        }
                        if($(this).data('field-type') == 'date') {
                            value = serializeDate(self.filters[$(this).data('field-name')][0])
                        } else if($(this).data('field-type') == 'datetime') {
                            value = serializeDateTime(self.filters[$(this).data('field-name')][0], { format: localization.dateFormat });
                        }
                        let domain = new Domain([[$(this).data('field-name'), $(this).data('operator'), value]]).toString();
                        self.env.searchModel.splitAndAddDomain(domain);
                    }
                }
            }
        });

        this.onReset();
    }

    qsKeyDown(ev) {
        const hotkey = getActiveHotkey(ev);
        if($(ev.target).is(':input:not(button)') && hotkey == 'enter') {
            this.onSubmit();
        }
    }
}

QuickSearchCustomize.template = 'quick_search_customize.ListQs';
QuickSearchCustomize.components = { DateTimeInput }
ListRenderer.components = { ...ListRenderer.components, QuickSearchCustomize };
AccountMoveUploadListRenderer.components = { ...AccountMoveUploadListRenderer.components, QuickSearchCustomize };