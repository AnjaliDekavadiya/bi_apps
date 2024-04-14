/** @odoo-module **/

import wSaleUtils from "@website_sale/js/website_sale_utils";

const cartHandlerMixin = wSaleUtils.cartHandlerMixin;


cartHandlerMixin._addToCartInPage = function (params) {
    this._super.apply(this, arguments);
    params.force_create = true;
    return this._rpc({
        route: "/shop/cart/update_json",
        params: params,
    }).then(async data => {
        sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
        if (data.cart_quantity && (data.cart_quantity !== parseInt($(".my_cart_quantity").text()))) {
            if ($('div[data-image_width]').data('image_width') !== 'none') {
                await animateClone360($('header .o_wsale_my_cart').first(), this.$itemImgContainer, 25, 40);
            }
            update360CartNavBar(data);
        }
    });
};


function animateClone360($cart, $elem, offsetTop, offsetLeft){
    if (!$cart.length) {
        return Promise.resolve();
    }
    $cart.removeClass('d-none').find('.o_animate_blink').addClass('o_red_highlight o_shadow_animation').delay(500).queue(function () {
        $(this).removeClass("o_shadow_animation").dequeue();
    }).delay(2000).queue(function () {
        $(this).removeClass("o_red_highlight").dequeue();
    });
    return new Promise(function (resolve, reject) {
        if(!$elem) resolve();
        var $imgtodrag = $elem.find('img').eq(0);
        var spans = $('.rotation').find('span');

        spans.each(function() {
            var displayProperty = $(this).css('display');
        
            if (displayProperty === 'block') {
            $imgtodrag = $(this).find('img')
            console.log('Span with display block found!');
            }
        });

        if ($('#360degree_btn').length){
            $imgtodrag = $elem.find('img.product_detail_img')
        }

        if ($imgtodrag.length) {
            var $imgclone = $imgtodrag.clone()
                .offset({
                    top: $imgtodrag.offset().top,
                    left: $imgtodrag.offset().left
                })
                .removeClass()
                .addClass('o_website_sale_animate')
                .appendTo(document.body)
                .css({
                    // Keep the same size on cloned img.
                    width: $imgtodrag.width(),
                    height: $imgtodrag.height(),
                })
                .animate({
                    top: $cart.offset().top + offsetTop,
                    left: $cart.offset().left + offsetLeft,
                    width: 75,
                    height: 75,
                }, 1000, 'easeInOutExpo');

            $imgclone.animate({
                width: 0,
                height: 0,
            }, function () {
                resolve();
                $(this).detach();
            });
        } else {
            resolve();
        }
    });
}

/**
 * Updates both navbar cart
 * @param {Object} data
 */
function update360CartNavBar(data) {
    $(".my_cart_quantity")
        .parents('li.o_wsale_my_cart').removeClass('d-none').end()
        .addClass('o_mycart_zoom_animation').delay(300)
        .queue(function () {
            $(this)
                .toggleClass('fa fa-warning', !data.cart_quantity)
                .attr('title', data.warning)
                .text(data.cart_quantity || '')
                .removeClass('o_mycart_zoom_animation')
                .dequeue();
        });

    $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
    $(".js_cart_summary").replaceWith(data['website_sale.short_cart_summary']);
}





