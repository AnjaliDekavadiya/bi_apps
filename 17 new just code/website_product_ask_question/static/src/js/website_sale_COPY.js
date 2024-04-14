odoo.define('website_product_ask_question.website_sale', function (require) {
'use strict';
require('web.dom_ready');
var Dialog = require('web.Dialog');
var core = require('web.core');
var _t = core._t;

var ajax = require('web.ajax');
	   $('#label').hide();

    $(document).ready(function () {

    $("#probc_submit_question").on("click", function(ev){

    	if($('#custom_probc_name').val() == ''){
    		$('#label').show();
    	}
    	if($('#custom_probc_phone').val() == ''){
    		$('#label').show();
    	}
    	if($('#custom_probc_email').val() == ''){
    		$('#label').show();
    	}
    	if($('#custom_probc_disc').val() == ''){
    		$('#label').show();
    	}
    	if($('#custom_probc_detail').val() == ''){
    		$('#label').show();
    	}
        if($('#custom_probc_disc').val() != '' && $('#custom_probc_detail').val() != ''){

		$("#probc_que_submit").modal("hide");		 
    }
		ajax.jsonRpc("/custom/ask/question", 'call', {

			'disc' : $('#custom_probc_description').val(),
			'name' : $('#custom_probc_name').val(),
			'phone': $('#custom_probc_phone').val(),
			'email': $('#custom_probc_email').val(),
			'detail': $('#custom_probc_detail').val(),
		}).then(function (url) {
            var content = $('<div>').html(_t('<p>Your question has been reveived and our team will get back to you asap.<p/>'));
            new Dialog(self, {
                title: _t('Submitted'),
                size: 'medium',
                $content: content,
                buttons: [
                {text: _t('Ok'), close: true}]
            }).open();
        });
	})

	$("#cancel").on("click", function(ev){
        $("#probc_que_submit").modal("hide");      
	})

	})
});
