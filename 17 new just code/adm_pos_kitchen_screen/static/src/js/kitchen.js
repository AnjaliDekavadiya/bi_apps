
/**@odoo-module */
const { Component, onMounted, onWillUnmount, useState } = owl;
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import {KitchenOrders} from './kitchen-orders';
const actionRegistry = registry.category("actions");
export class KitchenKanban extends Component {
    setup(){
        super.setup(...arguments);
        this.orders = [];
        this.orm = useService("orm");
        this.action = useService("action");
        this.category_ids = useState({ data: [] });
        this.pos_config_ids = useState({ data: [] });
        this.auto_refresh = true;
        this.show_pending_orders = true;
        this.show_in_progress_orders = true;
        this.show_done_orders = true;
        this.interval;
        
        onMounted(()=>{
            this.start();
        });

        onWillUnmount(()=>{
            clearInterval(this.interval);
        });
    }
    start() {
        if (localStorage.getItem('auto_refresh_seconds') === null) {
            localStorage.setItem('auto_refresh_seconds', 30);
        }
        // Made here to avoid background color change after initialized
        if (localStorage.getItem('theme')) {
            $('.theme-select').val(localStorage.getItem('theme'));
            this._setTheme(localStorage.getItem('theme'));
        }
        const self = this;
        this.orm.searchRead('res.users', [['id', '=', session.user_id]], ['kitchen_category_ids', 'pos_config_ids']).then((data) => {
            this.pos_config_ids = data[0].pos_config_ids;
            this.category_ids = data[0].kitchen_category_ids;
            if (this.category_ids.length == 0 || this.pos_config_ids.length === 0) {
                $('.setup_container').show();
                return;
            }
            self.load_data().then((res) => {
                this.set_refresh_interval();
                this._recovery_session_options();
            });

        });
    }

    _recovery_session_options() {
        $('.refresh-time').val(localStorage.getItem('auto_refresh_seconds'));
        var pausePlayRefresh = localStorage.getItem('pause_play_refresh') || 'play';
        var pendingOrders = localStorage.getItem('show_pending_orders') || 'show';
        var inProgressOrders = localStorage.getItem('show_in_progress_orders') || 'show';
        var doneOrders = localStorage.getItem('show_done_orders') || 'show';
        if (pausePlayRefresh === 'pause') {
            this._onPausePlayRefresh(undefined);
        }
        if (pendingOrders === 'hide') {
            this._onFilterPendingOrders(undefined);
        }
        if (inProgressOrders === 'hide') {
            this._onFilterInProgressOrders(undefined);
        }
        if (doneOrders === 'hide') {
            this._onFilterDoneOrders(undefined);
        }
    }

    set_refresh_interval() {
        const self = this;
        clearInterval(this.interval);
        this.interval = setInterval(() => {
            try {
                self.load_data();
            } catch(e) {
                console.error(e);
                clearInterval(this.interval);
            }
        }, localStorage.getItem('auto_refresh_seconds') * 1000);
    }

    async load_data(manual_refresh = false) {
        var self = this;
        if (!self.auto_refresh && !manual_refresh) {
            return;
        }
        if ($('.kitchen_container').length === 0) {
            $('.kanban_view').html(`
                <div class="kitchen_container">
                    <div class="kitchen_grid pending">
                            <h3 class="title">Pending</h3>
                            <div class="content"></div>
                    </div>
                    <div class="kitchen_grid in_progress">
                            <h3 class="title">In progress</h3>
                            <div class="content"></div>
                    </div>
                    <div class="kitchen_grid done">
                            <h3 class="title">Done</h3>
                            <div class="content"></div>
                    </div>
                    <hr/>
                </div>
            `);
        }
        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0');
        var yyyy = today.getFullYear();

        today = yyyy + '-' + mm + '-' + dd;
        //today = '2023-11-30'
        var fields = ['id', 'kitchen_state', 'name', 'start_date', 'user_id', 'pos_reference', 'table_id', 'create_date', 'customer_count'];
        var lines = await self.orm.searchRead('pos.order.line', [
            ['create_date', '>=', today],
            ['product_id.pos_categ_ids.id', 'in', self.category_ids],
            ['order_id.session_id.config_id.id', 'in', self.pos_config_ids]],
            ['kitchen_state', 'full_product_name', 'qty', 'order_id', 'product_id', 'avg_completion_time', 'note', 'customer_note']
        ).then(function(lines) {
            return lines;
        });
        await self.orm.searchRead('pos.order', [['create_date', '>=', today], ['kitchen_state', 'in', ['pending', 'in_progress', 'done']]], fields).then(function(orders) {
            orders.forEach(function(order) {
                order.user_id = order.user_id && order.user_id.length > 0 ? order.user_id[1] : '';
                order.table_id = order.table_id && order.table_id.length > 0 ? order.table_id[1] : '';
                order.create_date = self.convertDateToLocale(new Date(order.create_date));
            });
            orders = self.getOrdersWithLines(orders, lines);
            self.orders = orders;
            self._showOrders();
            self._hook_events();
            
        });
            
    }

    _showOrders() {
        const self = this;
        if (self.show_pending_orders) {
            self.getPendingOrders(self.orders);
        }
        if (self.show_in_progress_orders) {
            self.getInProgressOrders(self.orders);
        }
        if (self.show_done_orders) {
            self.getDoneOrders(self.orders);
        }
        self._hook_order_events();
    }



    _hook_events() {
        const self = this;
        $('.options_header').click(function(ev) {
            // refresh interval
            self.set_refresh_interval();
            self._onShowHideOptions(ev)
        });
        $('.refresh-time').on('change', (ev) => {
            $('.save-refresh-seconds').show(); 
        });
        $('.save-refresh-seconds').click((ev) => {
            self._save_refresh_seconds(ev);
        });
        $('.pause-play-refresh').click(function(ev) {
            self._onPausePlayRefresh(ev)
        });
        $('.pending-orders-filter').click(function(ev) {
            self._onFilterPendingOrders(ev)
        });
        $('.in-progress-orders-filter').click(function(ev) {
            self._onFilterInProgressOrders(ev)
        });
        $('.done-orders-filter').click(function(ev) {
            self._onFilterDoneOrders(ev)
        });
        $('.manual-refresh').click((ev) => {
            self.load_data(true);
        });

        $('.theme-select').on('change', (ev) => {
            const theme = ev.currentTarget.value;
            self._setTheme(theme);
            localStorage.setItem('theme', theme);
        });
    }

    _setTheme(theme) {
        $('.o_content.kitchen')[0].classList.forEach((className) => {
            if (className.startsWith('theme-')) {
                $('.o_content.kitchen')[0].classList.remove(className);
            }
        });
        $('.o_content.kitchen')[0].classList.add(theme);
    }

    _hook_order_events() {
        const self = this;
        $('.show_receipie').click(function(ev) {
            // refresh interval
            self.set_refresh_interval();
            self._onShowReceipie(ev);
        });
        $('.start_order_line').click(function(ev) {
            self._onStartOrEndOrderLine(ev)
        });
        $('.end_order_line').click(function(ev) {
            self._onStartOrEndOrderLine(ev)
        });
        $('.line-note').click(function(ev) {
            self._onShowNote(ev);
        });
    }

    getPendingOrders(orders) {
        
        orders = this.orders.filter((order) => {
            return order.lines.filter((line) => line.kitchen_state === 'in_progress' || line.kitchen_state === 'done').length === 0;
        });
        var kitchenOrders = new KitchenOrders({
            orders: orders
        });
        $('.kitchen_grid.pending .content').html(kitchenOrders.render());
    }

    getInProgressOrders(orders) {
        
        orders = this.orders.filter((order) => {
            const in_progress_lines = order.lines.filter((line) => line.kitchen_state === 'in_progress');
            const pending_lines = order.lines.filter((line) => line.kitchen_state === 'pending');
            const done_lines = order.lines.filter((line) => line.kitchen_state === 'done');
            return (in_progress_lines.length > 0) || (pending_lines.length > 0 && done_lines.length > 0);
        });
        var kitchenOrders = new KitchenOrders({
            orders: orders
        });
        $('.kitchen_grid.in_progress .content').html(kitchenOrders.render());
    }

    getDoneOrders(orders) {
        
        orders = this.orders.filter((order) => {
            return order.lines.filter((line) => line.kitchen_state !== 'done').length === 0;
        });
        var kitchenOrders = new KitchenOrders({
            orders: orders
        });
        $('.kitchen_grid.done .content').html(kitchenOrders.render());
    }

    getOrdersWithLines(orders, lines) {
        orders.forEach(function(order) {
            order.lines = lines.filter((line) => line.order_id[0] === order.id);
        });
        orders = orders.filter((order) => order.lines.length > 0);
        return orders;
    }

    convertDateToLocale(date) {
        var newDate = new Date(date.getTime()+date.getTimezoneOffset()*60*1000);
        var offset = date.getTimezoneOffset() / 60;
        var hours = date.getHours();
        newDate.setHours(hours - offset);
        return newDate.toLocaleString();
    }

    _save_refresh_seconds(ev) {
        var self = this;
        var seconds = $('.refresh-time').val();
        if (seconds === '') {
            seconds = 30;
        }
        localStorage.setItem('auto_refresh_seconds', seconds);
        self.set_refresh_interval();
        $('.save-refresh-seconds').hide();
    }

    _onShowHideOptions(ev) {
        $('.options_body').toggle();
        $('.options_header .chevron-icons i').toggle();
    }

    _onShowNote(ev) {
        var self = this;
        var internalNote = $(ev.currentTarget).data("note");
        var customerNote = $(ev.currentTarget).data("customer-note");
        var product = $(ev.currentTarget).data("product");
        var html_data = '<div class="icon-close-container"><span class="icon-close"><i class="fa fa-close"></i></span></div>';
        html_data += '<h5>' + product +  ' Notes</h5>';
        html_data += '<div class="note_wrapper">';
        html_data += '<p><strong>Internal Note:</strong> ' + internalNote + '</p>';
        html_data += '<p><strong>Customer Note:</strong> ' + customerNote + '</p>';
        html_data += '</div>';
        $('.note_container').html(html_data);
        $('.note_container').show();
        $('.note_container .icon-close').click(function(ev) {
            self._onHideNote();
        });
    }
        
    _onShowReceipie(ev) {
        var product = $(ev.currentTarget).data( "product").split(',')[0];
        this.orm.searchRead('product.product', [['id', '=', product]], ['name', 'recipie', 'image_512']).then((data) => {
            if (!data[0]['recipie']) {
                data[0]['recipie'] = '';
            }
            var html_data = '<div class="icon-close-container"><span class="icon-close"><i class="fa fa-close"></i></span></div>';
            html_data += '<h5> ' + data[0]['name'] +  ' Recipie</h5>';
            html_data += '<div class="recipie_wrapper">';
            if (data[0]['image_512'] !== false) {
                html_data += '<p class="product_image"><img src="data:image/png;base64, ' + data[0]['image_512'] + '" /></p>';
            }
            html_data += '<div class="recipie_description">' + data[0]['recipie'] + '</div>';
            html_data += '</div>';
            self.$('.recipie_container').html(html_data);
            self.$('.recipie_container').show();
            $('.recipie_container .icon-close').click(function(ev) {
                $('.recipie_container').hide();
            });
        });
        
    }

    _onHideNote(ev) {
        $('.note_container').hide();
    }
    
    _onStartOrEndOrderLine(ev) {
        var today = new Date();
        var date = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2, '0') + '-'+String(today.getDate()).padStart(2, '0');
        var time = String(today.getHours()).padStart(2, '0') + ":" + String(today.getMinutes()).padStart(2, '0') + ":" + String(today.getSeconds()).padStart(2, '0');
        var dateTime = date+' '+time;
        var self = this;
        // refresh interval
        self.set_refresh_interval();
        ev.stopPropagation();
        var values = {}
        var id = $(ev.currentTarget).data( "id");
        values[$(ev.currentTarget).data( "type") === 'start' ? 'start_date' : 'end_date'] = dateTime;
        this.orm.write('pos.order.line', [id], values).then(function (data) {
            $(ev.currentTarget).addClass('disabled');
            self.orders.forEach(function(order) {
                var line = order.lines.find((line) => line.id === id);
                if (line){
                    line[$(ev.currentTarget).data( "type") === 'start' ? 'start_date' : 'end_date'] = dateTime;
                    line['kitchen_state'] = $(ev.currentTarget).data( "type") === 'start' ? 'in_progress' : 'done';
                }
            });
            $(ev.currentTarget).removeClass('disabled');
            self._showOrders();
        }).catch(function (error) {
            console.error(error)
        });
    }
    
    _onPausePlayRefresh(ev) {
        $('.pause-play-refresh').toggle();
        $('.refresh-time').toggle();
        $('.refresh-time-label').toggle();
        $('.manual-refresh').toggle();
        this.auto_refresh = !this.auto_refresh;
        localStorage.setItem('pause_play_refresh', this.auto_refresh ? 'play' : 'pause');
    }

    _onFilterPendingOrders(ev) {
        $('.pending-orders-filter').toggleClass('active');
        $('.kitchen_grid.pending').toggle();
        this.show_pending_orders = !this.show_pending_orders;
        localStorage.setItem('show_pending_orders', this.show_pending_orders ? 'show' : 'hide');
    }

    _onFilterInProgressOrders(ev) {
        $('.in-progress-orders-filter').toggleClass('active');
        $('.kitchen_grid.in_progress').toggle();
        this.show_in_progress_orders = !this.show_in_progress_orders;
        localStorage.setItem('show_in_progress_orders', this.show_in_progress_orders ? 'show' : 'hide');
    }

    _onFilterDoneOrders(ev) {
        self.$('.done-orders-filter').toggleClass('active');
        self.$('.kitchen_grid.done').toggle();
        this.show_done_orders = !this.show_done_orders;
        localStorage.setItem('show_done_orders', this.show_done_orders ? 'show' : 'hide');
    }
}
KitchenKanban.template = "kitchen_template";
actionRegistry.add("kitchen_kanban", KitchenKanban);
