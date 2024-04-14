/** @odoo-module **/

// odoo.define('disable_right_click_website_product.right_click_disable', function (require) {
// "use strict";
//   require('web.dom_ready');
  
  // var publicWidget = require('web.public.widget');
import publicWidget from "@web/legacy/js/public/public_widget";

    
  publicWidget.registry.imagedisableform = publicWidget.Widget.extend({
     selector: '#o-carousel-product',
     init: function () {
         this._super.apply(this, arguments);
     },
     start: function () {
         var self = this;
        this._Disable_Right_Click();
            
         return this._super.apply(this, arguments);
     },
     _Disable_Right_Click: function(){
      var self = this;
        $('.carousel-inner').bind("contextmenu", function(e){
            e.preventDefault();
          }, false);
          $(".carousel-indicators").bind("contextmenu", function(e){
            e.preventDefault();
          }, false);
     },
  });
  

    