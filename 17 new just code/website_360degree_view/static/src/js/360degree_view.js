/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";



publicWidget.registry.Website360View = publicWidget.Widget.extend({
    selector: '#wrap',

    events: {
        'click #360degree_btn': '_360degreeBtnClick',
    },

	_360degreeBtnClick: function (ev) {
		var self = this;

		var product_id = parseInt($(ev.currentTarget).find('.360_product_id').val(),10);
			
		jsonrpc("/shop/360view/", {'product_id': product_id})
		.then(function (vals)
		{  
			var $modal = $(vals);
			$modal.appendTo('#wrapwrap').modal('show').on('hidden.bs.modal', function () {
				$(this).remove();
			});
		});
	},

});
