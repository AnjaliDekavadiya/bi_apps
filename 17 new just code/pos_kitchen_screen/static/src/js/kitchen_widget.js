/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

var globalSelf;
var orders_on_grid = 3;
var src = window.location.pathname;
const UPDATE_BUS_PRESENCE_DELAY = 60000;
var config_id = src.replace(/[^0-9]/g, '');

import { browser } from "@web/core/browser/browser";
import { renderToString } from "@web/core/utils/render";
import { throttleForAnimation } from "@web/core/utils/timing";
import publicWidget from "@web/legacy/js/public/public_widget";
import ServicesMixin from "@web/legacy/js/core/service_mixins";

publicWidget.registry.kitchenWidget = publicWidget.Widget.extend(
    ServicesMixin,
    {
        selector: ".o_pos_kitchen_management",
        events: {
            "click .wk-details": "_OnclickViewDetails",
            "click .bell,.bell-notification": "_OnclickBellButton",
            "click .list-hover": "_OnclickListHoverButton",
            "click .wk-next": "_OnclickListWkNext",
            "click .grid-view": "_OnclickChefHatButton",
            "click .wk-back": "_OnclickChefHatButton",
            "click .process-order .dropdown-item": "_onDropdownItemClick",
            "click .wk-cancel": "_onClickCancelAccept",

        },
        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            this.added_channel_list = [];
            this.orm = this.bindService("orm");
        },
        /**
         * @override
         */
        start: async function () {
            var self = this;
            var res = await this._super(...arguments);
            self.is_websocket_connected = false;
            self.pos_orders_by_id = {};
            self.kitchen_orders_by_id = {};
            self._fetch_kitchen_order_data();
            this.bus_service = self.__parentedParent.env.services.bus_service;
            this.startpolling();
            return res;
        },
        _fetch_kitchen_order_data: function () {
            var self = this;
            this.orm.call('pos.kitchen.order', 'fetch_kitchen_order_data', [[], parseInt(config_id)],
            ).then(function (res) {
                console.log('=============================res', res)
                self.kitchen_order_data = res;
                self.re_render_screen_grid();
                self.re_render_new_order_list();
            }).catch(function (error) {
                console.log("error", error);
            })
        },
        _OnclickViewDetails(event) {
            var self = this;
            var order = $(event.currentTarget).closest('.order-content');
            var order_id = order.attr('id');
            
            self.kitchen_order_data.order_data.forEach(function (order) {
                if (order.id == order_id) {
                    var order_html = renderToString('ListViewTemplate', { order: order });
                    $(".data-body").html(order_html);
                    if ($('.list-progress').text().trim() == 'Cancel') $('.list-order').addClass('list-cancel');
                    self.time_calculator_list();
                    var html = `
                    <div class="row" style="margin-top:7px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 20px;line-height: 24px;color: #FFFFFF;">
                    Order Token No. ` + order.kitchen_order_name + `
                    </div>`;
                    $('.token-detail').html(html);
                    $('.direction_keys').css('display', 'none');
                    if ($('.list-progress').text().trim() == 'Done') {
                        swal("Order is Successfully Done!")
                        setTimeout(function () {
                            $('.swal-button.swal-button--confirm').trigger('click')
                        }, 2000);
                    }
                }
            });
        },
        _onClickCancelAccept(ev) {
            setTimeout(() => {
                this._fetch_kitchen_order_data();
            }, 1700);
        },
        _OnclickChefHatButton(event) {
            var self = this;
            if (self && self.kitchen_order_data && self.kitchen_order_data.order_data) {
                var i = 0;
                var order_data = self.kitchen_order_data.order_data;
                var pending_orders = order_data.filter(function (order) {
                    return (order.order_progress != 'new' && order.kitchen_order_name != false);
                })
                while (i < pending_orders.length) {
                    var validate = false
                    for (var j = 0; j < pending_orders[i].lines.length; j++) {
                        if (pending_orders[i].lines[j].state == 'in_process') {
                            validate = true;
                        }
                    }
                    var dropdownItem = $('.new-order .dropdown-item[id=' + pending_orders[i].id + ']');
                    if (dropdownItem.length) {
                        dropdownItem.remove();
                        var dropdown_new = $('.new-order .dropdown-item').length;
                        if (!dropdown_new) {
                            $('.new-order .dropdown-menu').append(`
                <div class="blank-new-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
                    No new orders found...
                </div>`)
                        }
                        $('#newOrders').modal('hide');
                        $('#newOrders').removeClass('new_order_showing');
                        $(".order_modal").css('width', '0%');
                        $(".order_modal").css('height', '0%');
                    }
                    if (!validate) {
                        order_data.splice(i, 1);
                    }
                    else {
                        i++;
                    }
                }
                if (self.kitchen_order_data.queue_order == "new2old") {
                    pending_orders.reverse();
                };

                var new_arr = pending_orders;
                pending_orders.forEach(order => {
                    var cancel_lines = order.lines.filter(line => {
                        return line.state == 'cancel'
                    });
                    if (cancel_lines.length == order.lines.length) {
                        new_arr = self.arrRemove(pending_orders, order)
                    }
                });

                var grid_html = renderToString('GridViewTemplate', {
                    order: new_arr
                });
                var data_html = renderToString('KitchenDataTemplate', {
                    order_data: new_arr
                });
                var element = $(grid_html);
                element.find('#kitchen-order-data').append(data_html);
                $('.data-body').html(element);
                if (orders_on_grid == 4 || orders_on_grid == 6)
                    $('#kitchen-order-data').css('height', 'auto');
                $('.order-content').each(function (index, el) {
                    var last_element = $(el);
                    if (orders_on_grid == 4 || orders_on_grid == 6) {
                        last_element.addClass('main');
                        last_element.find('.grid-template-auto').addClass('categ-body');
                        last_element.find('.inner-element').addClass('categs');
                        last_element.find('.order-footer').addClass('foot');
                        last_element.find('.order-progress').addClass('temp-progress');
                        last_element.find('.order-header').addClass('head');
                    }
                });
                $("#list-right").attr('offset', 1);
                $("#list-left").attr('offset', -1);
                $('.direction_keys').css('display', 'inline-block');
                var html = ` <div class="row" style="font-family: Montserrat;
            font-style: normal;
            font-weight: normal;
            font-size: 20px;
            margin-top:4px;
            line-height: 24px;color: #FFFFFF;">
            Order Listing
            </div>
            <div class="row" style="ont-family: Montserrat;
            font-style: normal;
            font-weight: normal;
            font-size: 14px;
            line-height: 17px;
            margin-top:7px;
            color: #FFFFFF;">
            Kitchen Orders Listing
            </div>`;
                $('.token-detail').html(html);
                self.time_calculator_grid();
                for (var i = 0; i < orders_on_grid; i++) {
                    var element = $('.order-new').eq(i);
                    element.css('display', 'flex');
                }
            }
        },
        _onDropdownItemClick(ev) {
            // shows accept view when clicked on a dropdown item 
            var self = this;
            var order_id = $(ev.currentTarget).attr('id');
            var pending_order = self.kitchen_order_data.order_data.filter(function (order) {
                return (order.order_progress != 'new' && order.id == order_id);
            })
            if (pending_order && pending_order[0]) {
                var order = pending_order[0];
                var order_html = renderToString('ListViewTemplate', {
                    order: order
                });
                $(".data-body").html(order_html);
                if ($('.list-progress').text().trim() == 'Cancel')
                    $('.list-order').addClass('list-cancel');
                self.time_calculator_list();
                var html = `
                <div class="row" style="margin-top:7px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 20px;line-height: 24px;color: #FFFFFF;">
                Order Token No. ` + order.kitchen_order_name + `
                </div>`;
                $('.token-detail').html(html);
                $('.direction_keys').css('display', 'none');
                if ($('.list-progress').text().trim() == 'Done') {
                    $('#confirmDoneOrder').show();
                    $('.show_tick').show();
                    setTimeout(function () {
                        $('#confirmDoneOrder').hide();
                        $('.show_tick').hide();
                        $('.grid-view').click();
                    }, 1500);
                }
            }
        },
        _OnclickBellButton(event) {
            // function to hide/show dropdown menu for new order
            var self = this;
            event.stopPropagation();
            $(".new-order .dropdown-menu").toggle();
            $(".new-order .dropdown-menu").empty();
            $(".new-order .dropdown-menu").append(`<div class="blank-process-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
            No order found...
            </div>`);
            self.re_render_new_order_list();
            self.re_render_screen_grid();
            $(".bell-notification").hide();
            $(".bell").show();
        },
        _OnclickListHoverButton(event) {
            // render NewOrderTemplate to append in view to see pending orders
            var self = this;
            event.stopPropagation();
            if (self.kitchen_order_data && self.kitchen_order_data.order_data.length > 0) {
                var pending_orders = self.kitchen_order_data.order_data.filter(function (order) {
                    return (order.order_progress != 'new' && order.kitchen_order_name != false);
                })
                if (self.kitchen_order_data.queue_order == "new2old") {
                    pending_orders.reverse();
                };

                var new_arr = pending_orders;
                pending_orders.forEach(order => {
                    var cancel_lines = order.lines.filter(line => {
                        return line.state == 'cancel'
                    });
                    if (cancel_lines.length == order.lines.length) {
                        new_arr = self.arrRemove(pending_orders, order)
                    }
                });

                if (new_arr.length > 0) {
                    var order_html = renderToString('NewOrderTemplate', {
                        order_data: new_arr,
                        type_of_order: 'process'
                    });
                    $('.process-order .dropdown-menu').css('margin-left', '22%');
                    $('.process-order .dropdown-menu').css('margin-top', '10%');
                    $(".process-order .dropdown-menu").empty();
                    $(".process-order .dropdown-menu").append(order_html);
                }
            } else {
                var order_list = $('.dropdown-menu .dropdown-item');
                var blank_list = $('.process-order .dropdown-menu .blank-process-order');
                $('.process-order .dropdown-menu').css('margin-left', '32%');
                $('.process-order .dropdown-menu').css('margin-top', '10%');
                if (order_list.length == 0 && blank_list.length == 0) {
                    $('.process-order .dropdown-menu').empty();
                    $('.process-order .dropdown-menu').append(` <div class="blank-process-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
            No order found...
        </div>`);
                }
            }
            $('.process-order .dropdown-menu').toggle();
        },
        _OnclickListWkNext(event) {
            // function to append view when clicked on next button 
            var self = this;
            if (self.kitchen_order_data && self.kitchen_order_data.order_data.length > 0) {
                var pending_orders = self.kitchen_order_data.order_data.filter(function (order) {
                    return (order.order_progress != 'new' && order.kitchen_order_name != false);
                });
                if (self.kitchen_order_data.queue_order == "new2old") {
                    pending_orders.reverse();
                };

                var new_arr = pending_orders;
                pending_orders.forEach(order => {
                    var cancel_lines = order.lines.filter(line => {
                        return line.state == 'cancel'
                    });
                    if (cancel_lines.length == order.lines.length) {
                        new_arr = self.arrRemove(pending_orders, order)
                    }
                });

                var order = $(event.currentTarget).closest('.list-order');
                order.css('border', 'none');
                var order_id = order.attr('id');
                var progress = order.find('.list-progress').text().trim();
                var next_order_id = '';
                var next_order_type = '';
                if (progress == 'Cancel') {
                    order.removeClass('list-cancel');
                    order.removeClass('list-update');
                    $('.process-order .dropdown-item[id=' + order_id + ']').remove();
                }
                var order_index = 0;
                pending_orders.forEach(function (order) {
                    order_index += 1;
                    if (order.id == order_id) {
                        if (pending_orders[order_index]) {
                            next_order_id = pending_orders[order_index].id;
                            next_order_type = pending_orders[order_index].order_type;
                            var view_order = pending_orders.filter(function (order) {
                                return order.id == next_order_id && order.order_type == next_order_type;
                            })
                            var order_html = renderToString('ListViewTemplate', {
                                order: view_order[0],
                            });
                            $(".data-body").html(order_html);
                            if ($('.list-progress').text().trim() == 'Cancel')
                                $('.list-order').addClass('list-cancel');
                            self.time_calculator_list();
                            var html = `
                    <div class="row" style="margin-top:7px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 20px;line-height: 24px;color: #FFFFFF;">
                    Order Token No. ` + order.kitchen_order_name + `
                    </div>`;
                            $('.token-detail').html(html);
                            $('.direction_keys').css('display', 'none');
                            if ($('.list-progress').text().trim() == 'Done') {
                                swal("Success!", "Order is Successfully Done!", "success");
                                $('.swal-button.swal-button--confirm').trigger('click')
                            }
                        } else {
                            self._OnclickChefHatButton(event);
                        }
                    }
                });
            }
        },
        re_render_screen_grid() {
            var self = this;
            if (self.kitchen_order_data && self.kitchen_order_data.order_data.length > 0) {
                var pending_orders = self.kitchen_order_data.order_data.filter(function (order) {
                    return (order.order_progress != 'new' && order.kitchen_order_name != false);
                });

                var vals = self.kitchen_order_data;
                if (pending_orders.length > 0) {
                    if (vals.queue_order == "new2old") {
                        pending_orders.reverse()
                    };

                    var new_arr = pending_orders;
                    pending_orders.forEach(order => {
                        var cancel_lines = order.lines.filter(line => {
                            return line.state == 'cancel'
                        });
                        if (cancel_lines.length == order.lines.length) {
                            new_arr = self.arrRemove(pending_orders, order)
                        }
                    });

                    var data_html = renderToString('KitchenDataTemplate', {
                        order_data: new_arr,
                        pending_state: false,
                        screen_config: config_id
                    });
                    if (vals.order_data && vals.order_data[0] && vals.order_data[0].orders_on_grid)
                        orders_on_grid = vals.order_data[0].orders_on_grid;
                    $("#kitchen-order-data").empty();
                    $("#kitchen-order-data").append(data_html);
                    if (orders_on_grid == 4 || orders_on_grid == 6)
                        $('#kitchen-order-data').css('height', 'auto');
                    $('.order-content').each(function (index, el) {
                        var last_element = $(el);
                        if (orders_on_grid == 4 || orders_on_grid == 6) {
                            last_element.addClass('main');
                            last_element.find('.grid-template-auto').addClass('categ-body');
                            last_element.find('.inner-element').addClass('categs');
                            last_element.find('.order-footer').addClass('foot');
                            last_element.find('.order-progress').addClass('temp-progress');
                            last_element.find('.order-header').addClass('head');
                        }
                    });
                    self.time_calculator_grid();
                    for (var i = 0; i < orders_on_grid; i++) {
                        var element = $('.order-content').eq(i).parent();
                        element.css('display', 'flex');
                    }
                    $("#list-right").attr('offset', 1);
                    $("#list-left").attr('offset', -1);
                    self.re_render_new_order_list();
                    if ($('#newOrders').hasClass('new_order_showing')) {
                        $('#newOrders').modal('hide');
                        $(".order_modal").css('width', '0%');
                        $(".order_modal").css('height', '0%');
                    }
                    return true;
                }
            }
        },
        time_calculator_grid: function () {
            // shows time icon for each order 
            var self = this;
            if ($('.datetime').length) {
                $('.datetime').each(function (index, el) {
                    let date = ($(el).find('.order_time').text());
                    let currentDate = new Date().toLocaleTimeString(undefined, { hour12: false });
                    // order date
                    var date_list = date.split(":");
                    // order date in milliseconds
                    var prev_date_sec = (date_list[0]) * 60 * 60 + (+date_list[1]) * 60 + (+date_list[2]);
                    // current date
                    var currentDate_list = currentDate.split(":");
                    // current date in milliseconds
                    var curr_date_sec = (currentDate_list[0]) * 60 * 60 + (+currentDate_list[1]) * 60 + (+currentDate_list[2]);

                    var final_time = new Date((curr_date_sec - prev_date_sec) * 1000).toISOString().slice(11, -1);

                    // for hours and minutes extraction
                    var time_lst = final_time.split(':')
                    var minutes = parseInt(time_lst[1]);
                    var hours = parseInt(time_lst[0]);

                    var final_string = '';
                    if (hours > 0)
                        final_string = hours + ' Hour' + ' ' + minutes + ' Minutes';
                    else
                        final_string = minutes + ' Minutes';

                    // add time string to order
                    $(el).closest('.order-content').find('.time-elapsed').text(final_string);

                    var ctx = $(el).find('.timeChart');

                    // chart to show time percentage
                    var chart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            datasets: [{
                                fill: true,
                                backgroundColor: [
                                    '#3C84E2', 'white'
                                ],
                                data: [(minutes / 60) * 100, ((60 - minutes) / 60) * 100,],
                                borderColor: ['#3C84E2', '#3C84E2'],
                                borderWidth: [2, 2]
                            }]
                        },
                        options: {
                            tooltips: {
                                enabled: false
                            },
                            hover: {
                                mode: null
                            },
                            animation: false
                        }
                    });
                    $(el).find('.timeChart').css({
                        'width': '50px',
                        'height': 'auto'
                    })
                });
            }
            if (('.list-datetime').length)
                self.time_calculator_list();
        },
        time_calculator_list: function () {
            $('.list-datetime').each(function (index, el) {
                let date = $(el).find('.list-order-time').text();
                let currentDate = new Date().toLocaleTimeString(undefined, { hour12: false });
                // order date
                var date_list = date.split(":");
                // order date in milliseconds
                var prev_date_sec = (date_list[0]) * 60 * 60 + (+date_list[1]) * 60 + (+date_list[2]);
                // current date
                var currentDate_list = currentDate.split(":");
                // current date in milliseconds
                var curr_date_sec = (currentDate_list[0]) * 60 * 60 + (+currentDate_list[1]) * 60 + (+currentDate_list[2]);

                var final_time = new Date((curr_date_sec - prev_date_sec) * 1000).toISOString().slice(11, -1);
                // for hours and minutes extraction
                var time_lst = final_time.split(':')
                var minutes = parseInt(time_lst[1]);
                var hours = parseInt(time_lst[0]);
                // string to be added in order
                var final_string = '';
                if (hours > 0)
                    final_string = hours + ' Hour' + ' ' + minutes + ' Minutes';
                else
                    final_string = minutes + ' Minutes';
                // add time string to order
                $(el).find('.list-elapsed-time').text(final_string);

                var ctx = $(el).find('.timeListChart');
                var chart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        datasets: [{
                            fill: true,
                            backgroundColor: [
                                '#3C84E2', 'white'
                            ],
                            data: [(minutes / 60) * 100, ((60 - minutes) / 60) * 100,],
                            borderColor: ['#3C84E2', '#3C84E2'],
                            borderWidth: [2, 2]
                        }]
                    },
                    options: {
                        tooltips: {
                            enabled: false
                        },
                        hover: {
                            mode: null
                        },
                        animation: false
                    }
                });
                $(el).find('.timeListChart').css({
                    'width': '50px', 'height': 'auto'
                })
            });
        },
        arrRemove(arr, value) {
            return arr.filter(function (ele) {
                return ele.id != value.id;
            });
        },
        re_render_new_order_list() {
            // adds new orders in dropdown menu 
            var self = this;
            if (self.kitchen_order_data && self.kitchen_order_data.order_data.length > 0) {
                var new_orders = self.kitchen_order_data.order_data.filter(function (order) {
                    return order.order_progress == 'new' && order.kitchen_order_name != false;
                });

                var new_arr = new_orders;
                new_orders.forEach(order => {
                    var cancel_lines = order.lines.filter(line => {
                        return line.state == 'cancel'
                    });
                    if (cancel_lines.length == order.lines.length) {
                        new_arr = self.arrRemove(new_orders, order)
                    }
                });
                if (new_arr.length > 0) {

                    var order_html = renderToString('NewOrderTemplate', {
                        order_data: new_arr,
                        type_of_order: 'new'
                    });
                    
                    $(".new-order .dropdown-menu").empty();
                    $(".new-order .dropdown-menu").append(order_html);
                    $('.blank-new-order').remove();
                    $('.bell').css('display', 'none');
                    $('.notification').css('display', 'block');
                }
            }
        },
        startpolling: function () {
            var self = this;
            const imStatusModelToIds = {};
            let updateBusPresenceTimeout;
            const LOCAL_STORAGE_PREFIX = "presence";
            let lastPresenceTime =
                browser.localStorage.getItem(
                    `${LOCAL_STORAGE_PREFIX}.lastPresence`
                ) || new Date().getTime();
            const throttledUpdateBusPresence = throttleForAnimation(
                function updateBusPresence() {
                    clearTimeout(updateBusPresenceTimeout);
                    const now = new Date().getTime();
                    self.bus_service.send("update_presence", {
                        inactivity_period: now - lastPresenceTime,
                        im_status_ids_by_model: { ...imStatusModelToIds },
                    });
                    updateBusPresenceTimeout = browser.setTimeout(
                        throttledUpdateBusPresence,
                        UPDATE_BUS_PRESENCE_DELAY
                    );
                },
                UPDATE_BUS_PRESENCE_DELAY
            );
            browser.setTimeout(throttledUpdateBusPresence, 250);
            self.bus_service.addEventListener("notification", self._onNotification);
            self.add_channel(self.get_formatted_channel_name());
            self.bus_service.addEventListener("reconnect", throttledUpdateBusPresence);
            globalSelf = self;
            self._fetch_kitchen_order_data();
            self.re_render_new_order_list();
        },
        get_formatted_channel_name: function (channel) {
            return "_wk_pos_kitchen_poll" + "_" + String(1);
        },
        add_channel: function (channel) {
            var self = this;
            if (self.added_channel_list.indexOf(channel) === -1) {
                self.bus_service.addChannel(channel);
                self.added_channel_list.push(channel);
            }
        },
        _onNotification: function (notifications) {
            notifications.detail.forEach(notification => {
                if (notification.type === "websocket_status") {
                    globalSelf.is_websocket_connected = true;
                    globalSelf._update_sync_status();
                }
                if (notification.type === "pos_kitchen_data_update") {
                    globalSelf.is_websocket_connected = true;
                    globalSelf._update_sync_status();
                }
            });
            globalSelf._fetch_kitchen_order_data();
        },
        _update_sync_status: function () {
            var self = this;
            if (self.is_websocket_connected) {
                self.$el.find(".wk_kitchen_socket_status").addClass("active");
                self.$el.find(".wk_kitchen_socket_status .fa-refresh").removeClass("fa-spin");
                self.$el.find(".wk_kitchen_socket_status .fa-refresh").css({
                    color: "rgb(94, 185, 55)",
                });
            }
        },
    }
);