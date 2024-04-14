/** @odoo-module */

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import { jsonrpc } from "@web/core/network/rpc_service";

    $(document).ready(function(){


        $('[id^=adblockMultiple]').carousel({
          interval: 10000
        })

        $('[id^=adblockMultiple] .carousel-item').each(function(){
          var next = $(this).next();

          if (!next.length) {
            next = $(this).siblings(':first');
          }
          next.children(':first-child').clone().appendTo($(this));
          if (next.next().length>0) {
            next.next().children(':first-child').clone().appendTo($(this));
          }
          else {
          	$(this).siblings(':first').children(':first-child').clone().appendTo($(this));
          }
        });

        $('.ad_img_browse_btn').click(function(){
            $('#imgUpload').trigger('click');
        });

        $("#portal_add_banner").on("click", function(){
            var block_id = parseInt($(this).data('block-id'))
            var ad_banner_link;
            if(document.getElementById("ad_banner_link")!=null){
                ad_banner_link = document.getElementById("ad_banner_link").value
            } 
            var ele = document.getElementById("imgUpload")
            var files = !!ele.files ? ele.files : [];
            // if (!files.length || !window.FileReader) return;

            if($('#imgUpload').val().split('\\').pop().trim() == ""){
                $("#ad_banner_link").removeClass('ad_link_error')
                $("#imgUpload").parent().addClass('image_error')
                $("#show_req_panel").css("display", "inline-block")
            }
            else if(ad_banner_link==''){
                $("#imgUpload").parent().removeClass('image_error')
                $("#ad_banner_link").addClass('ad_link_error')
                $("#show_req_panel").css("display", "inline-block")
            }
            else{
                $("#ad_banner_link").removeClass('ad_link_error')
                $("#imgUpload").parent().removeClass('image_error')
                $("#show_req_panel").css("display", "none")

                if (!(!files.length || !window.FileReader) && (/^image/.test( files[0].type))){
                    var ReaderObj = new FileReader();
                    ReaderObj.readAsDataURL(files[0]);
                    ReaderObj.onloadend = function(){
                        var block = this.result.split(";");
                        var realData = block[1].split(",")[1];
                        var image_name = files[0].name
                        $('.ad_loader').show();
                        jsonrpc("/set/block/banner" ,{
                            'block_id': block_id,
                            'image': realData,
                            'ad_banner_link': ad_banner_link,
                            'ad_img_name': image_name,
                        }).then(function(data){
                            $('.ad_loader').hide();
                            location.reload(true);
                            $("#img_success_upd").css("display", "inline-block")
                        })
                    }
                }

                else{
                    $('.ad_loader').show();
                    jsonrpc("/set/block/banner",{
                        'block_id': block_id,
                        'ad_banner_link': ad_banner_link,
                    }).then(function(data){
                        $('.ad_loader').hide();
                        location.reload(true);
                        $("#img_success_upd").css("display", "inline-block")
                    })
                }
            }
        });

        $("#imgUpload").on("change", function(){
            var files = !!this.files ? this.files : [];
            if (!files.length || !window.FileReader) return; // Check if File is selected, or no FileReader support
            if (/^image/.test( files[0].type)){ //  Allow only image upload
                var ReaderObj = new FileReader(); // Create instance of the FileReader
                ReaderObj.readAsDataURL(files[0]); // read the file uploaded
                ReaderObj.onloadend = function(){ // set uploaded image data as background of div
                    $("#image_preview").css("background-image", "url("+this.result+")");
                }
            }
            else{
                alert("Upload an image");
            }
        });

        $('tr.ad_block_row').click(function() {
            var href = $(this).find("a").attr("href");
            if (href) {
                window.location = href;
          }
        });

        $('.book_ad_block_button').on('click',function (event) {
            var block_id = parseInt($(this).data('block-id'))
            var disabledDates = []
            $('.ad_loader').show();
            jsonrpc("/book/ad/block",{
                'block_id': block_id,
            }
            ).then(function (data) {
                var $modal = $(data['website_advertisement_manager.website_ad_block_book_modal'])
                disabledDates = data.block_date_list
                $('.ad_loader').hide();
                $modal.appendTo('#wrap')
                .modal('show')
                .on('shown.bs.modal', function () {  
                    document.querySelector("#input_ad_date_from").min= new Date().toISOString().split("T")[0];
                    document.querySelector("#input_ad_date_to").min= new Date().toISOString().split("T")[0];
                })
                .on('hidden.bs.modal', function () {
                    $(this).remove();
                })
            });
        });
    });

    $(document).on('change', '#input_ad_date_from , #input_ad_date_to', function(){
        var block_price_unit = $("#AdBlockModal").find('.block_price_unit').find('.oe_currency_value').text()
        var total_amount = $('.block_total_amount').find('.oe_currency_value').text()
        var ad_date_from = $("#input_ad_date_from").val()
        var ad_date_to = $("#input_ad_date_to").val()
        var interval= luxon.Interval.fromDateTimes(luxon.DateTime.fromISO(ad_date_from), luxon.DateTime.fromISO(ad_date_to));
        var diff = interval.toDuration(['days']);
        var days = parseInt(diff.toFormat('d')) +1

        if (days==NaN || days<0 || days==0){days = 1}
        var total_amount = parseFloat(parseFloat(block_price_unit) * days).toFixed(2)
        if(total_amount == NaN){
            total_amount = block_price_unit
        }
        if (ad_date_from!='' && ad_date_to!=''){
            $('.total_days').text(days)
            $('.block_total_amount').find('.oe_currency_value').text(total_amount)
        }
    })

    $(document).on('click', '#block_add_to_cart', function(event){
        event.preventDefault()
        var $form = $(this).closest('form');
        var amount= parseFloat($('.block_price_unit').find('.oe_currency_value').html()).toFixed(2)
        var block_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val());
        var ad_date_from = $("#input_ad_date_from").val()
        var ad_date_to = $("#input_ad_date_to").val()
        var interval= luxon.Interval.fromDateTimes(luxon.DateTime.fromISO(ad_date_from), luxon.DateTime.fromISO(ad_date_to));
        var diff = interval.toDuration(['days']);
        var days = parseInt(diff.toFormat('d')) +1
        var error = 0
        var error_msg = ''

        if(ad_date_from=='' || ad_date_to==''){
            error = 1
            error_msg = "Dates cannot be blank."
        }
        if(error==1){
            $("#input_ad_date_from").addClass("has_error")
            $("#input_ad_date_to").addClass("has_error")
            $('div.show_error').css("display","");
            $('span.error_msg').text(error_msg)
            $('.total_days').text('1')
            $('.block_total_amount').find('.oe_currency_value').text(amount)
        }
        else{
            $('.ad_loader').show();
            jsonrpc('/validate/ad/dates',{
                'block_id': block_id,
                'ad_date_from': $("#input_ad_date_from").val(),
                'ad_date_to': $("#input_ad_date_to").val(),
            }).then(function(data){
                debugger;
                if(data.error){
                    error_msg = data.error_msg
                    $("#input_ad_date_from").addClass("has_error")
                    $("#input_ad_date_to").addClass("has_error")
                    $('div.show_error').css("display","");
                    $('span.error_msg').text(error_msg)
                    $('.total_days').text('1')
                    $('.block_total_amount').find('.oe_currency_value').text(amount)
                }
                else{
                    $("#input_ad_date_from").removeClass("has_error")
                    $("#input_ad_date_to").removeClass("has_error")
                    $('div.show_error').css("display","none");
                    if(event.isDefaultPrevented()){
                        $form.submit();
                    }
                }
                $('.ad_loader').hide();
            })
        }
    });

