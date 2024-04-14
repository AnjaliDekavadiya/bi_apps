/* global display_identifier */
    $(function() {
        "use strict";

        $("#service_charge_head").hide()
        $(".o_service_type_head_probc").hide()

        var symbol = ''
        $('.service_type_probc').click(function() {
        var type_id = $(this).val()
        var total_charges = 0.0
        var total_td = 0
        var service_time_td = 0
        var service_time_td1 = 0
        var service_time = 0.0
        var total_time = 0.0
        var total_service_time_td = 0

        if ($(this).is(':checked'))
        {

            $("#service_charge_head").show()
            $(".o_service_type_head_probc").show()

            // $.ajax({
            //     type: 'POST',
            //     url: '/get_car_washing_data', // Replace with the actual route
            //     data: {
            //         type_id: type_id,
            //     },
            $.ajax({
                    type: "POST",
                    dataType: 'json',
                    url: '/get_car_washing_data',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'type_id': type_id}}),
                success: function (data) {
                    if (data){
                        var name = data['result'][0]
                        var service_charges = data['result'][1]
                        var service_time = data['result'][2]
                        total_charges += data['result'][1]
                        
                        total_time += data['result'][3]
                        symbol = data['result'][4]
                        var hrs = parseInt(Number(total_time));
                        var minute = Math.round((Number(total_time)-hrs) * 60);
                        hrs = (hrs < 10 ? '0' : '') + hrs
                        minute = (minute < 10 ? '0' : '') + minute
                        var total_service_time = hrs+':'+minute;
                        var total_charges = total_charges.toFixed(2);

                        $("#service_change_table").append(
                            '<tr t-att-data-service-id='+type_id+'>'+
                                '<td width="50%">' +
                                    '<b>' + name + ' </b>' +
                                '</td>'+
                                '<td width="20%" class="text-center total_time" data-hrs='+hrs+' data-minute='+minute+'>' +
                                    total_service_time +
                                '</td>'+
                                '<td width="20%" class="text-right total_charges" data-charges='+service_charges.toFixed(2)+'>' +
                                    service_charges.toFixed(2) + ' ' + symbol +
                                '</td>'+
                            '</tr>'+
                            '<tr>'
                        );

                    $("#total_charges").find("tr.total_tr").remove()
                    $("#service_change_table tr").find("td.total_charges").each(function(el){
                        total_td += parseFloat($(this).attr("data-charges"))
                    })
                     $("#service_change_table tr").find("td.total_time").each(function(el){
                        service_time_td += parseFloat($(this).attr("data-hrs"))
                        service_time_td1 += parseFloat($(this).attr("data-minute"))

                        var service_time_tdx = (service_time_td < 10 ? '0' : '') + service_time_td
                        var service_time_tdx1 = (service_time_td1 < 10 ? '0' : '') + service_time_td1

                        total_service_time_td = service_time_tdx+':'+service_time_tdx1;
                        
                    })
                    $("#total_charges").append(
                            '<tr class="total_tr">'+
                                '<td width="50%">' + 
                                    '<b>' + 'Total / charges ' + ' </b>' +
                                '</td>'+
                                '<td width="20%">' +
                                    '<b>' + total_service_time_td + ' </b>' +
                                '</td>'+
                                '<td width="20%" class="text-right">' +
                                    '<b>' + total_td.toFixed(2) + ' ' + symbol + '</b>' +
                                '</td>'+
                            '</tr>'
                        );
                    }
                }
               
            });
            
        
        }
        else
        {
            $("#service_change_table").find("tr[t-att-data-service-id="+type_id+"]").remove()
//            var total_td = 0
            $("#service_change_table tr").find("td.total_charges").each(function(el){
                total_td += parseFloat($(this).attr("data-charges"))
                
            })
            $("#service_change_table tr").find("td.total_time").each(function(el){
                service_time_td += parseFloat($(this).attr("data-hrs"))
                service_time_td1 += parseFloat($(this).attr("data-minute"))
                var service_time_tdx = (service_time_td < 10 ? '0' : '') + service_time_td
                var service_time_tdx1 = (service_time_td1 < 10 ? '0' : '') + service_time_td1
                total_service_time_td = service_time_tdx+':'+service_time_tdx1;
                
            })
            $("#total_charges").find("tr.total_tr").remove()
            $("#total_charges").append(
                '<tr class="total_tr">'+
                    '<td width="50%">' + 
                        '<b>' + 'Total / charges' + '</b>' +
                    '</td>'+
                    '<td width="20%">' +
                        '<b>' + total_service_time_td + ' </b>' +
                    '</td>'+
                    '<td width="20%" class="text-right">' +
                        '<b>' + total_td.toFixed(2) + ' ' + symbol + ' </b>' +
                    '</td>'+
                '</tr>'
            );
        }
    });
});


// // odoo.define('fleet_repair_request_management.website_service_type', function(require) {
// // "use strict";

//     // require('web.dom_ready');
//     // var rpc = require('web.rpc');
//     // var ajax = require('web.ajax');
//     $("#service_charge_head").hide()
//     // $(".o_service_type_head").hide() odoo13
//     $(".o_service_type_head_probc").hide()
    
//     var symbol = ''
//     $('.service_type_probc').click(function() {
//         var type_id = $(this).val()
//         var total_charges = 0.0
//         var total_td = 0
//         var service_time_td = 0
//         var service_time_td1 = 0
//         var service_time = 0.0
//         var total_time = 0.0
//         var total_service_time_td = 0
// //        var symbol = ''
//         if ($(this).is(':checked'))
//         {
//             $("#service_charge_head").show()
//             $(".o_service_type_head_probc").show()
            
//             ajax.jsonRpc('/get_car_washing_data', 'call', {
//                 type_id: type_id,
//             }).then(function (data){
//                 if (data){
//                     var name = data[0]
//                     var service_charges = data[1]
//                     var service_time = data[2]
//                     total_charges += data[1]
                    
//                     total_time += data[3]
//                     symbol = data[4]
//                     var hrs = parseInt(Number(total_time));
//                     var minute = Math.round((Number(total_time)-hrs) * 60);
//                     hrs = (hrs < 10 ? '0' : '') + hrs
//                     minute = (minute < 10 ? '0' : '') + minute
//                     var total_service_time = hrs+':'+minute;
//                     var total_charges = total_charges.toFixed(2);

//                     $("#service_change_table").append(
//                         '<tr t-att-data-service-id='+type_id+'>'+
//                             '<td width="50%">' +
//                                 '<b>' + name + ' </b>' +
//                             '</td>'+
//                             '<td width="20%" class="text-center total_time" data-hrs='+hrs+' data-minute='+minute+'>' +
//                                 total_service_time +
//                             '</td>'+
//                             '<td width="20%" class="text-right total_charges" data-charges='+service_charges.toFixed(2)+'>' +
//                                 service_charges.toFixed(2) + ' ' + symbol +
//                             '</td>'+
//                         '</tr>'
//                     );

//                 $("#total_charges").find("tr.total_tr").remove()
//                 $("#service_change_table tr").find("td.total_charges").each(function(el){
//                     total_td += parseFloat($(this).attr("data-charges"))
//                 })
//                  $("#service_change_table tr").find("td.total_time").each(function(el){
//                     service_time_td += parseFloat($(this).attr("data-hrs"))
//                     service_time_td1 += parseFloat($(this).attr("data-minute"))

//                     var service_time_tdx = (service_time_td < 10 ? '0' : '') + service_time_td
//                     var service_time_tdx1 = (service_time_td1 < 10 ? '0' : '') + service_time_td1

//                     total_service_time_td = service_time_tdx+':'+service_time_tdx1;
                    
//                 })
//                 $("#total_charges").append(
//                         '<tr class="total_tr">'+
//                             '<td width="50%">' + 
//                                 '<b>' + 'Total / charges' + '</b>' +
//                             '</td>'+
//                             '<td width="20%">' +
//                                 '<b>' + total_service_time_td + ' </b>' +
//                             '</td>'+
//                             '<td width="20%" class="text-right">' +
//                                 '<b>' + total_td.toFixed(2) + ' ' + symbol + '</b>' +
//                             '</td>'+
//                         '</tr>'
//                     );
//                 }
                
               
//             });
            
        
//         }
//         else
//         {
//             $("#service_change_table").find("tr[t-att-data-service-id="+type_id+"]").remove()
// //            var total_td = 0
//             $("#service_change_table tr").find("td.total_charges").each(function(el){
//                 total_td += parseFloat($(this).attr("data-charges"))
                
//             })
//             $("#service_change_table tr").find("td.total_time").each(function(el){
//                 service_time_td += parseFloat($(this).attr("data-hrs"))
//                 service_time_td1 += parseFloat($(this).attr("data-minute"))
//                 var service_time_tdx = (service_time_td < 10 ? '0' : '') + service_time_td
//                 var service_time_tdx1 = (service_time_td1 < 10 ? '0' : '') + service_time_td1
//                 total_service_time_td = service_time_tdx+':'+service_time_tdx1;
                
//             })
//             $("#total_charges").find("tr.total_tr").remove()
//             $("#total_charges").append(
//                 '<tr class="total_tr">'+
//                     '<td width="50%">' + 
//                         '<b>' + 'Total / charges' + '</b>' +
//                     '</td>'+
//                     '<td width="20%">' +
//                         '<b>' + total_service_time_td + ' </b>' +
//                     '</td>'+
//                     '<td width="20%" class="text-right">' +
//                         '<b>' + total_td.toFixed(2) + ' ' + symbol + ' </b>' +
//                     '</td>'+
//                 '</tr>'
//             );
//         }

//     });





// //    $("#myTable").on("click", function() {
// //        var total_charges = 0.0
// //        var total_time = 0.0
// //        $("table#myTable tr").each(function( i ) {
// //            var checkbox_cell_is_checked = $(this).find('#myCheck').is(':checked');
// //            if (checkbox_cell_is_checked)
// //            {
// //                $("#service_charge_head").show()
// //                // $(".o_service_type_head").show() odoo13
// //                $(".o_service_type_head_probc").show()
// //                var type_id = $(this).find('#typeid_in').val()
// //                var add_cloud = $(this).find('#service_charges').html()

// //                ajax.jsonRpc('/get_car_washing_data', 'call', {
// //                    type_id: type_id,
// //                }).then(function (data){
// //                    if (data){
// //                        var name = data[0]
// //                        var service_charges = data[1]
// //                        var service_time = data[2]
// //                        total_charges += data[1]
// //                        total_time += data[3]
// //                        var symbol = data[4]
// //                        createAnnuallyTableLine(name, service_charges, total_charges, service_time, total_time, symbol);
// //                    }
// //                });
// //            }
// //            else
// //            {
// //                $("#service_change_table tr").remove();
// //                $("#total_charges tr").remove();
// //            }

// //        });
// //    });

// //    function createAnnuallyTableLine(name, service_charges, total_charges, service_time, total_time, symbol)
// //    {
// //        var decimaltime= total_time
// //        var hrs = parseInt(Number(decimaltime));
// //        var minute = Math.round((Number(decimaltime)-hrs) * 60);
// //        if (hrs < 10){
// //            hrs = "0" + hrs
// //        }
// //        if (minute < 10){
// //            minute = "0" + minute
// //        }
// //        var total_service_time = hrs+':'+minute;

// //        $("#service_change_table").append(
// //            '<tr>'+
// //                '<td width="50%">' +
// //                    '<b>' + name + ' </b>' +
// //                '</td>'+
// //                '<td width="20%" class="text-center">' +
// //                    service_time +
// //                '</td>'+
// //                '<td width="20%" class="text-right">' +
// //                    service_charges.toFixed(2) + ' ' + symbol +
// //                '</td>'+
// //            '</tr>'
// //        );
// //        $("#total_charges tr").remove();
// //        var total_charges = total_charges.toFixed(2);
// //        $("#total_charges").append(
// //            '<tr>'+
// //                '<td width="50%">' + 
// //                    '<b>' + 'Total / charges' + '</b>' +
// //                        '</td>'+
// //                '<td width="20%" class="text-center">' + 
// //                    '<b>' 
// //                        + ' ' + total_service_time + 
// //                    '</b>' + 
// //                '</td>' + 
// //                '<td width="20%" class="text-right">'+
// //                    '<b>' 
// //                        + ' ' + total_charges + ' ' + symbol +
// //                    '</b>'+
// //                '</td>'+
// //            '</tr>'
// //        );
// //    }
// // });
