/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

// import ajax from "@web/legacy/js/core/ajax";
// import core from "@web/legacy/js/services/core";
import { session } from '@web/session';

    $(document).ready(function (e) {
        "use_strict";
        // var _t = core._t;

        //terms and condition part
        $("body").on("click", "#terms", function () {

            $("#termsModal").modal("show");

            //appending modal background inside the blue div
            $('.modal-backdrop').appendTo('.terms-block');

            //remove the padding right and modal-open class from the body tag which bootstrap adds when a modal is shown
            $('body').removeClass("modal-open")
            $('body').css("padding-right", "");
        });

        // (function() {

        if (!sessionStorage.length) {
            // Ask other tabs for session storage
            localStorage.setItem('getSessionStorage', Date.now());
        };

        window.addEventListener('storage', function (event) {
            if (event.key == 'getSessionStorage') {
                // Some tab asked for the sessionStorage -> send it
                localStorage.setItem('sessionStorage', JSON.stringify(sessionStorage));
                localStorage.removeItem('sessionStorage');
            } else if (event.key == 'sessionStorage' && !sessionStorage.length) {
                // sessionStorage is empty -> fill it
                var data = JSON.parse(event.newValue), value;
                for (key in data) {
                    sessionStorage.setItem(key, data[key]);
                }
                showSessionStorage();
            }
        });

        function showSessionStorage() {
            var pageURL = $(location).attr("pathname");
            var blacklistpages = $("#popuplist");
            if(blacklistpages.length == 0){
                if(pageURL == '/web/login'){
                    toggleModal(true);
                }
                else{
                    toggleModal(false);
                }
            }
            else{
                blacklistpages = blacklistpages.val().split(",");
                if(blacklistpages.indexOf(pageURL) != -1){
                    toggleModal(false);
                }
                else{
                    toggleModal(true);
                }
            }
            
        }

        function toggleModal(isblacklisted){

            if (sessionStorage.getItem('token') == 'age_verification_t8btYXPR1i' || isblacklisted) {
                $("#mc_modal").css({ 'display': 'none' })
                $("body").css({ 'overflow': 'auto' })
            } else {
                setTimeout(function () {
                    if (sessionStorage.getItem('token') != 'age_verification_t8btYXPR1i' && $("#mc_modal").length) {
                        $("#mc_modal").css({ 'display': 'block' })
                        $("body").css({ 'overflow': 'hidden' })
                    }
                }, 100);
            }
        }

        // window.addEventListener('load', function() {
        showSessionStorage();
        // })

        // })();

        //observe deletion
        var target = document.querySelector('#tnc');
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {

                var nodes = Array.from(mutation.removedNodes);
                var directMatch = nodes.indexOf(target) > -1
                var parentMatch = nodes.some(parent => parent.contains(target));

                if (directMatch) {
                    location.reload();
                } else if (parentMatch) {
                    location.reload();
                }

            });
        });

        var config = {
            subtree: true,
            childList: true,
            attributes: true,
        };
        observer.observe(document.body, config);

        //observe attribute changes in overlay
        var pageURL = $(location).attr("pathname");
        var foo = document.getElementById('mc_modal');

        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                var attrNewValue = mutation.target.getAttribute(mutation.attributeName);
                if ((attrNewValue != "display: block;") && (sessionStorage.getItem('token') != 'age_verification_t8btYXPR1i') && (pageURL.includes('/web/login') == false)) {
                    location.reload();
                }
            })
        });
        if (foo) {
            observer.observe(foo, {
                attributes: true,
                attributeOldValue: true
            });
        }

        ///////// Settings ////////////
        var age_form_element = document.getElementById('age_confirm');
        if (age_form_element != null) {
            var deny_msg = $(age_err_msg).val()
        }

        $("#submit_age").click(function () {
            var dob_element = document.getElementById('per_age');
            if (dob_element != null) {
                var year = $('#year').val();
                var month = $('#month').val();
                var day = $('#day').val();
                var dob = year + '-' + month + '-' + day
                var minimum_age = $("#min_age").val()
                try {
                    if (!year || !month || !day)
                        throw "Date of birth should not be blank";
                    if ($('#tnc').is(':checked') == false)
                        throw "Please select terms & conditions";
                    if (dob) {
                        // dob = new Date(dob);
                        dob = new Date(year,month-1,day);
                        var today = new Date();
                        var age = Math.floor((today - dob) / (365.25 * 24 * 60 * 60 * 1000));
                        if (age >= minimum_age) {
                            $("#mc_modal").css({ 'display': 'none' })
                            $("body").css({ 'overflow': 'auto' })
                            sessionStorage.setItem('token', 'age_verification_t8btYXPR1i');
                        }
                        else {
                            throw deny_msg.substring(0, 45);
                        }
                    }

                } catch (err) {
                    $(".age_error").text(err).css('display', 'block').show()
                }
            }
            else {
                if ($('#tnc').is(':checked') == false) {
                    event.preventDefault();
                    $(".age_error").text("Please select terms & condition").css('display', 'block').show();
                    return false;
                } else {
                    $("#mc_modal").css({ 'display': 'none' })
                    $("body").css({ 'overflow': 'auto' })
                    sessionStorage.setItem('token', 'age_verification_t8btYXPR1i');
                }
            }
        });

        //when deny button clicked
        $("#deny_age").click(function () {
            var msg = deny_msg.substring(0, 45);
            //show error message
            $(".age_error").text(msg).css('display', 'block').show()
        })
    });

