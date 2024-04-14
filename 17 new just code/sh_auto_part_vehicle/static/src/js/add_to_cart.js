/** @odoo-module **/
	
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { WebsiteSale } from '@website_sale/js/website_sale';
import { jsonrpc } from "@web/core/network/rpc_service";
    
WebsiteSale.include({
	read_events: {
		"click .sh_js_add_cart": "_onClickAddDirectCart",
	},

	/**
	 * Add product to cart and reload the carousel.
	 * @private
	 * @param {Event} ev
	 */
	_onClickAddDirectCart: function (ev) {
		var self = this;
		var $btn = $(ev.currentTarget);
		var productID = $btn.attr("product-product-id");
		var product_id =parseInt(productID)
		jsonrpc("/shop/cart/update_json",{
			product_id: product_id,
			add_qty: 1
		}).then(function (data) {
			var $navButton = $('header .o_wsale_my_cart').first();
			$(".my_cart_quantity").text(data.cart_quantity);
			var $img = $btn.parents(".main").find('.varinat_image_main');
			if ($img){
				wSaleUtils.animateClone($(".o_wsale_my_cart"), $img, 20, 10);
			}
			wSaleUtils.updateCartNavBar(data);
			//var fetch = self._fetchData();
			//var animation = wSaleUtils.animateClone($navButton, $(ev.currentTarget).parents('.card'), 25, 40);
			/*Promise.all([fetch, animation]).then(function (values) {
				wSaleUtils.updateCartNavBar(data);
				if (self.add2cartRerender) {
						self._render();
				}
			});*/
		});
	},
});

