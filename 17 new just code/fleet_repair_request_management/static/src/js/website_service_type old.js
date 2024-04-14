odoo.define('fleet_repair_request_management.website_service_type', function(require) {
"use strict";

    require('web.dom_ready');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    $("#service_charge_head").hide()
    // $(".o_service_type_head").hide() odoo13
    $(".o_service_type_head_probc").hide()
    $("#myTable").on("click", function() {
        var total_charges = 0.0
        var total_time = 0.0
        $("table#myTable tr").each(function( i ) {
            var checkbox_cell_is_checked = $(this).find('#myCheck').is(':checked');
            if (checkbox_cell_is_checked)
            {
                $("#service_charge_head").show()
                // $(".o_service_type_head").show() odoo13
                $(".o_service_type_head_probc").show()
                var type_id = $(this).find('#typeid_in').val()
                var add_cloud = $(this).find('#service_charges').html()

                ajax.jsonRpc('/get_car_washing_data', 'call', {
                    type_id: type_id,
                }).then(function (data){
                    if (data){
                        var name = data[0]
                        var service_charges = data[1]
                        var service_time = data[2]
                        total_charges += data[1]
                        total_time += data[3]
                        var symbol = data[4]
                        createAnnuallyTableLine(name, service_charges, total_charges, service_time, total_time, symbol);
                    }
                });
            }
            else
            {
                $("#service_change_table tr").remove();
                $("#total_charges tr").remove();
            }

        });
    });

    function createAnnuallyTableLine(name, service_charges, total_charges, service_time, total_time, symbol)
    {
        var decimaltime= total_time
        var hrs = parseInt(Number(decimaltime));
        var minute = Math.round((Number(decimaltime)-hrs) * 60);
        if (hrs < 10){
            hrs = "0" + hrs
        }
        if (minute < 10){
            minute = "0" + minute
        }
        var total_service_time = hrs+':'+minute;

        $("#service_change_table").append(
            '<tr>'+
                '<td width="50%">' +
                    '<b>' + name + ' </b>' +
                '</td>'+
                '<td width="20%" class="text-center">' +
                    service_time +
                '</td>'+
                '<td width="20%" class="text-right">' +
                    service_charges.toFixed(2) + ' ' + symbol +
                '</td>'+
            '</tr>'
        );
        $("#total_charges tr").remove();
        var total_charges = total_charges.toFixed(2);
        $("#total_charges").append(
            '<tr>'+
                '<td width="50%">' + 
                    '<b>' + 'Total / charges' + '</b>' +
                        '</td>'+
                '<td width="20%" class="text-center">' + 
                    '<b>' 
                        + ' ' + total_service_time + 
                    '</b>' + 
                '</td>' + 
                '<td width="20%" class="text-right">'+
                    '<b>' 
                        + ' ' + total_charges + ' ' + symbol +
                    '</b>'+
                '</td>'+
            '</tr>'
        );
    }
});
