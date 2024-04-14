odoo.define('dr_discount_otp_auth.SendOtpDialogPopup', function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');
    const ajax = require("web.ajax");
    const rpc = require("web.rpc");


    const { useRef, useState } = owl;
    class SendOtpDialogPopup extends AbstractAwaitablePopup{
        setup(){
            super.setup()
            this.state = useState({
                body: this.props.message,
                acceptation: false
            })
        }

        async confirm(){


            this.state.body = "we sent discount request from admin and wait until accept, screen automatically will dismiss if admin accept."
            const {
                contact, //admin
                cashierName,
                orderId,
                totalDiscountPercentage,
                totalDiscountValue,
                currencyName
            } = this.props.otpData;

            if (!contact || !contact.phone){
                await this.showPopup('ErrorPopup', {
                    title : this.env._t("Can't Send otp"),
                    body  : this.env._t("User not exist or not have phone number."),
                });
                return;
            }

            const otpBody = `${contact.name},${cashierName},${orderId},${totalDiscountPercentage},${totalDiscountValue},${currencyName}`

            const {wamid} = await ajax.jsonRpc(
                "/send_discount_otp_message",
                "call",
                {otpBody}
            );

            if(!wamid || wamid.length < 1){
                await this.showPopup('ErrorPopup', {
                    title : this.env._t("There is Problem in Template"),
                    body  : this.env._t("Please check template format or check phone number and is register with whatsapp."),
                });
                super.cancel();
            }

            let otpCounter = 0;
            const otpCheckApproveInterval = setInterval(async ()=>{
                otpCounter += 10;
                const [otpResponse, ...other] = await rpc.query({
                    model: "whatsapp.wamid",
                    method: "search_read",
                    fields: ["response"],
                    args: [[["wamid", "=", wamid]]]
                })
                if(otpResponse){
                    if(otpResponse.response === "approve"){
                        super.confirm()
                        clearInterval(otpCheckApproveInterval);
                    }else if(otpResponse.response === "reject"){
                        super.cancel();
                        clearInterval(otpCheckApproveInterval);
                    }
                }

                // 300 equal => 5 min
                if(otpCounter === 300){
                    super.cancel();
                    clearInterval(otpCheckApproveInterval);
                }
            }, 10000)

        }

        cancel(){
            super.cancel();
        }

        getPayload(){
            return {
                acceptationStatus: this.state.acceptation
            }
        }

        //TODO::- check if "whatsapp_connector" already exists or not
        checkModuleExist(moduleName){

        }





    }

    SendOtpDialogPopup.template = "dr_discount_otp_auth.SendOtpDialogPopup";
    SendOtpDialogPopup.defaultProps = {
        confirmText: _t('Send'),
        cancelText: _t('Cancel'),
        title: _t('Discount OTP Request'),
        body: _t("")
    };
    Registries.Component.add(SendOtpDialogPopup)
    return SendOtpDialogPopup;

});