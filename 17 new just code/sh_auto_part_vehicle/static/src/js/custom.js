/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import Dialog from "@web/legacy/js/core/dialog";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.shAddToCart = publicWidget.Widget.extend({
	selector: '#wrap',
	events: {
		'click .sh_add_to_cart': '_onClickAddtoCart',
		'click .js_cls_auto_parts_links': '_onClickLinkFollowContent',
		'click .js_cls_button_open_model': '_onClickLinkOpenModel',
	},


	/**
	 * @constructor
	 */
	init: function () {
		this._super(...arguments);
	},


	/**
	 * @private
	 */
	_onClickAddtoCart: function (ev) {
		var $btnCart = $(ev.currentTarget);
		var productID = $btnCart.attr('data_product_id');
		return jsonrpc("/shop/cart/update_json", {
			product_id: parseInt(productID, 10),
			add_qty: parseInt(1),
			display: false,
		}).then(function (result) {
			if (result) {
				window.location.href = "/shop/cart";
			}
		});

	},

	_onClickLinkFollowContent: function (ev) {
		var self = this;
		var $link = $(ev.currentTarget);
		$link.parents('section').find('.js_cls_auto_parts_links').removeClass('active')
		$link.addClass('active')
		var link = $link.attr('href');
		var $target = self.$el.find(link);
		var scrollLocation = $target.offset().top;

		var scrollinside = $("#wrapwrap").scrollTop();

		$('#wrapwrap').stop().animate({
			scrollTop: scrollLocation + scrollinside - 100
		}, 1500);
	},


	// Open compitible vehicles
	_onClickLinkOpenModel: function (ev) {
		var $btn = $(ev.currentTarget);
		var product_id = $btn.data('product-product-id') || False;
		jsonrpc("/sh_get_product_variant", {
			product_id: product_id,
		}).then((data) => {
			var vehicles = data['vehicles'];
			new Dialog(this, {
				size: "large",
				title: _t("Compitible Products"),
				$content: renderToElement('sh_auto_part_vehicle.CompitibleVehiclesModel', {
					vehicles: vehicles,
				}),
				buttons: [
					{ text: _t("Close"), close: true },
				],
			}).open();
		});
	},
});



publicWidget.registry.ShBrandFilterAttributes = publicWidget.Widget.extend({
	selector: '.sh_custom_attrs',
	events: {
		'input .sh_search_term': '_onChangeTermSearch',
	},
	_onChangeTermSearch: function (ev) {
		ev.preventDefault();
		ev.stopPropagation();
		var term_val = $(ev.currentTarget).val().trim();
		if (term_val) {
			this.$('label[data-search-term]').addClass('d-none');
			this.$('label[data-search-term*="' + term_val.toLowerCase() + '"]').removeClass('d-none');
		} else {
			this.$('label[data-search-term]').removeClass('d-none');
		}
	},

});
