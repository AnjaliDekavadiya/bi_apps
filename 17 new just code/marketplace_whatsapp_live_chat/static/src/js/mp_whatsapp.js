/** @odoo-module **/
/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
// odoo.define('marketplace_whatsapp_live_chat.button_functionality', function (require) {
// "use strict";

$(document).on('mouseenter','.mp_whatsapp_allow',function(ev){
    var $span = $(this).find('span');
    var str = $span.text();
    var style = {};
    var display = ''
    if (str == 'Activated') {
         display='Click to deactivate'; style = {'color':'red'};}
    else {
        display = 'Click to activate'; style = {'color':'green'}};
    $span.text(display).css(style);
})
.on('mouseleave','.mp_whatsapp_allow',function(ev){
    var $span = $(this).find('span');
    var str = $span.text();
    var display = ''
    if (str == 'Click to deactivate') display='Activated';
    else display = 'Deactivated';
    $span.text(display).css('color','black');
});
    

// });
