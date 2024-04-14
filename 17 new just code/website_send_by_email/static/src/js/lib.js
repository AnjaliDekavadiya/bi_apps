odoo.define("website_send_by_email.lib", [] ,function (require) {
		"use strict";
		// require('web.dom_ready');
		var final_value = '';
		// var ajax = require('web.ajax');
    	$('.error').hide();
		$("#sent").on("click", function()
		{ 	
			var output_data = $('#custom_order_id').val()
			var data = $('#order_id').val()
			if (output_data == ""){
            	alert('Please enter your email(s)');

	        return output_data;
	        }
	        var is_email=true;
			// var $result = $("#invalid_email");
			var $result = $("#invalid_email_probc");
			var email = $("#custom_order_id").val();
			var mail = email.split(',')
			$result.text("");
			$.each(mail, function (index, value) {
				var re = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
				if(!re.test(value)) {
					is_email=false;

					var invalid = value + '  ';
					final_value +=  invalid;
				}
			});
			if(is_email == true)
	        {
				// ajax.jsonRpc("/link", 'call',{output_data, data}).then(function(data) 
				// ajax.jsonRpc("/send_email_probc", 'call',{output_data, data}).then(function(data) 
				// {

				// 	$('#custom_order_id').val(output_data)
				// 	$('#sent').attr("data-dismiss","modal");
				// 	$('.error').hide();
				// 	$('#message').modal('show');
				// 	// $('#myModal').modal('hide');
				// 	$('#myModal_send_by_email_probc').modal('hide');
				// });

				$.ajax({
				    type: "POST",
				    dataType: 'json',
				    url: '/send_email_probc',
				    contentType: "application/json; charset=utf-8",
				    data: JSON.stringify({
				        'jsonrpc': "2.0",
				        'method': "call",
				        "params": {
				            "output_data": output_data,
				            "data": data
				        }
				    }),
				    success: function (response) {
				        $('#custom_order_id').val(output_data);
				        $('#sent').attr("data-bs-dismiss", "modal");
				        $('.error').hide();
				        $('#message').modal('show');
				        // $('#myModal').modal('hide');
				        $('#myModal_send_by_email_probc').modal('hide');
				    }
				});

	        }
	        else
	        {
	        	// $('#myModal').modal('show');
				$('#myModal_send_by_email_probc').modal('show');
	        	// $('#invalid_email').show();
	        	$('#invalid_email_probc').show();
				$result.text(final_value + " : Listed emails are Invalid format.");
				$result.css("color", "red");
				return true;
	        }
 	});
});
