/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
$('.geodir-js-favorite_btn, .js_add_wishlist').on('click', function(e){
    const tgClass = $(this).hasClass('liked');
    const access = $(this).data('access');
    e.preventDefault();
    jsonrpc("/property/wishlist", {
        'toggle': tgClass,
        'access': access
    }).then(function (result){
        if(result.count){
            $('.cart-counter').text(result.count);
        }
    });
    $(this).toggleClass('liked');
});
$('.clear-wishlist').on('click', function (c) {
    const access = $(this).data('access');
    jsonrpc("/property/wishlist/clear", {
        'access': access
    }).then(function (result){
        if(result.count){
            $('.cart-counter').text(result.count);
        }
    });
    $(this).parent().parent().fadeOut('slow', function (c) {});
});
$('#sort_type').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("property_type=") >= 0){
            window.location.href = current_url.replace(/\bproperty_type=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'property_type=' + this.value)
        }else{
            window.location.href = current_url+'&property_type='+this.value
        }
    }else{
        window.location.href = current_url+'?property_type='+this.value
    }
});
$('#price_type').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("price_order=") >= 0){
            window.location.href = current_url.replace(/\bprice_order=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'price_order=' + this.value)
        }else{
            window.location.href = current_url+'&price_order='+this.value
        }
    }else{
        window.location.href = current_url+'?price_order='+this.value
    }
});

$('.price-range').on('change', function() {
    let slider = $(".price-range").data("ionRangeSlider");
    $('#price_start').attr('name', 'price-start').val(slider.result.from);
    $('#price_end').attr('name', 'price-end').val(slider.result.to);
});
$('.area-range').on('change', function() {
    let slider = $(".area-range").data("ionRangeSlider");
    $('#area_start').attr('name', 'area-start').val(slider.result.from);
    $('#area_end').attr('name', 'area-end').val(slider.result.to);
});

$('#check-gym').on('click', function() {
     add_amt_attribute('check-gym', this, 'gym');
});
$('#check-wifi').on('click', function() {
    add_amt_attribute('check-wifi', this, 'wifi');
});
$('#check-parking').on('click', function() {
    add_amt_attribute('check-parking', this, 'parking');
});
$('#check-pool').on('click', function() {
    add_amt_attribute('check-pool', this, 'pool');
});
$('#check-security').on('click', function() {
    add_amt_attribute('check-security', this, 'security');
});
$('#check-laundry').on('click', function() {
    add_amt_attribute('check-laundry', this, 'laundry');
});
$('#check-eq-kitchen').on('click', function() {
    add_amt_attribute('check-eq-kitchen', this, 'kitchen');
});
$('#check-air-condition').on('click', function() {
    add_amt_attribute('check-air-condition', this, 'ac');
});
$('#check-semi-furnish').on('click', function() {
    add_amt_attribute('check-semi-furnish', this, 'smf');
});
$('#check-full-furnish').on('click', function() {
    add_amt_attribute('check-full-furnish', this, 'fuf');
});
$('#check-alarm').on('click', function() {
    add_amt_attribute('check-alarm', this, 'alarm');
});
$('#check-wc').on('click', function() {
    add_amt_attribute('check-wc', this, 'wc');
});
$('.da').on('click', function() {
    let da = ""
    $('.da:checked').each(function(){
        da += $(this).data('id').toString() + ",";
    })
    $('#da').val(da);
});

// FILTERS
// STATUS FILTER
$('.status_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("st=") >= 0){
            window.location.href = current_url.replace(/\bst=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'st=' + this.value.replace(/\s/g, ''))
        }else{
            window.location.href = current_url+'&st='+this.value.replace(/\s/g, '')
        }
    }else{
        window.location.href = current_url+'?st='+this.value.replace(/\s/g, '')
    }
})

// CITY FILTER
$('.city_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("cn=") >= 0){
            window.location.href = current_url.replace(/\bcn=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'cn=' + this.value)
        }else{
            window.location.href = current_url+'&cn='+this.value
        }
    }else{
        window.location.href = current_url+'?cn='+this.value
    }
})

// CATEGORY FILTER
$('.category_filter').on('change', function() {

    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("categ=") >= 0){
            let ap  = current_url.replace(/\bcateg=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'categ=' + this.value.replace(/\s/g, ''))
            window.location.href = ap.replace(/\bdc=[0-9a-zA-Z_@.#+-]{1,50}\b/, '')
        }else{
            window.location.href = current_url+'&categ='+this.value.replace(/\s/g, '')
        }
    }else{
        window.location.href = current_url+'?categ='+this.value.replace(/\s/g, '')
    }
});

// SUB CATEGORY FILTER
$('.sub_category_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("dc=") >= 0){
            window.location.href = current_url.replace(/\bdc=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'dc=' + this.value.replace(/\s/g, ''))
        }else{
            window.location.href = current_url+'&dc='+this.value.replace(/\s/g, '')
        }
    }else{
        window.location.href = current_url+'?dc='+this.value.replace(/\s/g, '')
    }
});

// BEDROOMS FILTER
$('.bedrooms_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("rooms=") >= 0){
            window.location.href = current_url.replace(/\brooms=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'rooms=' + this.value)
        }else{
            window.location.href = current_url+'&rooms='+this.value
        }
    }else{
        window.location.href = current_url+'?rooms='+this.value
    }
});

// BATHROOMS FILTER
$('.bathrooms_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("bathrooms=") >= 0){
            window.location.href = current_url.replace(/\bbathrooms=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'bathrooms=' + this.value)
        }else{
            window.location.href = current_url+'&bathrooms='+this.value
        }
    }else{
        window.location.href = current_url+'?bathrooms='+this.value
    }
});

// FLOORS FILTER
$('.floor_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("floor=") >= 0){
            window.location.href = current_url.replace(/\bfloor=[0-9a-zA-Z_@.#+-]{1,50}\b/, 'floor=' + this.value)
        }else{
            window.location.href = current_url+'&floor='+this.value
        }
    }else{
        window.location.href = current_url+'?floor='+this.value
    }
});

// FACILITY FILTER
$('.facility_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("facility=") >= 0){
            if (current_url.indexOf(",") >= 0) {
                if (current_url.includes("facility=,")) {
                    window.location.href = current_url.replace("facility=,", 'facility=' + this.value + ',')
                } else {
                    window.location.href = current_url.replace(/facility=/, `facility=${this.value},`)
                }
            } else {
                window.location.href = current_url + this.value + ","
            }
        }else{
            window.location.href = current_url+'&facility='+this.value + ","
        }
    }else{
        window.location.href = current_url+'?facility='+this.value + ","
    }
});

// FACILITY FILTER CHECKED
$('.facility_filter_checked').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("facility=") >= 0){
            window.location.href = current_url.replace(`${this.value},`,'')
        }else{
            window.location.href = current_url+'&facility='+''
        }
    }else{
        window.location.href = current_url+'?facility='+''
    }
});

// EXTRA FACILITY FILTER
$('.extra_facility_filter').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("da=") >= 0){
            if (current_url.indexOf(",") >= 0) {
                if (current_url.includes("da=,")) {
                    window.location.href = current_url.replace("da=,", 'da=' + this.value + ',')
                } else {
                    window.location.href = current_url.replace(/da=/, `da=${this.value},`)
                }
            } else {
                window.location.href = current_url + this.value + ","
            }
        }else{
            window.location.href = current_url+'&da='+this.value + ","
        }
    }else{
        window.location.href = current_url+'?da='+this.value + ","
    }
});

// EXTRA FACILITY FILTER CHECKED
$('.extra_facility_filter_checked').on('change', function() {
    let current_url = window.location.pathname + window.location.search;
    if(current_url.indexOf("?") >=0){
        if(current_url.indexOf("da=") >= 0){
            window.location.href = current_url.replace(`${this.value},`,'')
        }else{
            window.location.href = current_url+'&da='+''
        }
    }else{
        window.location.href = current_url+'?da='+''
    }
});


function add_amt_attribute(id, self, name){
    if (self.checked){
        $('#'+id).attr('name', name);
    }else {
        $('#'+id).removeAttr('name');
    }
}

