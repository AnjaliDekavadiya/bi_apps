// odoo.define('laundry_iron_business.laundry_service_js', function(require) {
// "use strict";
$(function () {
    // require('web.dom_ready');

    // $( "#expected_pickup_date" ).datepicker({changeMonth: true,changeYear: true, dateFormat: "dd/mm/yy" });

    //Show or hide section of multiple services selection from repair maintenance service request form
    $(".request_to_multiple_services_probc").on("click", function(ev){
        if ($(this).is(':checked')){
            $("#service_id").val("")
            $("#service_id").hide()
            $("#service_id").removeAttr("required", "required")//Remove Required Attribute of Service When untick multiple services
            $("#service label").html("Services")//Change lable Service to Services When tick multiple services
            $(".multiple_service_div_probc").removeClass("o_hidden")
            $(".multiple_service_div_probc").show()
        }
        else{
            $("#service_id").show()
            $("#service_id").attr("required", "True")//Required Service When tick multiple services
            $("#service label").html("Service")//Change lable Services to Service When untick multiple services
            $(".multiple_service_div_probc").load(location.href+" .multiple_service_div_probc>*","")
            $(".multiple_service_div_probc").hide()
        }
    });

});
