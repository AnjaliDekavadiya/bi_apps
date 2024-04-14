odoo.define("courier_management.portal_courier_requests_group_by_search", function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var registry = require("@web/core/registry")
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Template = publicWidget.Widget.extend({
        selector: '.search_group_by_courier_requests',
        events : {
            'change #group_select_courier_requests' : '_onChangeCourierRequests',
            'click #search_courier_requests' : '_onClickCourierRequests'
        },
    //    This is for getting group value of courier requests
        _onChangeCourierRequests: function(){
            let self = this
            var search_value = self.$el.find("#group_select_courier_requests").val();
            ajax.jsonRpc('/courier/requests/group/by', 'call', {
                'search_value': search_value,
            }).then(function(result) {
                self.__parentedParent.$el.find(".search_courier_requests").html(result);
                });
        },
    //    This is for getting search value of courier requests
        _onClickCourierRequests: function(){
            let self = this
            var search_value = self.$el.find("#courier_requests_search_box").val();
            ajax.jsonRpc('/courier/requests/search', 'call', {
                'search_value': search_value,
            }).then(function(result) {
                self.__parentedParent.$el.find(".search_courier_requests").html(result);
                });
        }
    })
publicWidget.registry.search_group_by_courier_requests = Template;
return Template
})
