$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;

    $('.email_check_probc').change(function emailchack() 
   {
        var email = $(".email_check_probc").val();
        var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (!filter.test(email)) 
        {
           $("#email_msg_probc").html('Please enter valid Email ID.').show(1000);
           email.focus;
           return false;
        }
        $("#email_msg_probc").hide(2000);
   });
});
});
