/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

    // require('web.dom_ready');
    import { jsonrpc } from "@web/core/network/rpc_service";

    // var ajax = require('web.ajax');
    // var core = require('web.core');

    function show_map(lat, log){
        $('#show_store_on_map').empty();
        var mapProp = {
            center: new google.maps.LatLng(lat, log),
            zoom: 10,
            // mapTypeId: 'roadmap',
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        };
        var map = new google.maps.Map(document.getElementById("show_store_on_map"), mapProp);
        var marker = new google.maps.Marker({
            // position: { lat: 28.63067, lng: 77.38209 },
            position: new google.maps.LatLng(lat, log),
            map: map,
            label: 'A',
            title: 'Store Location'
        });
    }

    $(".seller_p_stores").on('click','.product_store',function(){
        var $this = $(this);
        var latitude = parseFloat($this.find('input[type="hidden"][name="store_latitude"]').val());
        var longitude = parseFloat($this.find('input[type="hidden"][name="store_longitude"]').val());
        var store_id = parseInt($this.find('input[type="hidden"][name="seller_store"]').val(),10);
        $('#temp_selected_store').val(store_id);
        if(latitude && longitude){
            show_map(latitude, longitude);
        }
    });

    $(".seller_p_stores").on('click','.store_pickup_on_map',function(){
        var $this = $(this);
        var seller_p_stores = $this.closest('.seller_p_stores');
        var store_id = parseInt(seller_p_stores.find('select[name="store_id"]').val(),10);
        var selected_store_details = seller_p_stores.find('.selected_store_details');
        var latitude = parseFloat(selected_store_details.find('input[type="hidden"][name="store_latitude"]').val());
        var longitude = parseFloat(selected_store_details.find('input[type="hidden"][name="store_longitude"]').val());
        var $div = $this.closest('div');
        var product_store_ids = $div.find('.product_store_ids').data('product_store_ids');
        var values = {
            'product_store_ids' : product_store_ids,
        }
        if(store_id){
            values['selected_store_id'] = store_id;
        }
        jsonrpc("/store/pickup/map", values)
            .then(function (modal) {
                var $modal = $(modal);
                $modal.appendTo($div)
                    .modal('show')
                    .on('hidden.bs.modal', function () {
                        $(this).remove();
                    });
                if(store_id && latitude && longitude){
                    show_map(latitude, longitude);
                }
                else{
                    show_map(0, 0);
                }
            });
    });

    $(".seller_p_stores").on('click','#selected_store_on_map',function(){
        var $this = $(this);
        var seller_p_stores = $this.closest('.seller_p_stores');
        var store_id = seller_p_stores.find('select[name="store_id"]');
        var selected_store = parseInt($('#temp_selected_store').val(),10);
        store_id.val(selected_store).change();
        $('#store_map_modal').modal('hide');
    });

