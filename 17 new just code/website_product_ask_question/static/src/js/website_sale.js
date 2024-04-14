/** @odoo-module **/

// import core from "@web/legacy/js/services/core";
import Dialog from '@web/legacy/js/core/dialog';

import { _t } from "@web/core/l10n/translation";
import { WebsiteSale } from '@website_sale/js/website_sale';
import publicWidget from '@web/legacy/js/public/public_widget';


publicWidget.registry.ProductAskQuestion = WebsiteSale.extend({
    selector: '#probc_que_submit',
    events: {
        'click #probc_submit_question': '_onClickSubmitQuestion',
        'click #cancel': '_onClickCancelQuestion',
    },
   
    _onClickSubmitQuestion: function(ev){
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
        $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/custom/ask/question',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'disc' : $('#custom_probc_description').val(),
                    'name' : $('#custom_probc_name').val(),
                    'phone': $('#custom_probc_phone').val(),
                    'email': $('#custom_probc_email').val(),
                    'detail': $('#custom_probc_detail').val()}}),
                success: function (url) {
                        var content = $('<div>').html(_t('<p>Your question has been reveived and our team will get back to you asap.<p/>'));
                        const dialog = new Dialog(this, {
                            title: _t('Submitted'),
                            size: 'medium',
                            $content: content,
                            buttons: [
                            {text: _t('Ok'), close: true}]
                        });
                        dialog.open();
                   
                }
            });
    },

    _onClickCancelQuestion: function(ev){
        $("#probc_que_submit").modal("hide");
    },
});
