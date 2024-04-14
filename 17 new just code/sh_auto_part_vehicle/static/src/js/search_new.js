/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import Dialog from "@web/legacy/js/core/dialog";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.sh_motorcycle_shop_search = publicWidget.Widget.extend({
	selector: '#wrap',
	events: {
		'change .id_sh_motorcycle_type_select': '_onChangeTypeGetMake',
		'change .id_sh_motorcycle_make_select': '_onChangeMakeGetModel',
		'change .id_sh_motorcycle_model_select': '_onChangeModelGetYear',
		'click .id_sh_motorcycle_select_diff_bike_btn': '_onClickDiffBikeBtn',
		'click .id_sh_motorcycle_search_diff_bike_close': '_onClickDiffBikeBtnClose',
		'click .id_sh_motorcycle_save_bike_to_garage_btn': '_onClickSaveBikeToGarage',
		'click .js_cls_remove_vehicle_button':'_onClickRemoveVehicle',
	},

	start: function () {
		$('.sh_supported_products_sec .nav-tabs li:first() a').click()
		$('.sh_supported_products_sec .nav-tabs li:first() a').addClass('active')
		this._super.apply(this, arguments);
		var self = this;

		this._onChangeTypeGetMake();
		this._onChangeMakeGetModel();
		this._onChangeModelGetYear();

		$(".id_sh_motorcycle_type_select > option").not('.blank').remove();
		jsonrpc("/sh_motorcycle/get_type_list",).then(function (data) {
			jQuery.each(data, function (key, value) {
				$(".id_sh_motorcycle_type_select").append('<option value="' + value.id + '">' + value.name + "</option>");
			});
		});

		// Set effect from select menu value
		this.save_bike_to_garage_btn_old_style = $(".id_sh_motorcycle_save_bike_to_garage_btn").css("display");



		//when document reload or page refresh
		var self = this;
		var result = self.getQueryString();
		jsonrpc("/sh_motorcycle/is_bike_already_in_garage", {
			type_id: result["type"],
			make_id: result["make"],
			model_id: result["model"],
			year_id: result["year"],
		}).then(function (rec) {
			if (rec.is_bike_already_in_garage) {
				$(".id_sh_motorcycle_save_bike_to_garage_btn").hide();
			} else {
				$(".id_sh_motorcycle_save_bike_to_garage_btn").show();
			}
		});

		$(".id_sh_motorcycle_select_saved_bike_div > a").remove();

		jsonrpc("/sh_motorcycle/get_saved_bike",).then(function (data) {
			jQuery.each(data, function (key, value) {
				$(".id_sh_motorcycle_select_saved_bike_div").append('<a class="dropdown-item" href="' + value.moto_url + '">' + value.name + "</a>");
			});
		});

		var searchParams = new URLSearchParams(window.location.search)

		var paramType = searchParams.get('type');
		var paramMake = searchParams.get('make');
		var paramModel = searchParams.get('model');
		var paramYear = searchParams.get('year');
		var paramPType = searchParams.get('p_type');
		setTimeout(function () {
			if (paramType > 0) {
				var selected = $(document).find('.id_sh_motorcycle_search_diff_bike_form .id_sh_motorcycle_type_select option[value="' + paramType + '"]').attr('selected', 'true');
				if (selected) {
					var x = $(document).find('.id_sh_motorcycle_search_diff_bike_form .id_sh_motorcycle_make_select').prop("disabled", false);;
				}
			}
			if (paramMake > 0) {
				$(document).find('.id_sh_motorcycle_search_diff_bike_form .id_sh_motorcycle_make_select option[value="' + paramMake + '"]').attr('selected', 'true');
			}
			if (paramModel > 0) {
				$(document).find('.id_sh_motorcycle_search_diff_bike_form .id_sh_motorcycle_model_select option[value="' + paramModel + '"]').attr('selected', 'true');
			}
			if (paramYear > 0) {
				$(document).find('.id_sh_motorcycle_search_diff_bike_form .id_sh_motorcycle_year_select option[value="' + paramYear + '"]').attr('selected', 'true');
			}
			/*if(paramPType > 0){
				$(document).find('.id_sh_motorcycle_search_diff_bike_form #id_sh_motorcycle_p_type_select option[value="'+paramPType+ '"]').attr('selected','true');
			}*/
		}, 500);



	},

	/**
	 * @private
	 */
	//Onchange type get make
	_onChangeTypeGetMake: function (ev) {
		var self = this;
		//ev.preventDefault();

		$(".id_sh_motorcycle_make_select > option").not('.blank').remove();

		jsonrpc("/sh_motorcycle/get_make_list", {
			type_id: $(".id_sh_motorcycle_type_select > option:selected").val(),
		}).then(function (data) {
			jQuery.each(data, function (key, value) {
				$(".id_sh_motorcycle_make_select").append('<option value="' + value.id + '">' + value.name + "</option>");
			});

			//self.diable_select_options();
		});

	},

	/**
	 * @private
	 */
	//Onchange make get model
	_onChangeMakeGetModel: function (ev) {
		var self = this;
		//ev.preventDefault();
		$(".id_sh_motorcycle_model_select > option").not('.blank').remove();
		jsonrpc("/sh_motorcycle/get_model_list", {
			type_id: $(".id_sh_motorcycle_type_select > option:selected").val(),
			make_id: $(".id_sh_motorcycle_make_select > option:selected").val(),
		}).then(function (data) {
			jQuery.each(data, function (key, value) {

				$(".id_sh_motorcycle_model_select").append('<option value="' + value.id + '">' + value.name + "</option>");
			});
			//self.diable_select_options();
		});
	},

	/**
	 * @private
	 */
	//Onchange model get year
	_onChangeModelGetYear: function (ev) {
		// ev.preventDefault();
		var self = this;

		$(".id_sh_motorcycle_year_select > option").not('.blank').remove();
		jsonrpc("/sh_motorcycle/get_year_list", {
			type_id: $(".id_sh_motorcycle_type_select > option:selected").val(),
			make_id: $(".id_sh_motorcycle_make_select > option:selected").val(),
			model_id: $(".id_sh_motorcycle_model_select > option:selected").val(),
		}).then(function (data) {
			jQuery.each(data, function (kqy, value) {
				$(".id_sh_motorcycle_year_select").append('<option value="' + value + '">' + value + "</option>");
			});
			//self.diable_select_options();
		});
	},

	/**
		* @private
		*/
	//Onchange product type get go button
	_onChangeTypeGetGoButton: function (ev) {
		ev.preventDefault();
		var self = this;
	},

	_onClickDiffBikeBtn: function (ev) {
		$(".id_sh_motorcycle_search_diff_bike_div").toggle();
		$(".id_sh_motorcycle_select_diff_bike_btn").toggle();
		this.save_bike_to_garage_btn_old_style = $(".id_sh_motorcycle_save_bike_to_garage_btn").css("display");
		$(".id_sh_motorcycle_save_bike_to_garage_btn").hide();
	},

	_onClickDiffBikeBtnClose: function (ev) {
		$(".id_sh_motorcycle_search_diff_bike_div").toggle();
		$(".id_sh_motorcycle_select_diff_bike_btn").toggle();
		$(".id_sh_motorcycle_save_bike_to_garage_btn").css("display", this.save_bike_to_garage_btn_old_style);
	},

	getQueryString: function () {
		var result = {};
		if (!window.location.search.length) return result;
		var qs = window.location.search.slice(1);
		var parts = qs.split("&");
		for (var i = 0, len = parts.length; i < len; i++) {
			var tokens = parts[i].split("=");
			result[tokens[0]] = decodeURIComponent(tokens[1]);
		}
		return result;
	},

	_onClickSaveBikeToGarage: function (ev) {
		var self = this;
		var result = self.getQueryString();
		jsonrpc("/sh_motorcycle/add_bike_to_garage", {
			type_id: result["type"],
			make_id: result["make"],
			model_id: result["model"],
			year_id: result["year"],
			//p_type_id: result["p_type"],
		}).then(function (rec) {
			//refresh the page
			location.reload(true);

		});
	},

	_onClickRemoveVehicle:function (ev) {
		var self = this
		var motorcycle_id = $(ev.currentTarget).data('motorcycle_id')

		new Dialog(this, {
            title: _t("Confirmation"),
            $content: $('<p>' + _t('Are you sure you want to remove the vehicle?') + '</p>'),
            buttons: [
				{text: _t("Yes"), classes: 'btn-primary', click: async (ev) => {
					window.location.href = '/my/garage/remove_bike?id=' + motorcycle_id
				}},
				{text: _t("Cancel"), close: true}
			],
        }).open();
	},

});