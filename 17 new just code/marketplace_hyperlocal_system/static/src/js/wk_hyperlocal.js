/** @odoo-module **/

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
// import ajax from "@web/legacy/js/core/ajax";


publicWidget.registry.hyperlocal = publicWidget.Widget.extend({
    selector: '#hyperlocalsection',
    events: {
        'click .wk_shop_btn_trigger': '_onClick_wk_trigger',
        'keydown #form_goto_shop': '_enter_goto_shop',
        'click #wk_btn_warning' : '_onClick_wk_btn_warning',
        'click .odr_shop_btn_trigger' : '_onClick_odr_shop_btn_trigger'
    },
    _defAddress:true,
    isFacebookApp: function(){
      var ua = navigator.userAgent || navigator.vendor || window.opera;
      return (ua.indexOf("FBAN") > -1) || (ua.indexOf("FBAV") > -1);
    },
    isInstagramApp: function(){
      var ua = navigator.userAgent || navigator.vendor || window.opera;
      var isInstagram = (ua.indexOf('Instagram') > -1) ? true : false;
      return isInstagram
    },
    initAutocomplete:function () {
        var input = $('#pac-input').get(0);
        var searchBox = new google.maps.places.SearchBox(input);
    },
    start: function(){
      var self = this
      if($('i.my_location').length > 0){
          $('i.my_location').removeAttr('style');
          $('div#selected-location').removeAttr('style');
      }
      if (this.$el.find('address-for-shop') != null) {
            jsonrpc('/check/hyperlocal/enable').then(function(res) {
              var enable_hyperlocal = res["enable_hyperlocal"]
              if (res["enable_hyperlocal"])
              {
                  if (self._defAddress) {
                      self.geoFindMe();
                  }
                  self.initAutocomplete()
                  var deflocation = $('#selected-location').val();
              }
          });
      }

    },
    _onClick_odr_shop_btn_trigger:function(e){
      e.preventDefault()

    },
    _onClick_wk_trigger :function(){

      $('#wk_btn_warning').trigger('click');
    },
    _onClick_wk_btn_warning:function(e){
      var address = $('#pac-input').val();
      var self  = this
      jsonrpc("/set/temp/location", {'location':address})
          .then(function (data) {
              self.defAddress = false;
              if (!data['error_msg']){

                  window.location="/get/lat/long"
                }
              else{
                  if ($('#wk_btn_warning_close')){
                      $('#wk_btn_warning_close').trigger('click');
                  }
                  $(".wk_error_msg").text(data['error_msg']).removeClass( "d-none" )
              }
          })
    },
    _enter_goto_shop:function(event){
      if (event.keyCode == 13) {
          $('#wk_shop_btn').click();
          event.preventDefault();
      }
    },
    geoFindMe: function(){
      var self = this
      if (!navigator.geolocation){
          console.log("<p>Geolocation is not supported by your browser</p>");
      }

      function success(position) {
          var latitude  = position.coords.latitude;
          var longitude = position.coords.longitude;
          var latlng = new google.maps.LatLng(latitude, longitude);
          var geocoder = geocoder = new google.maps.Geocoder();
          geocoder.geocode({ 'latLng': latlng }, function (results, status) {
              if (status == google.maps.GeocoderStatus.OK) {
                  if (results[1]) {
                      var formatted_address = results[1].formatted_address;
                      jsonrpc("/set/current/location", {'location':formatted_address,'latitude':latitude,'longitude':longitude})
                          .then(function (data) {
                              if (data) {
                                  $('#pac-input').val(formatted_address);
                                  $('#selected-location').text(formatted_address);
                                  self._defAddress = false;
                              }
                          })
                  }
              }

          });
      }
      function error() {
          console.log("Unable to retrieve your location");
      }
      if(navigator.geolocation && !self.isFacebookApp() && !self.isInstagramApp()){navigator.geolocation.getCurrentPosition(success, error);}
    }
  })
