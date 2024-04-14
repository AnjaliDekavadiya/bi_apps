/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import "@website_sale/js/website_sale_delivery";
import "@payment/js/payment_form";

publicWidget.registry.websiteSaleDelivery.include({

    events: Object.assign({}, publicWidget.registry.websiteSaleDelivery.prototype.events, {
        "click .sol_delivery_carrier input[name^='delivery_type']" : '_onSOLCarrierClick',
    }),

    init: function(){
        this._super.apply(this, arguments);
        this.del_div = false;
    },

    start: function (){
        var self = this;
        $(".sol_delivery_carrier").toArray().forEach((SolCarrier, k) => {
            var $this = $(SolCarrier);
            var SOLCarrier = $this.find("input[name^='delivery_type']:first");
            const radio = document.querySelector('#'+SOLCarrier.attr('id'));
            var carrier_id = SOLCarrier.val();
            var sol_ids = $this.find('.sale_order_line_id').data('sale_order_line_ids');
            var values = {'carrier_id': carrier_id, 'order_lines': sol_ids};
            $('#shipping_per_product_loader').show();
            this.rpc('/shop/sol/update_carrier', values).then(function(result){
                result['del_div'] = $this;
                SOLCarrier.prop('checked', true);
                self._handleCarrierUpdateResult(radio);
            });
        });
        return this._super.apply(this, arguments);
    },

    _setCarrierResultBadge: function(result, del_div){
        var $carrierBadge = del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .o_wsale_delivery_badge_price');
        var $check_sol_del = del_div.find('input[name^="line_delivery_name"]');

        if (result.status === true) {
                // if free delivery (`free_over` field), show 'Free', not '$0'
                if (result.is_free_delivery) {
                    $carrierBadge.text(_t('Free'));
                } else {
                    $carrierBadge.html(result.sol_delivery_amount);
                }
                $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
                $check_sol_del.val("SOL Delivery Selected");
        } else {
            $carrierBadge.addClass('o_wsale_delivery_carrier_error');
            $carrierBadge.text(result.error_message);
            $check_sol_del.val("");
        }
    },

    _handleCarrierUpdateResultBadge: function (result) {
        $('#shipping_per_product_loader').hide();
        if(result['del_div']){
            this._setCarrierResultBadge(result, result['del_div']);
        }
        else if(this.del_div){
            this._setCarrierResultBadge(result, this.del_div);
        }
        else{
            this._super.apply(this, arguments);
        }

    },

    _handleCarrierUpdateResultCustom: async function(values){
        const result = await this.rpc('/shop/sol/update_carrier', values)
        this.result = result;
        this._handleCarrierUpdateResultBadge(result);
        // if (carrierInput.checked) {
            var amountDelivery = document.querySelector('#order_delivery .monetary_field');
            var amountUntaxed = document.querySelector('#order_total_untaxed .monetary_field');
            var amountTax = document.querySelector('#order_total_taxes .monetary_field');
            var amountTotal = document.querySelectorAll('#order_total .monetary_field, #amount_total_summary.monetary_field');

            amountDelivery.innerHTML = result.new_amount_delivery;
            amountUntaxed.innerHTML = result.new_amount_untaxed;
            amountTax.innerHTML = result.new_amount_tax;
            amountTotal.forEach(total => total.innerHTML = result.new_amount_total);
            // we need to check if it's the carrier that is selected
            if (result.new_amount_total_raw !== undefined) {
                this._updateShippingCost(result.new_amount_total_raw);
            }
            this._updateShippingCost(result.new_amount_delivery);
        // }
        this._enableButton(result.status);
        let currentId = result.carrier_id
        const showLocations = document.querySelectorAll(".o_show_pickup_locations");

        for (const showLoc of showLocations) {
            const currentCarrierId = showLoc.closest("li").getElementsByTagName("input")[0].value;
            if (currentCarrierId == currentId) {
                this._specificDropperDisplay(showLoc);
                break;
            }
        }
    },

    _onSOLCarrierClick: async function(ev){
        var $this = $(ev.currentTarget);
        var self = this;
        var $payButton = $('button[name="o_payment_submit_button"]');
        $payButton.prop('disabled', true);
        $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
        var del_div = $this.closest('.sol_delivery_carrier');
        this.del_div = del_div;
        var carrier_id = $this.val();
        var sol_ids = del_div.find('.sale_order_line_id').data('sale_order_line_ids');
        var $empty_sol_del_error = del_div.find('.empty_sol_del_error');
        var values = {'carrier_id': carrier_id, 'order_lines': sol_ids};
        $empty_sol_del_error.hide();
        $('#shipping_per_product_loader').show();
        self._handleCarrierUpdateResultCustom(values)
    },
});

publicWidget.registry.PaymentForm.extend({

    _checkSolDelivery: function(event){
        var count = 1
        $('.line_delivery_name').each(function () {
            var $this = $(this);
            var $empty_sol_del_error = $this.closest('.sol_delivery_carrier').find('.empty_sol_del_error');
            if($(this).val() == ''){
                count = 0;
                $empty_sol_del_error.show();
                try{
                    $(".toggle_summary_div.d-none").removeClass("d-none");
                    var thead = $empty_sol_del_error.closest('table');
                    $("html, body").animate({ scrollTop: thead.offset().top }, 500);
                }
                catch(err) {
                    console.log("Error:-",err.message);
                }
                setTimeout(function() {$empty_sol_del_error.hide()},12000);
                return false;
            }
        });
        return count;
    },
    _submitForm: function (ev) {
        ev.preventDefault();
        var result = this._checkSolDelivery();
        if(result == 1){
            this._super.apply(this, arguments);
        }
    }
});
