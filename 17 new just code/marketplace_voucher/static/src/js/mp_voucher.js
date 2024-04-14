/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import { jsonrpc } from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";

    publicWidget.registry.websiteCoupon.include({
        _onClickApplyVocuher: function (ev) {
			ev.preventDefault();
			this.ApplyVoucher(ev);
		},
        _onKeyUpVoucherCode: function(ev){
			if (ev.keyCode == 13) {
				this.ApplyVoucher(ev);
			}
		},
        ApplyVoucher(ev) {
            var $el = $(ev.currentTarget);
            var $js_cart_summary = $el.closest(".o_website_sale_checkout");
            var $form = $el.closest("form");
            var $error_msg = $js_cart_summary.find(".error_msg");
            var $success_msg = $js_cart_summary.find(".success_msg");
            var $promo_input = $form.find("input[name='promo']");
            var mp_seller_id = $promo_input.data('mp_seller_id');
            var secret_code = $promo_input.val();
            var $mp_loader = $('.mp-box-review_loader');
            $mp_loader.show();
			jsonrpc(
				"/website/voucher/",
				{
				secret_code: secret_code,
          		seller_id: mp_seller_id
				},
			).then(function (result) {
				console.log('result',result)
                $mp_loader.hide();
				if (result['status']) {
					$success_msg.css('display', 'block')
					$success_msg.html(result['message']);
					$success_msg.fadeOut(3000);
					$(location).attr('href', "/shop/cart");
				}
				else {
					$error_msg.css('display', 'block')
					$error_msg.html(result['message']);
					$error_msg.fadeOut(5000);
				}
			});
		},

    });

$( document ).ready(function() {
	$(".wk_modal").append("<h1 id='empty_cart' class='text-primary p-5'>NO COUPONS ARE AVAILABLE</h1>")
	$('.oe_website_sale').on("click",".btn_modal_vouchers",function(ev){
 	  	$('#empty_cart').hide()
			var seller = this.id
			var voucher_count= $('.voucher').length
			$('.voucher').each(function(i,data){
			if($(data).find("#seller_name").text() && $(data).find("#seller_name").text()!= seller){
				$(this).hide()
				voucher_count-=1
			}
			else{
				$(this).show()
			}
			if (voucher_count == 0){
				$('#empty_cart').show()


			}
		})
	})
});
// })
