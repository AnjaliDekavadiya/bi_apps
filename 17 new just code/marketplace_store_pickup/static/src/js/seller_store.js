/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */
// odoo.define('marketplace_store_pickup.seller_store', function (require) {
//     'use strict';
import { jsonrpc } from "@web/core/network/rpc_service";
const { DateTime } = luxon;

    $(".sol_delivery_carrier input[name^='delivery_type']").click(function(){
            
            var $this = $(this);
            var $sol_div = $this.closest('.sol_delivery_carrier')
            var seller_p_stores = $sol_div.find('.seller_p_stores')
            var is_store_delivery = $this.closest('li').find('input[type="hidden"][name="is_store_delivery"]').first().val();
            if(seller_p_stores.length){
                if(is_store_delivery == '1'){
                    seller_p_stores.slideDown("slow");
                }
                else {
                    seller_p_stores.find('select[name="store_id"]').find('option')[0].selected = 'selected';
                    seller_p_stores.find('.selected_store_details').empty();
                    seller_p_stores.slideUp();
                }
            }
        }),
        
        $(".sol_delivery_carrier").on('click','.product_store',function(){
                var $this = $(this);
                var $sol_div = $this.closest('.sol_delivery_carrier')
                var line_store_name = $sol_div.find(".line_store_name");
                var empty_store_pickup_error = $sol_div.find('.empty_store_pickup_error');
                empty_store_pickup_error.hide();
                $sol_div.find('.product_store').not($this).each(function(){
                    var $this = $(this)
                    if($this.hasClass('seller-store2')){
                        $this.removeClass('seller-store2');
                        $this.addClass('seller-store1');
                    }
                });
                if($this.hasClass('seller-store1')){
                    $this.removeClass('seller-store1');
                    $this.addClass('seller-store2');
                    line_store_name.val("Store PickUp");
                }
                else{
                    $this.removeClass('seller-store2');
                    $this.addClass('seller-store1');
                    line_store_name.val("");
                }
            })
    
            
    function check_store_pickup(){
        var count = 1
        var so_details = []
        $('.sol_delivery_carrier').each(function () {
            var $this = $(this);
            var err_list = []
            var sol_ids = $this.find('.sale_order_line_id').data('sale_order_line_ids');
            var empty_store_pickup_error = $this.find('.empty_store_pickup_error');
            var store_id = parseInt($this.find('select[name="store_id"]').first().val(), 10);
            var pickup_date = $this.find("input[name='pickup_date_value']").first().val();
            var pickup_time = $this.find('select[name="pickup_timing"]').first().val();
            var all_delivery = $this.find("input[name^='delivery_type']");
            var err_msg = "";
            all_delivery.each(function(){
                var del_this = $(this);
                var is_store_delivery = del_this.closest('li').find('input[type="hidden"][name="is_store_delivery"]').first().val();
                if(del_this.prop('checked') && is_store_delivery == '1'){
                    if(!store_id){
                        count = 0;
                        err_list.push("Pick Up Store");
                    }
                    else{
                        if(!pickup_date){
                            count = 0;
                            err_list.push("Pick Up Date");
                        }
                        if(!pickup_time){
                            count = 0;
                            err_list.push("Pick Up Time");
                        }
                    }
                    if(err_list.length > 0){
                        err_msg = "Please enter these details correctly to proceed further: "
                        for (var i = 0; i<err_list.length; i++){
                            if(i < err_list.length-1){
                                err_msg = err_msg + err_list[i] +', '
                            }
                            else{
                                err_msg = err_msg + err_list[i] +'.'
                            }
                        }
                        empty_store_pickup_error.empty().html(err_msg).show();
                        try{
                            var thead = empty_store_pickup_error.closest('table');
                            $("html, body").animate({ scrollTop: thead.offset().top }, 500);
                        }
                        catch(err) {
                            console.log("Error:-",err.message);
                        }
                        // setTimeout(function() {empty_store_pickup_error.hide()},12000);
                        return false;
                    }
                    else{
                        var dict = {'line_ids':sol_ids, 'store_id':store_id, 'pickup_date':pickup_date, 'pickup_time':pickup_time,}
                        so_details.push(dict);
                        empty_store_pickup_error.empty().hide();
                    }
                }
            });
        });
        if(count == 1){
            var values = {
                'so_details':so_details,
            }
            jsonrpc('/seller/store/update_sol_update',  values)
              .then(function(result){
            });
            return true;
        }
        else{
            return false;
        }
    }

    $("button[name='o_payment_submit_button']").click(function(event){
        var $this = $(this);
        var check_sol_del_func = check_store_pickup();
        var result = check_sol_del_func;
        if(!result){
            event.preventDefault();
            event.stopPropagation();
        }
    });
    

    $('.seller_p_stores').on('change', "select[name='store_id']",function(event){
        var $this = $(this);
        var seller_p_stores = $this.closest('.seller_p_stores');
        var selected_store_details = seller_p_stores.find('.selected_store_details');
        var $sol_div = $this.closest('.sol_delivery_carrier')
        var sol_ids = $sol_div.find('.sale_order_line_id').data('sale_order_line_ids');
        var sol_id = ''
        var store_id = parseInt($this.val(),10);
        var values = {}
        if(sol_ids){
            var sol_id = sol_ids[0]
        }
        if(store_id){
            values['store_id'] = store_id;
            values['order_lines'] = sol_ids;
            jsonrpc('/selected/store/details', values)
                .then(function(result){
                    var $result =$(result['data']);
                    selected_store_details.empty();
                    $result.appendTo(selected_store_details);
                    var store_time_data = result['store_time']
                    var closed_day = []

                    $.each(store_time_data, function(key, value){
                         if(value == 'closed'){
                            closed_day.push(key)
                        }
                    });

                    function DisableWeekdays(date) {
                        var day = date.getDay();
                        if (closed_day.indexOf(day) > -1) {
                            return [false] ;
                        }
                        else {
                            return [true] ;
                        }
                    }


                    try {
                        
                        var pickup_date = selected_store_details.find('.pickup_date_' + sol_id).first();
                        var target = document.querySelector('.pickup_date_value')
                        target.min = new Date().toISOString().split("T")[0];
                        var today_date = new Date()
                        var test = today_date.toISOString()

                    
        
                        // pickup_date.datetimepicker({
                        //     daysOfWeekDisabled : closed_day,
                        //     format : 'L',
                        //     ignoreReadonly : true,
                        //     useCurrent : false,
                        //     defaultDate : false,
                        //     minDate : new Date(),
                        //     icons: {
                        //         time: 'fa fa-clock-o',
                        //         date: 'fa fa-calendar',
                        //         next: 'fa fa-chevron-right',
                        //         previous: 'fa fa-chevron-left',
                        //         up: 'fa fa-chevron-up',
                        //         down: 'fa fa-chevron-down',
                        //     },
                        // });

                        pickup_date.on("change.datetimepicker", function (e) {
                            var $this = $(this);
                            var pickup_date = $this.find("input[name='pickup_date_value']").first().val();
                            var day = new Date(e.date);
                            values['pickup_date'] = pickup_date
                            const d = new Date(pickup_date)

                            var pickup_timing = selected_store_details.find('select[name="pickup_timing"]')[0];
                            pickup_timing.options.length = 0;

                            var opt1 = document.createElement('option');
                            opt1.value = "";
                            opt1.innerHTML = "Pickup timing...";
                            pickup_timing.add(opt1);

                            var slots = store_time_data[d.getDay()];
                            if(slots != 'closed'){
                                for (var i = 0; i<slots.length; i++){
                                    var opt = document.createElement('option');
                                    var str = slots[i][0]+" - "+slots[i][1];
                                    opt.value = str;
                                    opt.innerHTML = str;
                                    pickup_timing.add(opt);
                                }
                            }
                            else{
                                var opt = document.createElement('option');
                                opt.value = 'closed';
                                opt.innerHTML = "Store Closed";
                            }
                        });
                    } catch (e) { 
                        console.log("Error===============",e);
                    }
                });
        }
        else{
            selected_store_details.empty();
        }
    });


