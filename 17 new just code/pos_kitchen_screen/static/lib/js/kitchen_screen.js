/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { renderToString } from "@web/core/utils/render";
const orders_on_grid = 3;
const src = window.location.pathname;
const config_id = src.replace(/[^0-9]/g, '');
import { jsonrpc } from "@web/core/network/rpc_service";

if (config_id) {
    $(document).ready(function () {
        // some click events on kitchen screen 
        $('.o_pos_kitchen_management').click(function (e) {
            if ($(".new-order .dropdown-menu").is(":visible")) {
                $(".new-order .dropdown-menu").hide();
                $(".bell-notification").hide();
                $(".bell").show();
            }
            if ($('.process-order .dropdown-menu').is(":visible")) {
                $('.process-order .dropdown-menu').hide();
            }
            if ($('.blank-filter-order').is(':visible')) {
                $('.blank-filter-order').hide();
            }
        });
        // cancel button 
        $("#newOrders").on('click', '.wk-cancel-order', function (event) {
            $('.modal-confirm').css('display', 'none');
            $('.modal-cancel').show();
            $('input#ofs').prop('checked', true);
        });

        $("#newOrders").on('click', '.accept_wk_cancel', function (event) {
            $('.modal-cancel').hide();
            $('.modal-confirm').show();
        });

        $("#newOrders").on('click', '.action_cancel', function (event) {
            event.preventDefault();
            var order = $(event.currentTarget);
            var order_id = order.find().attr('value');
            var order_type = order.find().attr('value');
            var atr = $('.action_cancel').attr('action');
            var $inputs = $('.action_confirm :input');
            // not sure if you wanted this, but I thought I'd add it.
            // get an associative array of just the values.

            var values = {};
            $inputs.each(function () {
                values[this.name] = $(this).val();
            });
            if (order_type) {
                values['order_type'] = order_type
            }
            jsonrpc(atr, {
                'screen_id': config_id,
                'order_type': order_type,
                'config_id': values['config_id'],
            }).then(function (vals) {
                console.log('confirm', vals)
            });
        });

        $("#newOrders").on('change', function (e) {
            var wk_otf_count = 0
            var out_stock_products = $('.out-of-stock .cancel-modal-product .out-of-stock-product')
            out_stock_products.each((i, el) => {
                if ($(el).is(':checked')) {
                    wk_otf_count += 1;
                }
            })
            if (($("input#reason").is(':checked') && $('#cancel-reason').val() == '') || ($('#ofs').is(':checked') && wk_otf_count <= 0)) {
                $('.cancel_order_div').addClass('unclickable_wk');
                $('.cancel_order_div').css('pointer-events', 'none');
            } else {
                $('.cancel_order_div').removeClass('unclickable_wk');
                $('.cancel_order_div').css('pointer-events', 'auto');
            }
        })

        $("#newOrders").on('click', '.wk-confirm, .wk-cancel', function (event) {
            var order_id = $('.modal-order').attr('id');
            var dropdownItem = $('.new-order .dropdown-item[id=' + order_id + ']');
            dropdownItem.remove();
            var dropdown_new = $('.new-order .dropdown-item').length;
            if (!dropdown_new) {
                $('.new-order .dropdown-menu').append(`
                        <div class="blank-new-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
                            No new orders found...
                        </div>`)
            }
            $('#newOrders').removeClass('new_order_showing');
            $('#newOrders').modal('hide');
            $(".order_modal").css('width', '0%');
            $(".order_modal").css('height', '0%');
            if ($(event.target).hasClass('wk-cancel')) {
                setTimeout(function () {
                    swal("Cancelled!", "Order is Successfully Cancelled!", "success");
                }, 200);
                setTimeout(function () {
                    $('.swal-button.swal-button--confirm').trigger('click')
                }, 1500);
            }
        });

        $('body').on('click', '#list-left', function () {
            var offset = $('#list-left').attr('offset');
            var rightOffset = $('#list-right').attr('offset');
            var newOffset = parseInt(offset) * orders_on_grid;
            if (newOffset >= 0) {
                for (var i = 0; i < orders_on_grid; i++) {
                    var element = $('.order-content').eq(newOffset + i).parent();
                    $('.order-content').eq(newOffset + orders_on_grid + i).parent().css('display', 'none')
                    element.css('display', 'flex');
                };
                $("#list-right").attr('offset', parseInt(rightOffset) - 1);
                $("#list-left").attr('offset', parseInt(offset) - 1);
            };
        });

        $('body').on('click', '#list-right', function () {
            var offset = $('#list-right').attr('offset');
            var leftOffset = $('#list-left').attr('offset');
            var newOffset = parseInt(offset) * orders_on_grid;
            var e_length = $('.order-content').length;
            if (e_length > newOffset) {
                for (var i = 0; i < orders_on_grid; i++) {
                    var element = $('.order-content').eq(newOffset + i).parent();
                    $('.order-content').eq(newOffset - i - 1).parent().css('display', 'none')
                    element.css('display', 'flex');
                }
                $("#list-right").attr('offset', parseInt(offset) + 1);
                $("#list-left").attr('offset', parseInt(leftOffset) + 1);
            }
        });

        $('.new-order .dropdown-menu').on('click', '.dropdown-item', function (event) {
            var order_id = $(event.currentTarget).attr('id');
            var order_type = $(event.currentTarget).find('.order-type').text().replace(/\s/g, '')
            jsonrpc("/pos/" + config_id + "/order/show/", {
                'order_id': parseInt(order_id),
                'order_type': order_type
            }).then(function (vals) {
                if (vals && vals.order_data && vals.order_data[0]){
                    var order_html = renderToString('ModalBodyData', {
                        order: vals.order_data[0],
                        config: config_id
                    });
                }
                $(".modal-replace").html(order_html);
                $(".modal-title").html(vals.order_data[0].kitchen_order_name);
                $('.new-order .dropdown-menu').hide()
                $("#newOrders").modal('show');
                $("#newOrders").addClass('new_order_showing');
                $("#newOrders").css('padding-left', '0%');
                $(".order_modal").css('width', '100%');
                $(".order_modal").css('height', '100%');
            });
        });

        $('.filter-view').on('click', function (event) {
            var product_elements = $('.process-order .product_id');
            var product_data = {};
            var product_name_by_id = {};
            event.stopPropagation();
            if (product_elements.length == 0) {
                $('.blank-filter-order').toggle();
            } else {
                product_elements.each(function (index, el) {
                    var element = $(el);
                    var product_name = element.find('.product_name').text().trim();
                    var quantity = element.find('.product_qty').text().trim();
                    var token_no = element.closest('.dropdown-item').find('.token_no').text().trim();
                    var order_id = element.closest('.dropdown-item').attr('id');
                    var order_type = element.closest('.dropdown-item').find('.order-type').text();
                    var product_id = element.attr('product_id');
                    if (product_id in product_data) {
                        product_data[product_id]['lines'].push({
                            'token_no': token_no,
                            'quantity': quantity,
                            'order_id': order_id,
                            'order_type': order_type
                        })
                        product_data[product_id]['total'] += parseInt(quantity)
                    } else {
                        product_data[product_id] = {
                            'total': parseInt(quantity),
                            'lines': [{
                                'token_no': token_no,
                                'quantity': quantity,
                                'order_id': order_id,
                                'order_type': order_type
                            }]
                        };
                    }
                    if (!(product_id in product_name_by_id))
                        product_name_by_id[product_id] = product_name;
                });
                if (product_data && product_name_by_id)
                    var filter_html = renderToString('FilterViewTemplate', {
                        product_data: product_data,
                        product_name_by_id: product_name_by_id
                    });
                $('.data-body').html(filter_html);
                $('.direction_keys').css('display', 'none');
                var html = `
                            <div class="row" style="margin-top:7px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 20px;line-height: 24px;color: #FFFFFF;">
                            Order Filter
                            </div>`;
                $('.token-detail').html(html);
            }
        });

        $('.data-body').on('click', '.card-header', function (event) {
            var product_id = $(event.currentTarget).attr('id');
            $(this).next(".data-content").slideToggle("slow");
            $('.data-content').each(function (index, el) {
                if (product_id != $(el).attr('content'))
                    $(el).css('display', 'none');
            });
        });

        $('.data-body').on('click', '#kitchen-order-data .wk-remove-grid', function (event) {
            var order = $(event.currentTarget).closest('.order-new');
            order.remove();
        })

        $(".data-body").on('click', '.wk-done-list', function (event) {
            var order = $(event.currentTarget).closest('.list-order');
            var order_id = order.attr('id');
            $('.wk-next').click();
            $('.process-order .dropdown-item[id=' + order_id + ']').remove();
            var dropdown_new = $('.process-order .dropdown-item').length;
            if (!dropdown_new) {
                $('.process-order .dropdown-menu').append(`
                <div class="blank-process-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
                    testt   No orders found...
                </div>`);
            }
        });

        $(".data-body").on('click', '.wk-cook', function (event) {
            $('.action_cook').parent().css('display', 'none');
            $('.action_done').parent().css('display', 'block');
            $('.list-process-state').show();
            $('.list-queue-state').css('display', 'none');
            var order = $(event.currentTarget).closest('.list-order');
            var order_id = order.attr('id');
            $('.process-order .dropdown-item[id=' + order_id + ']').find('.process-order-process').css('display', 'block');
            $('.process-order .dropdown-item[id=' + order_id + ']').find('.process-order-queue').css('display', 'none');
        });

        $(".data-body").on('click', '.wk-done-orderline', function (event) {
            $('.list-process-state').show();
            $('.list-queue-state').css('display', 'none');
            var order = $(event.currentTarget).closest('.list-order');
            var order_id = order.attr('id');
            $('.process-order .dropdown-item[id=' + order_id + ']').find('.process-order-process').css('display', 'block');
            $('.process-order .dropdown-item[id=' + order_id + ']').find('.process-order-queue').css('display', 'none');
            setTimeout(function () {
                $(event.currentTarget).closest('.action_done_orderline').replaceWith('<i class="fa fa-check" style="color:green;font-size:24px;"/>');
                var elements = $('.list-order-line');
                var count = 0;
                elements.each(function (index, el) {
                    var tick = $(el).find('.fa-check');
                    if (tick.length)
                        count++;
                })
                if (count == elements.length) {
                    $('.list-done-state').show();
                    $('.list-process-state').css('display', 'none');
                    $('.process-order .dropdown-item[id=' + order_id + ']').remove()
                    setTimeout(function () {
                        swal("Success!", "Order is Successfully Done!", "success");
                    }, 1500);
                    setTimeout(function () {
                        $('.swal-button.swal-button--confirm').trigger('click')
                    }, 3000);
                    setTimeout(function () {
                        $('.grid-view').click();
                    }, 700);
                }
            }, 500);
        });

        function render_grid_order_on_done() {
            // renders grid orders after an order is marked as done
            var rightOffset = parseInt($("#list-right").attr('offset'));
            var is_last_order = orders_on_grid - (rightOffset * orders_on_grid - $('.order-new').length - 1)
            var iter = 0;
            if (is_last_order == 1) {
                iter = ((rightOffset - 2) * orders_on_grid) - 1;
                var leftOffset = parseInt($("#list-left").attr('offset'));
                if (leftOffset >= 0) {
                    $("#list-right").attr('offset', rightOffset - 1);
                    $("#list-left").attr('offset', leftOffset - 1);
                }
            } else
                iter = ((rightOffset - 1) * orders_on_grid) - 1;
            for (var i = iter; i < (rightOffset - 1) * orders_on_grid; i++) {
                $('.order-new').eq(i).css('display', 'flex');
            }
        }

        function order_done(event) {
            // when order is marked done on grid view 
            var element = $(event.currentTarget).closest('.order-new');
            var rightOffset = parseInt($("#list-right").attr('offset'));
            var order = $(event.currentTarget).closest('.order-content');
            var order_id = order.attr('id');
            $('.process-order .dropdown-item[id=' + order_id + ']').remove();
            element.remove();
            var dropdown_new = $('.process-order .dropdown-item').length;
            if (!dropdown_new) {
                $('.process-order .dropdown-menu').append(`
                <div class="blank-process-order" style="height:auto;padding:5px;font-family: Montserrat;font-style: normal;font-weight: normal;font-size: 14px;line-height: 17px;color: #7F4167;">
                    No orders found...
                </div>`)
            }
            var next_element = $('.order-new').eq(rightOffset * orders_on_grid - 1)
            next_element.css('display', 'flex');
            if (!next_element.length) {
                setTimeout(render_grid_order_on_done, 200);
            }
        }

        $(".data-body").on('click', '.wk-done-grid,.wk-remove-grid', function (event) {
            setTimeout(order_done, 500, event);
        });

        $(".data-body").on('click', '.wk-done-grid', function (event) {
            event.preventDefault();
            var element = $(event.currentTarget).closest('.action_done');
            var order = $(event.currentTarget).closest('.order-content');
            var atr = element.attr('action')
            var $inputs = $('.action_done :input');
            // not sure if you wanted this, but I thought I'd add it.
            // get an associative array of just the values.
            var values = {};
            $inputs.each(function () {
                values[this.name] = $(this).val();
            });
            var order_type = order.attr('order-type');
            jsonrpc(atr, {
                'screen_config': values['screen_config'],
                'order_type': order_type,
            }).then(function (vals) {
                swal("Success!", "Order is Successfully Done!", "success");
                $('.process-order .dropdown-menu').empty();
                setTimeout(function () {
                    $('.swal-button.swal-button--confirm').trigger('click')
                }, 1500);
            });
        });

        $(".data-body").on('click', '.wk-done-orderline', function (event) {
            event.preventDefault();
            var element = $(event.currentTarget).closest('.action_done_orderline');
            var atr = element.attr('action');
            var $inputs = $('.action_done_orderline :input');
            // not sure if you wanted this, but I thought I'd add it.
            // get an associative array of just the values.
            var values = {};
            $inputs.each(function () {
                values[this.name] = $(this).val();
            });
            jsonrpc(atr, {
                'screen_config': values['screen_config'],
                'order_type': values['order_type']
            }).then(function (vals) {
                console.log('vals', vals);
            });
        });

        $("#newOrders").on('click', '.wk-confirm', function (event) {
            event.preventDefault();
            var order = $(event.currentTarget);
            var order_type = order.prev().prev().attr('value');
            var atr = $('.action_confirm').attr('action');
            var $inputs = $('.action_confirm :input');
            // not sure if you wanted this, but I thought I'd add it.
            // get an associative array of just the values.
            var values = {};
            $inputs.each(function () {
                values[this.name] = $(this).val();
            });
            if (order_type) {
                values['order_type'] = order_type;
            }
            jsonrpc(atr, {
                'order_type': order_type,
                'config_id': values['config_id'],
            }).then(function (vals) {
                console.log('confirm', vals)
            });
        });

        function requestFullScreen(element) {
            var isInFullScreen = (document.fullscreenElement && document.fullscreenElement !== null) ||
                (document.webkitFullscreenElement && document.webkitFullscreenElement !== null) ||
                (document.mozFullScreenElement && document.mozFullScreenElement !== null) ||
                (document.msFullscreenElement && document.msFullscreenElement !== null);
            var docElm = document.documentElement;
            if (!isInFullScreen) {
                if (docElm.requestFullscreen) {
                    docElm.requestFullscreen();
                } else if (docElm.mozRequestFullScreen) {
                    docElm.mozRequestFullScreen();
                } else if (docElm.webkitRequestFullScreen) {
                    docElm.webkitRequestFullScreen();
                } else if (docElm.msRequestFullscreen) {
                    docElm.msRequestFullscreen();
                }
                var enter = document.getElementById('qms_enter');
                enter.style.display = 'none';
                var leave = document.getElementById('qms_leave');
                leave.style.display = 'initial';
                var close = document.getElementById('qms_close');
                if (close && close.style)
                    close.style.display = 'none';
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    document.mozCancelFullScreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
                var enter = document.getElementById('qms_enter');
                enter.style.display = 'initial';
                var leave = document.getElementById('qms_leave');
                leave.style.display = 'none';
                var close = document.getElementById('qms_close');
                if (close && close.style)
                    close.style.display = 'initial';
            }
        }

        $('.qms_fs').on('click', function () {
            var elem = document.body; // Make the body go full screen.
            requestFullScreen(elem);
        });
    })
}