/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteTrackingAlternative = publicWidget.registry.websiteSaleTrackingAlternative.extend({
    selector: 'span.fa.fa-4x.fa-thumbs-up.mx-auto.rounded-circle.bg-primary',

    start: function (ev) {
        this.trigger_up('tracking_lead');
        return this._super.apply(this, arguments);
    },
});

export default publicWidget.registry.websiteTrackingAlternative;
