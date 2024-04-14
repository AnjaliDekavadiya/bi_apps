/** @odoo-module **/
/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.websiteCoupon = publicWidget.Widget.extend({
	selector: '.oe_website_sale, #open_vouchers_modal',
	events: {
		'click .wk_voucher': '_onClickApplyVocuher',
		'click .copy_code': '_onClickCopyCode',
		'keyup #voucher_8d_code': '_onKeyUpVoucherCode',
	},
	_onClickApplyVocuher: function (ev) {
		ev.preventDefault();
		this.ApplyVoucher();
	},
	ApplyVoucher() {
		var secret_code = $("#voucher_8d_code").val();
		jsonrpc("/website/voucher/",
			{
				secret_code: secret_code
			}).then(function (result) {
			if (result['status']) {
				$(".success_msg").css('display', 'block')
				$(".success_msg").html(result['message']);
				$(".success_msg").fadeOut(3000);
				$(location).attr('href', "/shop/cart");
			}
			else {
				$(".error_msg").css('display', 'block')
				$(".error_msg").html(result['message']);
				$(".error_msg").fadeOut(5000);
				$("#voucher_8d_code").val('');
			}
		});
	},
	_onClickCopyCode: function (ev) {
		ev.stopImmediatePropagation()
		ev.stopPropagation()
		ev.preventDefault()
		var $fa = $(ev.currentTarget);
		if (navigator.clipboard){
			navigator.clipboard.writeText($fa.prev().text())
		}
		else{
			var $temp = $("<input>");
			$fa.parent().append($temp);
			$temp.val($fa.prev().text());
			// console.log($temp.select())
			$temp.select().focus();
			document.execCommand('Copy');
			$temp.remove();
			$('.copy_code').text("Copy Code");
		}
		$fa.text("Code Copied");
		setTimeout(function() {
			$fa.text("Copy Code");
		}, 2000);
	},
	_onKeyUpVoucherCode: function(ev){
		if (ev.keyCode == 13) {
			this.ApplyVoucher();
		}
	},
});
