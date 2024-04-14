/* @odoo-module */

import {
    Component,
    onWillStart,
    onMounted,
    onWillUnmount,
    useChildSubEnv,
    useRef,
    useState,
    useEffect,
    useExternalListener,
} from "@odoo/owl";

import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class InternalRecords extends Component {
    static components = {
    };
    static props = {
        value: { type: String, optional: true },
    };
    static template = "whatsapp.Internal";

    async setup(){
        this.messaging = useState(useService("mail.messaging"));
        this.store = useState(useService("mail.store"));
        this.threadService = useState(useService("mail.thread"));
        this.personaService = useService("mail.persona");
        this.contentRef = useRef("content");
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.root = useRef("root");
        this.invoicesref = useRef("invoice_textarea");
        this.contactsref = useRef("contact_textarea");
        this.saleref = useRef("sale_textarea");
        this.purchaseref = useRef("purchase_textarea")
        this.productref = useRef("product_textarea");
        this.product_recordsref = useRef("product_records");
        this.purchase_recordsref = useRef("purchase_records");
        this.sale_recordsref = useRef("sale_records");
        this.contacts_recordsref = useRef("contact_records");
        this.invoices_recordsref = useRef("invoice_records");
        this.reportGrid = useRef("reportGrid");
        console.log("report grid====", this.reportGrid);
        this.product_search = false;
        this.purchase_search = false;
        this.sale_search = false;
        this.contact_search = false;
        this.invoice_search = false;
        await this.store;
        await this.reportGrid;
        this.generate_graph();
        console.log("products===", this.store);
        console.log("this internal===", this);
    }

    get products() {
        // console.log("products===", this)
        return this.store.products;
    }

    get purchases() {
        return this.store.purchases;
    }

    get sales() {
        return this.store.sales;
    }

    get contacts() {
        return this.store.contacts;
    }

    get invoices() {
        return this.store.invoices;
    }
    
    search_invoices(ev){
        const ref = this.invoicesref.el;
        var self = this;
        console.log("the ref====", this.invoicesref);
        console.log("the records ref====", this.invoices_recordsref);
        const $el = $(this.invoices_recordsref.el);
        console.log("jquery======", $el.contents());
        const invoices = self.store.invoices.filter((element) => element.name.includes(ref.value));
        console.log("invoice search", invoices);
        $el.empty();
        self.render_invoices(invoices);
    }

    search_contacts(ev){
        const ref = this.contactsref.el;
        var self = this;
        console.log("the ref====", this.contactsref);
        console.log("the records ref====", this.contacts_recordsref);
        const $el = $(this.contacts_recordsref.el);
        console.log("jquery======", $el.contents());
        self.rpc("/whatsapp_dashboard/search_input_chart",{
            search_input: ref.value,
            model_name: 'res.partner',
        }).then(function (res){
            console.log("contacts===", res);
            self.contact_search = res;
            $el.empty();
            self.render_contacts(res);
        })
    }

    search_sales(ev){
        const ref = this.saleref.el;
        var self = this;
        console.log("the ref====", this.saleref);
        console.log("the records ref====", this.sale_recordsref);
        const $el = $(this.sale_recordsref.el);
        console.log("jquery======", $el.contents());
        self.rpc("/whatsapp_dashboard/search_input_chart",{
            search_input: ref.value,
            model_name: 'sale.order',
        }).then(function (res){
            console.log("sales===", res);
            self.sale_search = res;
            $el.empty();
            self.render_sales(res);
        })
    }

    search_purchases(ev){
        const ref = this.purchaseref.el;
        var self = this;
        console.log("the ref====", this.purchaseref);
        console.log("the records ref====", this.purchase_recordsref);
        const $el = $(this.purchase_recordsref.el);
        console.log("jquery======", $el.contents());
        self.rpc("/whatsapp_dashboard/search_input_chart",{
            search_input: ref.value,
            model_name: 'purchase.order',
        }).then(function (res){
            console.log("purchases===", res);
            self.purchase_search = res;
            $el.empty();
            self.render_purchases(res);
        })
    }

    search_products(ev){
        const ref = this.productref.el;
        var self = this;
        console.log("the ref====", this.productref);
        console.log("the records ref====", this.product_recordsref);
        const $el = $(this.product_recordsref.el);
        console.log("jquery======", $el.contents());
        // this.el.append(this._mainWrapperElement);
        self.rpc("/whatsapp_dashboard/search_input_chart",{
            search_input: ref.value,
            model_name: 'product.template',
        }).then(function (res){
            console.log("Products===", res);
            self.product_search = res;
            $el.empty();
            self.render_products(res);
            // for (const child in $el.contents().filter((index, content) =>
            //     content.nodeType === 1 || (content.nodeType === 3 && content.nodeValue.trim()))){
            //     console.log("child=======", child);
            //     let $child = $(self.product_recordsref.el.children[child]);
            //     console.log("child=======", $child);
            //     // $child.remove();

            //     self.product_recordsref.el.removeChild($child[0]);
            // }
            // self.render_products(self.product_search);
            // $el.remove();
            // self.$(".product-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped' id='productstack' style='display: contents;'></div>")
        });
    }

    generate_graph(){
        var self = this;
        self.rpc("/whatsapp/get_message_dashboard",{})
        .then(function (res){
            for (let i = 0; i < res.length; i++) {
                var rec = res[i]
                self.render_chart(rec, rec.id);
            }
        });
    }

    render_chart(dict_data, dashboard_item_id){
        var self = this;
        const $el = $(this.reportGrid.el);
        var dataset = JSON.parse(dict_data.chart_data);
        console.log($el);
        var grid_path = null;
        var new_grid = null;
        var options_grid = {
            alwaysShowResizeHandle: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
            staticGrid: true,
            float: false,
            margin: '100px',
        };
        $el.gridstack(options_grid);
        var grid_stack = $el;
        // var widget_stack = self.$('.o_widget_Discuss').prevObject;
        // var widget_stack2 = widget_stack[0];
        // var widget_stack3 = widget_stack2.childNodes;
        // console.log(grid_stack);
        self.grid = $el.data('gridstack');
        // self.grid.enableMove(false, true);
        // self.grid.enableResize(false, true);
        grid_stack.append(`<div class='chart-container box' id='chart_item_${dashboard_item_id}' /></div>`)
        var serizize_data = null;
        if (dict_data.chart_dashboard_positions){
            var dict_obj = JSON.parse((dict_data.chart_dashboard_positions))
            serizize_data = [{id: `chart_item_${dashboard_item_id}`, x: dict_obj.chart_x, y: dict_obj.chart_y, w: dict_obj.chart_width, h:dict_obj.chart_height}]
        }
        else{
            serizize_data = [{id: `chart_item_${dashboard_item_id}`, x: 0, y: 200, w: 12, h:5}]
        }
        var items = GridStackUI.Utils.sort(serizize_data);
        // console.log(items);
        items.forEach(node=>{
            var containerElt = $("#" + node.id);
            containerElt.attr("data-gs-id", node.id);
            containerElt.attr("data-gs-width", node.w);
            containerElt.attr("data-gs-height", node.h);
            containerElt.attr("data-gs-x", node.x);
            containerElt.attr("data-gs-y", node.y);
            grid_path = self.grid.makeWidget(containerElt)
        });

        var options = {
            series: dataset.data_list,
            chart: {
                type: dict_data.chart_type == 'column'? 'bar': dict_data.chart_type,
                height : '100%',
                background: dict_data.chart_theme == 'custom' ? dict_data.chart_background_color : false,
                foreColor: dict_data.chart_theme == 'custom' ? dict_data.chart_fore_color : false,
                redrawOnParentResize: true,
                redrawOnWindowResize: true,
                toolbar: {
                    show: false
                },
            },
            title: {
                text: dict_data.name,
            },
            theme: {
                mode: dict_data.chart_theme == 'custom' ? false : dict_data.chart_theme,
                palette: dict_data.color_palette,
            },
        };
        if (dict_data.chart_type == 'bar' || dict_data.chart_type == 'column'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['plotOptions'] =  {
                bar: {
                    horizontal: dict_data.chart_type == 'column'? false : true,
                    columnWidth: '75%',
                    distributed: dict_data.is_distributed_chart,
                }
            }
        }
        else if (dict_data.chart_type == 'pie'){
            options['labels'] = dataset.model_label_list
            options['responsive'] = [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 200,
                        height: 350
                    },
                }
            }]
        }
        else if (dict_data.chart_type == 'donut'){
            options['labels'] = dataset.model_label_list
            options['responsive'] = [{
                breakpoint: 480,
                options: {
                    chart: {
                        type: 'donut',
                        width: 200,
                        height: 350,
                    },
                }
            }]
        }
        else if (dict_data.chart_type == 'line'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'line',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'area'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'area',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'treemap'){
            // options['xaxis'] = {
            //     categories: dataset.model_label_list,
            // }
            options['series'] = [{
                data: dataset.data_list
            }]
            options['chart'] = {
                type: 'treemap',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'radar'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'radar',
                height: 350,
            }
        }
        var new_chart = $el.find(`[id='chart_item_${dashboard_item_id}']`)
        new_chart.append('<div class="grid-stack-item-content"></div>')
        var new_grid_item = $el.find(`[id='chart_item_${dashboard_item_id}']`).find('.grid-stack-item-content')
        // console.log(new_grid_item[0]);
        var chart = new ApexCharts(new_grid_item[0], options);
        chart.render();
    }

    render_invoices(data){
        const $el = $(this.invoices_recordsref.el);
        for (const index in data){
            let dict_data = data[index];
            $el.append(`<tr class="o_data_row invoice_record text-info" style="cursor: pointer;" id="account_move_${dict_data.id}" draggable="true" ondragstart="dragStartpurchase(event)">`);
            var check_box = $el.find(`[id='account_move_${dict_data.id}']`)
            const edit = this.edit_invoice.bind(this);
            check_box.on("click", edit);
            check_box.append(`<td class="o_list_record_selector">
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" id="checkbox-${dict_data.id}" class="custom-control-input"/>
                    <label for="checkbox-${dict_data.id}" class="custom-control-label">​</label>
                </div>
            </td>`)
            var reference_field = $el.find(`[id='account_move_${dict_data.id}']`);
            reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${dict_data.name}" name="name">
            ${dict_data.name}
            </td>`)
            var creation_date_field = $el.find(`[id='account_move_${dict_data.id}']`);
            creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="invoice_date">${dict_data.invoice_date}</span>
            </td>`)
            var vendor_field = $el.find(`[id='account_move_${dict_data.id}']`);
            vendor_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${dict_data.partner_id[1]}" name="partner_id">
            ${dict_data.partner_id[1]}
            </td>`)
            var representative_field = $el.find(`[id='account_move_${dict_data.id}']`);
            representative_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="invoice_date_due">${dict_data.invoice_date_due}</span>
            </td>`)
            var total_field = $el.find(`[id='account_move_${dict_data.id}']`);
            total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
                ${dict_data.amount_total}${dict_data.currency_symbol}
                </span>
            </td>`)
            var status_field = $el.find(`[id='account_move_${dict_data.id}']`);
            status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${dict_data.state}</span>
            </td>`)
            var report_link = $el.find(`[id='account_move_${dict_data.id}']`);
            report_link.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
                draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                    <a href="/report/pdf/account.report_invoice/${dict_data.id}"></a>
                </div>
                <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_invoice_report" name="${dict_data.name}" index="${dict_data.id}"></button>
            </td>`)
        }
    }

    render_contacts(data){
        const $el = $(this.contacts_recordsref.el);
        for (const index in data){
            let contacts = data[index];
            $el.append(`<div id="article_${contacts.id}" role="article" class="o_kanban_record flex-grow-1 flex-md-shrink-1 flex-shrink-0" tabindex="0" style="max-width: 265px; min-width: 260px; min-height: 138px; max-height: 140px; margin-left: auto; display: inline-block;"></div>`)
            var contacts_record = $el.find(`[id='article_${contacts.id}']`)
            contacts_record.append(`<div id="res_partner_${contacts.id}" class="oe_kanban_global_click o_kanban_record_has_image_fill o_res_partner_kanban contact_record" style="max-width: 265px; min-width: 260px; min-height: 138px; max-height: 140px;"></div>`)
            if (!contacts.is_company) {
                var main_image = $el.find(`[id='res_partner_${contacts.id}']`);
                const edit = this.edit_contact.bind(this);
                main_image.on("click", edit);
                main_image.append(`<div class="o_kanban_image_fill_left d-none d-md-block" style="background-image:url('/web/image/res.partner/${contacts.id}/avatar_128')" draggable="true" ondragstart="dragStartImg(event)">
                    <img class="o_kanban_image_inner_pic" alt="${contacts.parent_id}" src="/web/image/res.partner/${contacts.id}/avatar_128" draggable="true" ondragstart="dragStartImg(event)"/>
                </div>`)
                var small_image = $el.find(`[id='res_partner_${contacts.id}']`)
                small_image.append(`<div class="o_kanban_image d-md-none">
                    <img class="o_kanban_image_inner_pic" t-if="record.parent_id" alt="${contacts.parent_id}" src="/web/image/res.partner/${contacts.id}/avatar_128" draggable="true" ondragstart="dragStartImg(event)"/>
                </div>`)
            }
            else {
                var main_image = $el.find(`[id='res_partner_${contacts.id}']`)
                main_image.append(`<img class="o_kanban_image_fill_left o_kanban_image_full" style="max-height: 130px; min-height: 125px; max-width: 100px;" src="/web/image/res.partner/${contacts.id}/avatar_128" role="img" draggable="true" ondragstart="dragStartImg(event)"/>`)
            }
            var details_div = $el.find(`[id='res_partner_${contacts.id}']`)
            details_div.append(`<div class="oe_kanban_details d-flex flex-column" draggable="true" ondragstart="dragStart(event)"></div>`)
            var display_name = $el.find(`[id='res_partner_${contacts.id}']`).find('.oe_kanban_details')
            display_name.append(`<strong class="o_kanban_record_title oe_partner_heading">
            ${contacts.display_name}
            </strong>`)

            var display_tags = $el.find(`[id='res_partner_${contacts.id}']`).find('.oe_kanban_details');
            display_tags.append(`<div class="o_kanban_tags_section oe_kanban_partner_categories"/>`);
            var other_details = $el.find(`[id='res_partner_${contacts.id}']`).find('.oe_kanban_details');
            other_details.append(`<ul></ul>`);
            var other_details_ul = $el.find(`[id='res_partner_${contacts.id}']`).find('.oe_kanban_details').find('ul');
            // console.log(other_details_ul);
            if (contacts.parent_id!=false){
                other_details_ul.append(`<li>${contacts.parent_name}</li>`)
            }
            if (!contacts.parent_id && contacts.function){
                other_details_ul.append(`<li>${contacts.function}</li>`)
            }
            if (contacts.parent_id && contacts.function){
                other_details_ul.append(`<li>${contacts.function} at ${contacts.parent_name}</li>`)
            }
            if (contacts.city || contacts.country_id){
                if (contacts.city) {
                    other_details_ul.append(`<li>${contacts.city}, ${contacts.country_id[1]}</li>`)
                }
                else {
                    other_details_ul.append(`<li>${contacts.country_id[1]}</li>`)
                }
            }
            if (contacts.email) {
                other_details_ul.append(`<li class="o_text_overflow">${contacts.email}</li>`)
            }
        }
    }

    render_sales(data){
        const $el = $(this.sale_recordsref.el);
        for (const index in data){
            let sales = data[index];
            $el.append(`<tr class="o_data_row sale_record" id="sale_order_${sales.id}" draggable="true" ondragstart="dragStartSale(event)">`)
            var check_box = $el.find(`[id='sale_order_${sales.id}']`)
            const edit = this.edit_sale.bind(this);
            check_box.on("click", edit);
            check_box.append(`<td class="o_list_record_selector">
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" id="checkbox-sale-${sales.id}" class="custom-control-input"/>
                    <label for="checkbox-sale-${sales.id}" class="custom-control-label">​</label>
                </div>
            </td>`)
            var reference_field = $el.find(`[id='sale_order_${sales.id}']`)
            reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${sales.name}" name="name">
            ${sales.name}
            </td>`)
            var creation_date_field = $el.find(`[id='sale_order_${sales.id}']`)
            creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="create_date">${sales.create_date}</span>
            </td>`)
            var customer_field = $el.find(`[id='sale_order_${sales.id}']`)
            customer_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${sales.partner_id[1]}" name="partner_id">
            ${sales.partner_id[1]}
            </td>`)
            // var salesperson_field = $el.find(`[id='sale_order_${sales.id}']`)
            // salesperson_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_many2one_avatar_user_cell" tabindex="-1">
            //     <div class="o_clickable_m2x_avatar o_field_many2one_avatar o_field_widget o_quick_editable" name="user_id">
            //         <div class="o_m2o_avatar">
            //             <img src="/web/image/res.users/${sales.user_id[0]}/avatar_128" alt="${sales.user_id[1]}"/>
            //             <span>${sales.user_id[1]}</span>
            //         </div>
            //     </div>
            // </td>`)
            var total_field = $el.find(`[id='sale_order_${sales.id}']`)
            total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
                ${sales.amount_total}${sales.currency_symbol}
                </span>
            </td>`)
            var status_field = $el.find(`[id='sale_order_${sales.id}']`)
            status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${sales.state}</span>
            </td>`)
            var report_field = $el.find(`[id='sale_order_${sales.id}']`)
            report_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
                draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                    <a href="/report/pdf/sale.report_saleorder/${sales.id}"></a>
                </div>
                <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_report" name="${sales.name}" index="${sales.id}"></button>
            </td>`)
        }
    }

    render_purchases(data){
        const $el = $(this.purchase_recordsref.el);
        for (const index in data){
            let purchases = data[index];
            $el.append(`<tr class="o_data_row purchase_record text-info" id="purchase_order_${purchases.id}" draggable="true" ondragstart="dragStartpurchase(event)">`);
            var check_box = $el.find(`[id='purchase_order_${purchases.id}']`)
            const edit = this.edit_purchase.bind(this);
            check_box.on("click", edit);
            check_box.append(`<td class="o_list_record_selector">
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" id="checkbox-${purchases.id}" class="custom-control-input"/>
                    <label for="checkbox-${purchases.id}" class="custom-control-label">​</label>
                </div>
            </td>`)
            var reference_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${purchases.name}" name="name">
            ${purchases.name}
            </td>`)
            var creation_date_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="date_order">${purchases.date_order}</span>
            </td>`)
            var vendor_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            vendor_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${purchases.partner_id[1]}" name="partner_id">
            ${purchases.partner_id[1]}
            </td>`)
            // var representative_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            // representative_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_many2one_avatar_user_cell" tabindex="-1">
            //     <div class="o_clickable_m2x_avatar o_field_many2one_avatar o_field_widget o_quick_editable" name="user_id">
            //         <div class="o_m2o_avatar">
            //             <img src="/web/image/res.users/${purchases.user_id[0]}/avatar_128" alt="${purchases.user_id[1]}"/>
            //             <span>${purchases.user_id[1]}</span>
            //         </div>
            //     </div>
            // </td>`)
            var total_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
                <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
                ${purchases.amount_total}${purchases.currency_symbol}
                </span>
            </td>`)
            var status_field = $el.find(`[id='purchase_order_${purchases.id}']`);
            status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${purchases.state}</span>
            </td>`)
            var report_link = $el.find(`[id='purchase_order_${purchases.id}']`);
            report_link.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
                <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
                draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                    <a href="/report/pdf/purchase.report_purchaseorder/${purchases.id}"></a>
                </div>
                <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_purchase_report" name="${purchases.name}" index="${purchases.id}"></button>
            </td>`)
        }
    }

    render_products(data){
        console.log(data);
        const $el = $(this.product_recordsref.el);
        for (const index in data){
            let product = data[index];
            $el.append(`<div id="article_${product.id}" role="article" class="o_kanban_record flex-grow-1 flex-md-shrink-1 flex-shrink-0" tabindex="0" style="max-width: 255px; min-width: 250px; min-height: 100px; max-height: 130px; display: inline-block;"></div>`)
            var products_record = $el.find(`[id='article_${product.id}']`)
            products_record.append(`<div class='oe_kanban_global_click product_record' t-on-click='edit_product' id='kanbandrag${product.id}' style="max-width: 255px;min-width: 250px;min-height: 95px;max-height: 125px;"/></div>`);
            var new_card = $el.find(`[id='kanbandrag${product.id}']`);
            const edit = this.edit_product.bind(this);
            new_card.on("click", edit);
            new_card.append(`<div class='o_kanban_image mr-1'/></div>`);
            new_card.append(`<div class="oe_kanban_details" draggable="true" ondragstart="dragStart(event)"></div>`);
            var product_image = $el.find(`[id='kanbandrag${product.id}']`).find('.o_kanban_image')
            product_image.append(`<img src='/web/image/product.template/${product.id}/image_128' alt="Product" class="o_image_64_contain" draggable="true" ondragstart="dragStartImg(event)"/>`)
            var product_details = $el.find(`[id='kanbandrag${product.id}']`).find('.oe_kanban_details')
            product_details.append(`<div class="o_kanban_record_top mb-0"></div>`);
            var product_name_div = $el.find(`[id='kanbandrag${product.id}']`).find('.oe_kanban_details').find('.o_kanban_record_top')
            product_name_div.append(`<div class="o_kanban_record_headings"><strong class="o_kanban_record_title">${product.name}</strong></div>`);
            if (product.default_code){
                product_details.append(`[${product.default_code}]`)
            }
            if (product.product_variant_count > 1){
                product_details.append(`<strong>${product.product_variant_count} Variants</strong>`);
            }
            product_details.append(`<div name="product_lst_price" class="product_lst_price mt-1"></div>`)
            var product_price_div = $el.find(`[id='kanbandrag${product.id}']`).find('.oe_kanban_details').find('.product_lst_price')
            if (product.currency_id){
                product_price_div.append(`${product.list_price} ${product.currency_symbol}`)
            }
            else {
                product_price_div.append(`${product.list_price}`)
            }
        }
    }

    clear_product_search(ev){
        const $el = $(this.product_recordsref.el);
        $(this.productref.el).val('');
        $(this.product_recordsref.el).empty();
        console.log("all products=====", this.store.products);
        this.render_products(this.store.products);
    }

    clear_purchase_search(ev){
        const $el = $(this.purchase_recordsref.el);
        $(this.purchaseref.el).val('');
        $(this.purchase_recordsref.el).empty();
        console.log("all purchases=====", this.store.purchases);
        this.render_purchases(this.store.purchases);
    }

    clear_sale_search(ev){
        const $el = $(this.sale_recordsref.el);
        $(this.saleref.el).val('');
        $(this.sale_recordsref.el).empty();
        console.log("all sales=====", this.store.sales);
        this.render_sales(this.store.sales);
    }
    clear_contact_search(ev){
        const $el = $(this.contacts_recordsref.el);
        $(this.contactsref.el).val('');
        $(this.contacts_recordsref.el).empty();
        console.log("all contacts=====", this.store.contacts);
        this.render_contacts(this.store.contacts);
    }

    clear_invoice_search(ev){
        const $el = $(this.invoices_recordsref.el);
        $(this.invoicesref.el).val('');
        $(this.invoices_recordsref.el).empty();
        console.log("all invoices=====", this.store.invoices);
        this.render_invoices(this.store.invoices);
    }

    create_products(ev){
        ev.stopPropagation();
        let action = {
            res_model: 'product.template',
            name: _t('Create a new product'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
    }

    create_purchases(ev){
        ev.stopPropagation();
        let action = {
            res_model: 'purchase.order',
            name: _t('Create a new purchase'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
    }

    create_sale(ev){
        ev.stopPropagation();
        let action = {
            res_model: 'sale.order',
            name: _t('Create a new sale'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
    }

    create_invoice(ev){
        ev.stopPropagation();
        let action = {
            res_model: 'account.move',
            name: _t('Create a new invoice'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
    }

    create_contact(ev){
        ev.stopPropagation();
        let action = {
            res_model: 'res.partner',
            name: _t('Create a new contact'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
    }

    edit_product(event){
        // console.log(event);
        var self = this;
        var product_id = event.currentTarget.id.split('g')[1];

        let action = {
            res_model: 'product.template',
            res_id: Number(product_id),
            name: _t('Edit product'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };

        var options= {
            title: 'Edit product',
            res_model: 'product.template',
            res_id: Number(product_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        this.action.doAction(action);
        // new dialogs.FormViewDialog(this, options).open();
    }

    edit_purchase(event){
        // console.log(event);
        var self = this;
        var purchase_id = event.currentTarget.id.split('r_')[1];

        let action = {
            res_model: 'purchase.order',
            res_id: Number(purchase_id),
            name: _t('Edit product'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
        // new dialogs.FormViewDialog(this, options).open();
    }

    edit_sale(event){
        // console.log(event);
        var self = this;
        var sale_id = event.currentTarget.id.split('r_')[1];

        let action = {
            res_model: 'sale.order',
            res_id: Number(sale_id),
            name: _t('Edit sale'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
        // new dialogs.FormViewDialog(this, options).open();
    }

    edit_invoice(event){
        // console.log(event);
        var self = this;
        var invoice_id = event.currentTarget.id.split('e_')[1];

        let action = {
            res_model: 'account.move',
            res_id: Number(invoice_id),
            name: _t('Edit invoice'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
        // new dialogs.FormViewDialog(this, options).open();
    }

    edit_contact(event){
        // console.log(event);
        var self = this;
        var contact_id = event.currentTarget.id.split('r_')[1];

        let action = {
            res_model: 'res.partner',
            res_id: Number(contact_id),
            name: _t('Edit contact'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
        // new dialogs.FormViewDialog(this, options).open();
    }

    send_purchase_report(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        // find a way to get the active dashboard channel id
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        // var active_channel_id = this.discuss.thread.id;
        console.log("records====", this.store.Thread.records)
        // Object.values(this.store.Thread.records)
        var active_channel_id = Object.values(this.store.Thread.records).find((channel)=> channel.isLoaded && channel.type==="multi_livechat_NAMEs");
        console.log("records====", active_channel_id)
        if(active_channel_id.id !== 'inbox'){
            self.rpc("/web/dataset/call_kw/discuss.channel/upload_pdf",{
                model: 'discuss.channel',
                method: 'upload_pdf',
                args: ["", name, "purchase.report_purchaseorder", id, active_channel_id.id],
                kwargs: {}
            })
        }
    }
    send_sale_report(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        //find a way to get the id of the sale order
        //find a way to get the name of the sale order
        // find a way to get the active dashboard channel id
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        var active_channel_id = Object.values(this.store.Thread.records).find((channel)=> channel.isLoaded && channel.type==="multi_livechat_NAMEs");
        if(active_channel_id.id !== 'inbox'){
            self.rpc("/web/dataset/call_kw/discuss.channel/upload_pdf", {
                model: 'discuss.channel',
                method: 'upload_pdf',
                args: ["", name, "sale.report_saleorder", id, active_channel_id.id],
                kwargs: {}
            });
        }
    }
    send_invoice_report(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        
        var active_channel_id = Object.values(this.store.Thread.records).find((channel)=> channel.isLoaded && channel.type==="multi_livechat_NAMEs");
        if (this.store.discuss.thread){
            active_channel_id = this.store.discuss.thread
        }
        if(active_channel_id.id !== 'inbox'){
            self.rpc("/web/dataset/call_kw/discuss.channel/upload_pdf", {
                model: 'discuss.channel',
                method: 'upload_pdf',
                args: ["", name, "account.report_invoice", id, active_channel_id.id],
                kwargs: {}
            })
        }
    }
}