/** @odoo-module **/
	
import publicWidget from "@web/legacy/js/public/public_widget";
import wSaleUtils from "@website_sale/js/website_sale_utils";
// import { jsonrpc } from "@web/core/network/rpc_service";
import { RPCError } from "@web/core/network/rpc_service";

publicWidget.registry.ProductWishlist.include({

    /**
     * @private
     */
    _addNewProducts: function ($el) {
        var self = this;
        var productID = $el.data('product-product-id');
        if ($el.hasClass('o_add_wishlist_dyn')) {
            productID = parseInt($el.closest('.js_product').find('.product_id:checked').val());;
        }
        var $form = $el.closest('form');
        var templateId = $form.find('.product_template_id').val();
        // when adding from /shop instead of the product page, need another selector
        if (!templateId) {
            templateId = $el.data('product-template-id');
        }
        $el.prop("disabled", true).addClass('disabled');
        var productReady = this.selectOrCreateProduct(
            $el.closest('form'),
            productID,
            templateId,
            false
        );
        var otherBtn = $el.data('other-btn');
        productReady.then(function (productId) {
            productId = parseInt(productId, 10);

            if (productId && !self.wishlistProductIDs.includes(productId)) {
                return self.rpc('/shop/wishlist/add', {
                    product_id: productId,
                }).then(function () {
                    var $navButton = $('header .o_wsale_my_wish').first();
                    self.wishlistProductIDs.push(productId);
                    sessionStorage.setItem('website_sale_wishlist_product_ids', JSON.stringify(self.wishlistProductIDs));
                    self._updateWishlistView();

                    //Shop
                    if($el.closest('form') && !otherBtn){
                        wSaleUtils.animateClone($navButton, $el.closest('form'), 25, 40);
                    }
                    //detail page						
                    if ($el.parents('section#product_detail').find('.row #o-carousel-product .carousel-item.h-100.active').length && !otherBtn) {
                        wSaleUtils.animateClone($("header .o_wsale_my_wish"), $el.parents('section#product_detail').find('.row #o-carousel-product .carousel-item.h-100.active'), 20, 10);
                    }
                    
                    //detail alternate table
                    else if ($el.parents('.main').find('.varinat_image_main').length && otherBtn) {
                        wSaleUtils.animateClone($("header .o_wsale_my_wish"), $el.parents('.main').find('.varinat_image_main'), 20, 10);
                    }


                    // It might happen that `onChangeVariant` is called at the same time as this function.
                    // In this case we need to set the button to disabled again.
                    // Do this only if the productID is still the same.
                    let currentProductId = $el.data('product-product-id');
                    if ($el.hasClass('o_add_wishlist_dyn')) {
                        currentProductId = parseInt($el.closest('.js_product').find('.product_id:checked').val());
                    }
                    if (productId === currentProductId) {
                        $el.prop("disabled", true).addClass('disabled');
                    }
                }).catch(function (e) {
                    $el.prop("disabled", false).removeClass('disabled');
                    if (!(e instanceof RPCError)) {
                        return Promise.reject(e);
                    }
                });
            }
        }).catch(function (e) {
            $el.prop("disabled", false).removeClass('disabled');
            if (!(e instanceof RPCError)) {
                return Promise.reject(e);
            }
        });
    },

});