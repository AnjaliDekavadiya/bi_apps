/** @odoo-module */

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";
var bounds;
var map;
var marker;
patch(PartnerDetailsEdit.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        onMounted(() => {
            var self = this
            
            if(self.pos.company.enable_google_map){
                
                bounds = new google.maps.Geocoder();
                var latlng = new google.maps.LatLng(-34.397, 150.644);
                var mapOptions = {
                    zoom: 14,
                    center: latlng,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                }
                map = new google.maps.Map(document.getElementById('map'), mapOptions);


                var partner = this.props.partner;
                var address = partner.address
                this.customer_locations_on_map(address)
                self.initMap()
            }

            Object.assign(this.props.imperativeHandle, {
                save: () => this.saveChanges(),
            });
        });
    },

    customer_locations_on_map(address) {
        if(address){

            var self = this;
            bounds = new google.maps.Geocoder();

            bounds.geocode( { 'address': address}, function(results, status) {
                if (status == 'OK') {
                    map.setCenter(results[0].geometry.location);
                    
                    map.setCenter(results[0].geometry.location);
                    var infowindow = new google.maps.InfoWindow(
                    {   content: '<b>'+address+'</b>',
                        size: new google.maps.Size(150,50)
                    });
                    if (marker) {
                        marker.setMap(null);
                        if (infowindow) infowindow.close();
                    }
                    marker = new google.maps.Marker({
                        map: map,
                        draggable: true,
                        position: results[0].geometry.location
                    });


                    google.maps.event.addListener(marker, 'dragend', function() {
                        bounds.geocode({
                            latLng: marker.getPosition()
                        }, function(add_data) {
                            infowindow.setContent(add_data[0].formatted_address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
                            infowindow.open(map, marker);

                            var postal_code_updated = false
                            var city_updated = false
                            for (var i = 0; i < add_data[0].address_components.length; i++) {
                                var add_component_type =  add_data[0].address_components[i].types[0];
                                var add_component =  add_data[0].address_components[i];

                                var splitted = add_data[0].formatted_address.split(",");
                                var street = add_data[0].formatted_address.slice(0, add_data[0].formatted_address.indexOf(','))
                                
                                if(splitted.length >= 3)
                                {
                                    street = add_data[0].formatted_address.split(",",3);


                                    $("input[name='street']").val(street[0]+street[1]);
                                    self.changes['street'] = street[0]+street[1];
                                }

                                if(add_component_type ==  "locality")
                                {
                                    if(add_component_type ==  "locality")
                                    {
                                        city_updated = true
                                        var city = add_component.long_name;
                                        $("input[name='city']").val(city)
                                        self.changes['city'] = city;
                                    }else{
                                        $("input[name='city']").val('')
                                        self.changes['city'] = '';
                                    }
                                }else{
                                    if(city_updated == false){
                                        $("input[name='city']").val('');
                                        self.changes['city'] = '';
                                    }
                                }


                                if(add_component_type == "postal_code")
                                {
                                    postal_code_updated = true
                                    var zip = add_component.long_name;
                                    $("input[name='zip']").val(zip);
                                    self.changes['zip'] = zip;
                                }else{
                                    if(postal_code_updated == false){
                                        $("input[name='zip']").val('');
                                        self.changes['zip'] = '';
                                    }
                                }

                                if(add_component_type == "country")
                                {
                                    self.orm.searchRead(
                                        "res.country",
                                        [['name', '=', add_component.long_name]],
                                        ["id","name"]
                                    ).then(function(country_data) {
                                        if(country_data && country_data[0])
                                        {
                                            var country = country_data[0]['id']
                                            self.changes['country_id'] = country;
                                            $("select[name='country_id']").val(country).change();
                                        }
                                        
                                    });
                                }
                                if (add_component_type == "administrative_area_level_1"){

                                    self.orm.searchRead(
                                        "res.country.state",
                                        [['name', '=', add_component.long_name]],
                                        ["id","name"]
                                    ).then(function(state_data) {
                                        if(state_data && state_data[0])
                                        {
                                            var state = state_data[0]['id']
                                            
                                            self.changes['state_id'] = state;
                                            $('select[name="state_id"]').append('<option value="'+state+'">'+state_data[0]['name']+'</option>');
                                            $("select[name='state_id']").val(state).change();
                                        }
                                        
                                    });
                                }
                            }
                        });
                    });
                    google.maps.event.addListener(marker, 'click', function() {
                        if (marker.formatted_address) {
                            infowindow.setContent(marker.formatted_address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
                        } else {
                            infowindow.setContent(address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
                        }

                        bounds.geocode({
                            latLng: marker.getPosition()
                        }, function(add_data) {
                            infowindow.setContent(add_data[0].formatted_address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
                            infowindow.open(map, marker);

                            var postal_code_updated = false
                            var city_updated = false
                            
                            for (var i = 0; i < add_data[0].address_components.length; i++) {
                                var add_component_type =  add_data[0].address_components[i].types[0];
                                var add_component =  add_data[0].address_components[i];

                                var splitted = add_data[0].formatted_address.split(",");
                                var street = add_data[0].formatted_address.slice(0, add_data[0].formatted_address.indexOf(','))
                                
                                if(splitted.length >= 3)
                                {
                                    street = add_data[0].formatted_address.split(",",3);


                                    $("input[name='street']").val(street[0]+street[1]);
                                    self.changes['street'] = street[0]+street[1];
                                }

                                if(add_component_type ==  "locality")
                                {
                                    if(add_component_type ==  "locality")
                                    {
                                        city_updated = true
                                        var city = add_component.long_name;
                                        $("input[name='city']").val(city)
                                        self.changes['city'] = city;
                                    }else{
                                        $("input[name='city']").val('')
                                        self.changes['city'] = '';
                                    }
                                }else{
                                    if(city_updated == false){
                                        $("input[name='city']").val('');
                                        self.changes['city'] = '';
                                    }
                                }


                                if(add_component_type == "postal_code")
                                {
                                    postal_code_updated = true
                                    var zip = add_component.long_name;
                                    $("input[name='zip']").val(zip);
                                    self.changes['zip'] = zip;
                                }else{
                                    if(postal_code_updated == false){
                                        $("input[name='zip']").val('');
                                        self.changes['zip'] = '';
                                    }
                                }

                                if(add_component_type == "country")
                                {
                                    self.orm.searchRead(
                                        "res.country",
                                        [['name', '=', add_component.long_name]],
                                        ["id","name"]
                                    ).then(function(country_data) {
                                        if(country_data && country_data[0])
                                        {
                                            var country = country_data[0]['id']
                                            self.changes['country_id'] = country;
                                            $("select[name='country_id']").val(country).change();
                                        }
                                        
                                    });
                                }
                                if (add_component_type == "administrative_area_level_1"){
                                    self.orm.searchRead(
                                        "res.country.state",
                                        [['name', '=', add_component.long_name]],
                                        ["id","name"]
                                    ).then(function(state_data) {
                                        if(state_data && state_data[0])
                                        {
                                            var state = state_data[0]['id']
                                            
                                            self.changes['state_id'] = state;
                                            $('select[name="state_id"]').append('<option value="'+state+'">'+state_data[0]['name']+'</option>');
                                            $("select[name='state_id']").val(state).change();
                                        }else{
                                            self.changes['state_id'] = false;
                                            $("select[name='state_id']").val('None').change();
                                        }
                                        
                                    });
                                }
                            }
                        });

                        infowindow.open(map, marker);
                    });

                    google.maps.event.trigger(marker, 'click');
                } else {
                    alert('Geocode was not successful for the following reason: ' + status);
                }
            });
        }
    },


    initMap () {
        var self = this;
        var searchBox = new google.maps.places.SearchBox($('#search_location')[0]);
        var markers = [];

        searchBox.addListener('places_changed', function() {
            var places = searchBox.getPlaces();

            if (places.length == 0) {
                return;
              }

            if(places)
                {
                    self.customer_locations_on_map(places[0].formatted_address);
                }
        });
    }
        
});
