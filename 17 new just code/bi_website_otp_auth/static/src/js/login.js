/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

    publicWidget.registry.LoginForm = publicWidget.Widget.extend({
        selector: '.oe_login_form',

        events: {
            'click .otp_next_btn': '_OnNextButtonClick',
            'click .otp_resend': '_OnResendButtonClick',
        },

        start: function(){
            var $otp_option = $(this.$el).find('.form-group.field-otp');
            if($otp_option.length > 0){
                $(this.$el).find('#password').css('display','none');
                $(this.$el).find('label[for="password"]').css('display','none');
                $(this.$el).find('button[type="submit"]').css('display','none');
            }
        },

        _OnNextButtonClick: function(ev){
            ev.preventDefault();
            var self = this;
            $('.form-group.field-otp').css('display','block');
            $('.form-group.field-login').css('display','none');
            var $radio = $('input[type="radio"]:checked');
            var $email = $('input[name="login"]').val();
            var $limit = $('input[name="otp_limit"]').val();
            if(!$email){
                $('#email_msg').removeClass('d-none');
                return false;
            }
            else{
                if($radio.val() === 'pwd'){
                    $('.form-group.field-otp').css('display','none');
                    $('.otp_next_btn').css('display','none');
                    $('#password').css('display','block');
                    $('label[for="password"]').css('display','block');
                    $('button[type="submit"]').css('display','block');
                }
                if($radio.val() === 'otp'){
                    jsonrpc('/check/login', {
                    	'login':$email,
                    }).then(function (login) {
                        if(login === true){
                            $('.form-group.field-otp').after('<p id="otp_msg" class="alert alert-danger">Failed to send OTP !! Wrong username/email.</p>');
                        }
                        else{
                            var $otp_type = $('input[name="otp_type"]').val();
                            self.VerifyOtp($otp_type, $limit, $email);
                        }
                    });
                }
            }
        },

        VerifyOtp: function($otp_type, $limit, $email){
            if($otp_type === 'text'){
                $('#password input').attr('type','text');;
            }
            $('.form-group.field-otp').css('display','none');
            $('.otp_next_btn').css('display','none');
            $('label[for="password"]').text('Enter Otp');
            $('#password').attr('placeholder','Enter Otp');;
            $('#password').css('display','block');
            $('button[type="submit"]').css('display','block');
            $('#password').after('<p id="otp_msg" class="alert alert-success">OTP has been sent to given Email Address : '+ $email +'.</p>');
            
			jsonrpc('/send/otp',{
					'login':$email,
                	'name':$email,
			}).then(function(result){
                if (result){
                    var Timer = setInterval(function(){
                        if($limit < 0){                 
                            clearInterval(Timer);
                            $('#bi_login_otpvalue').text('');
                            $('#otp_msg').remove();
                            $('#password').after('<a class="btn btn-link float-right otp_resend" href="#">Resend OTP</a>')
                            $('button[type="submit"]').attr('disabled',true);
                            jsonrpc('/verify/otp',{
                            	'Otpid':result,
                            });
                        } else {
                            $('button[type="submit"]').attr('disabled',false);
                            $('#bi_login_otpvalue').text("OTP will expire in " + $limit + " seconds.");
                        }
                        $limit -= 1;
                    }, 1000);
                }
            });

        },

        _OnResendButtonClick: function(ev){
            ev.preventDefault();
            var self = this;
            var $otp_type = $('input[name="otp_type"]').val();
            var $email = $('input[name="login"]').val();
            var $limit = $('input[name="otp_limit"]').val();
            $('.otp_resend').remove();
            self.VerifyOtp($otp_type, $limit, $email);
        },

    });

    publicWidget.registry.SignupForm = publicWidget.Widget.extend({
        selector: '.oe_signup_form',

        events: {
            'click .send_otp': '_OnSendButtonClick',
            'click .signup_otp_resend': '_OnSignupResendButtonClick',
        },

        start: function(){
            if($('.send_otp').length > 0){
                $('button[type="submit"]').attr('disabled',true);
            }
        },

        VerifySignupOtp: function($otp_type, $limit, $email){
            if($otp_type === 'text'){
                $('.form-group.field-otp input').attr('type','text');;
            }
            $('.form-group.field-otp').after('<p id="otp_msg" class="alert alert-success">OTP has been sent to given Email Address : '+ $email +'.</p>');
            var $name = $('input[name="name"]').val();
            jsonrpc('/send/otp', {
            	'login':$email,
                'name':$name,
            }).then(function(result){
                if(result){
                    var Timer = setInterval(function(){
                        if($limit < 0){                    
                            clearInterval(Timer);
                            $('#bi_signup_otpvalue').text('');
                            $('#otp_msg').remove();
                            $('.form-group.field-otp').after('<a class="btn btn-link float-right signup_otp_resend" href="#">Resend OTP</a>')
                            $('button[type="submit"]').attr('disabled',true);
                            jsonrpc('/verify/otp',{
                            	'Otpid':result
                            });
                        } else {
                            var $otp_val = $('input[name="otp"]').val();
                            if($otp_val){
                                $('button[type="submit"]').attr('disabled',false);
                            }
                            $('#bi_signup_otpvalue').text("OTP will expire in " + $limit + " seconds.");
                        }
                        $limit -= 1;
                    }, 1000);
                }
            })
        },

        _OnSendButtonClick: function(ev){
            ev.preventDefault();
            var self = this;
            var $email = $('input[name="login"]').val();
            var $limit = $('input[name="otp_limit"]').val();
            if(!$email){
                $('.form-group.field-confirm_password').after('<p id="email_msg" class="alert alert-danger">Please enter an email address.</p>');
            }
            else{
                $(ev.currentTarget).css('display','none');
                var $otp_type = $('input[name="otp_type"]').val();
                $('.form-group.field-otp').css('display','block');
                $('.form-group.field-otp input').attr('required',true);
                self.VerifySignupOtp($otp_type, $limit, $email);
            }
        },

        _OnSignupResendButtonClick: function(ev){
            ev.preventDefault();
            var self = this;
            var $otp_type = $('input[name="otp_type"]').val();
            var $email = $('input[name="login"]').val();
            var $limit = $('input[name="otp_limit"]').val();
            $('.signup_otp_resend').remove();
            self.VerifySignupOtp($otp_type, $limit, $email);
        },
    });

