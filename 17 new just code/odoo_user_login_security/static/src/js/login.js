/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget";
const { Component, onWillUpdateProps, onWillStart } = owl;

// export class LoginSecurity extends Component{

	publicWidget.registry.LogInForm = publicWidget.Widget.extend({
		selector: '.oe_login_form',
		events: {
			'submit': '_onSubmit',
		},

// odoo.define('@auth_signup.signup', [], function (require) {
// 	'use strict';
	
// 	var publicWidget = odoo.loader.modules.get("@web/legacy/js/public/public_widget");
// 	console.log('ddddddddddddddddddddddddddd',publicWidget)
	
// 	// import publicWidget from "@web/legacy/js/public/public_widget";

// // publicWidget.registry.AccountPortalSidebar = PortalSidebar.extend({
// //     selector: '.o_portal_invoice_sidebar',
// //     events: {
// //         'click .o_portal_invoice_print': '_onPrintInvoice',
//     // },



	// 	//--------------------------------------------------------------------------
	// 	// Handlers
	// 	//--------------------------------------------------------------------------

	// 	/**
	// 	 * @private
	// 	 */
		_onSubmit: function () {
			var $btn = this.$('.oe_login_buttons > button[type="submit"]');
			$btn.attr('disabled', 'disabled');
			$btn.prepend('<i class="fa fa-refresh fa-spin"/> ');
		},
	// });
});
