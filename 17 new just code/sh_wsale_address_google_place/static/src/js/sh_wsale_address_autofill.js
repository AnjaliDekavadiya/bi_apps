/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";
import { debounce } from"@web/core/utils/timing";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.ShWSaleAddressAutofill = publicWidget.Widget.extend({
    selector: '.sh_js_cls_address_autofill',
    events: {
        'input input[name="address"]': '_onChangeAddress',
        'click .sh_js_cls_address_dropdown_item': '_onClickAddressDropdownItem',
    },
    init: function () {
        this._super.apply(this, arguments);
        this.oldAddress = "";
        this.addressSuggestion = []
        this._onChangeAddress = debounce(this._onChangeAddress, 200);
    },
    start: function () {
        this._super.apply(this, arguments);
        var parent = this.$el.parent();
        this.viewTemplate = this.$el[0].dataset.viewTemplate !== undefined ? this.$el[0].dataset.viewTemplate : '';
        this.streetInput = parent.find('input[name="street"]');
        this.cityInput = parent.find('input[name="city"]');
        this.zipInput = this.viewTemplate === 'portal' ? parent.find('input[name="zipcode"]') : parent.find('input[name="zip"]');
        this.stateSelect = document.querySelector('select[name="state_id"]');
        this.countrySelect = document.querySelector('select[name="country_id"]');
    },
    /**
     * For Hide addresses dropdown
     * @param {Element} $el 
     */
    _hideAddressDropdown: function ($el) {
        const addressesDropdown = $el.find('.sh_js_cls_addresses_dropdown');
        if (addressesDropdown) {
            addressesDropdown.remove();
        }
    },
    /**
     * @private
     * @param {Event} ev 
     */
    async _onChangeAddress(ev) {
        var self = this;
        if (ev.currentTarget.value.length) {
            var address = ev.currentTarget.value;
            console.log('\n\n address',address)
            if (address.trim() != self.oldAddress.trim()) {
                self._hideAddressDropdown(self.$el);
                await jsonrpc('/sh_wsale_address_google_place/partial_address',{
                    partial_address: address }).then(function (results) {
                    self.oldAddress = address
                    if (results.length > 0) {
                        self.addressSuggestion = results
                    }
                });
            }
            self._showAddressDropDown();
        }
        else {
            self._hideAddressDropdown(self.$el);
        }
    },
    /**
     * Render the address drop down qweb and append it to the $el.
     * @private
     */
    async _showAddressDropDown() {
        if (this.addressSuggestion !== undefined && this.addressSuggestion.length > 0) {
            this.$el.append(renderToElement('sh_wsale_address_google_place.AddressDropDown', { addresses: this.addressSuggestion }));
        }
        else {
            this._hideAddressDropdown(this.$el);
        }
    },
    /**
     * @private
     * @param {Event} ev 
     */
    async _onClickAddressDropdownItem(ev) {
        
        const addressInput = this.$el.find('input[name="address"]');
        const address = ev.currentTarget.innerText.trim();
        if (addressInput !== undefined) {
            addressInput.val(address);
            this.oldAddress = address;
        }
        const address_vals = await jsonrpc('/sh_wsale_address_google_place/fill_address', {address: address, place_id: ev.currentTarget.dataset.placeId });
        if (address_vals) {
            this.countrySelect.value = address_vals.country !== undefined ? address_vals.country : 0;
            this.countrySelect.dispatchEvent(new Event('change', { bubbles: true }));
            if (address_vals.state) {
                if (this.viewTemplate === 'shop') {
                    new MutationObserver((entries, observer) => {
                        this.stateSelect.value = address_vals.state
                        observer.disconnect();
                    }).observe(this.stateSelect, {
                        childList: true,
                    });
                }
                else {
                    this.stateSelect.value = address_vals.state
                    this.stateSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            this.zipInput.val(address_vals.zip !== undefined ? address_vals.zip : '');
            this.cityInput.val(address_vals.city !== undefined ? address_vals.city : '');
            this.streetInput.val(address_vals.formatted_street !== undefined ? address_vals.formatted_street : address_vals.street !== undefined ? address_vals.street : '');
        }
        this._hideAddressDropdown(this.$el);
    }
});