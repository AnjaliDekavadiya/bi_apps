odoo.define('website_construction_project_page.website_construction', [],function (require) {
'use strict';
require('web.dom_ready');
    $(function() {
        $('.pop').on('click', function() {
            $('.imagepreview').attr('src', $(this).find('img').attr('src'));
            $('#imagemodal').modal('show');   
            
        });
        
//        $('#floor_plan_ref').on('click', function() { odoo13
        $('.floor_plan_ref').on('click', function() {
            $('.imagepreview').attr('src', $(this).find('img').attr('src'));
            $('#fp_imagemodal').modal('show');
            
        });     
        
//        $('#location_plan_ref').on('click', function() { odoo13
        $('.location_plan_ref').on('click', function() {
            $('.imagepreview').attr('src', $(this).find('img').attr('src'));
            $('#lp_imagemodal').modal('show');   
            
        });     
});

$("#slideshow_probc > div:gt(0)").hide();

setInterval(function() { 
  $('#slideshow_probc > div:first')
    .fadeOut(2000)
    .next()
    .fadeIn(2000)
    .end()
    .appendTo('#slideshow_probc');
},  4000);

});
