odoo.define('dr_discount_otp_auth.CustomProductScreen', function (require) {
    "use strict";


    const Registries = require('point_of_sale.Registries');
    const  ProductScreen = require('point_of_sale.ProductScreen')
    const rpc = require("web.rpc");


    const { onMounted, useState } = owl;
    const CustomProductScreen = (ProductScreen)=>{
        return class extends ProductScreen{
            setup() {
                super.setup();
            }
            async _onClickPay() {
                debugger;
                // NOTE::- All calculation done without tax.
                let totalDiscountValue = 0;
                let totalDiscountPercentage = 0;
                const pos = this.env.pos;
                const order = pos.get_order();
                const config = pos.config;
                const cashier =  pos.get_cashier();
                const currency = pos.currency;

                //(-1) => no discount || 0 => discount with any percentage || EX:- 12% discount value
                const otpTotalDiscountPercentage = config.otp_total_discount;
                const otpContactId = config.otp_contact_id;
                const env = this.env;


                // check if there are global discount product.
                const discountProduct = pos.db.get_product_by_id(config.discount_product_id[0]);
                if(discountProduct){
                    const expectedDiscountOrderLine = order.orderlines.find(order => order.product.id === discountProduct.id)
                    // check if there are global discount in order line
                    if(expectedDiscountOrderLine){
                        // add global discount value
                        totalDiscountValue += Math.abs(expectedDiscountOrderLine.export_for_printing().price_without_tax)
                    }
                }



                if(otpTotalDiscountPercentage !== 0){
                    debugger;
                    totalDiscountValue += order.export_for_printing().total_discount;
                    const totalOrderWithDiscountWithoutTax =  order.export_for_printing().total_without_tax;
                    const totalOrderWithoutDiscountWithoutTax = totalOrderWithDiscountWithoutTax + totalDiscountValue;
                    totalDiscountPercentage = ((totalDiscountValue) * 100) / totalOrderWithoutDiscountWithoutTax;

                    if(otpTotalDiscountPercentage < 0 && totalDiscountPercentage > 0){
                        await this.showPopup('ErrorPopup', {
                            title : this.env._t("Discount not allow"),
                            body  : this.env._t("Please Call admin to active discount or remove discount from order."),
                        });
                        return;
                    }else if(otpTotalDiscountPercentage >= 0 && totalDiscountPercentage >= otpTotalDiscountPercentage){

                        //TODO::- Error Handling for meta template
                        //1- check if template already exist.
                        // const response = await this.checkTemplateExists();

                        //2- check if user select discount template or not
                        const whatsappTemplateId = config.otp_whatsapp_template_id;
                        if(!whatsappTemplateId){
                            await this.showPopup('ErrorPopup', {
                                title : this.env._t("There is problem in template"),
                                body  : this.env._t("Please select template from configuration or create it like documentation."),
                            });
                            return;
                        }

                        //3- check if template approved or not [boolean]
                        // const templateApproved = await  this.checkTemplateApproved(whatsappTemplateId);
                        // if(!templateApproved){
                        //     await this.showPopup('ErrorPopup', {
                        //         title : this.env._t("There is problem in template"),
                        //         body  : this.env._t("template not approved yet!"),
                        //     });
                        //     return
                        // }

                        //TODO::- check if there are user or not
                        const [adminUser, ...rest] = await rpc.query({
                            model: "res.users",
                            method: "search_read",
                            fields: ["name", "phone"],
                            args:[[["id", "=", otpContactId]]],
                        })

                        if(!adminUser){
                            await this.showPopup('ErrorPopup', {
                                title : this.env._t("There is problem in settings"),
                                body  : this.env._t("Please Check if you already selected admin in pos-discount-otp module"),
                            });
                            return
                        }

                        const otpData = {
                            contact: adminUser,
                            cashierName: cashier.name,
                            orderId: order.uid,
                            totalDiscountPercentage: totalDiscountPercentage.toPrecision(2),
                            totalDiscountValue: totalDiscountValue.toPrecision(2),
                            currencyName: currency.name
                        }

                        const otpMessage = `Hi,${otpData.contact.name} There is a POS order created by ${cashier.name} with order number  ${order.uid}that needs permission.  The discount percentage ${totalDiscountPercentage.toFixed(2)}% with value ${totalDiscountValue.toFixed(2)} ${currency.name}`;

                        const {confirmed, payload} = await this.showPopup("SendOtpDialogPopup", {
                            message: otpMessage,
                            otpData
                        });

                        if(!confirmed){
                            return
                        }
                    }
                }

                if (this.env.pos.get_order().orderlines.some(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot()) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Some Serial/Lot Numbers are missing'),
                        body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                        confirmText: this.env._t('Yes'),
                        cancelText: this.env._t('No')
                    });
                    if (confirmed) {
                        this.showScreen('PaymentScreen');
                    }
                } else {
                    this.showScreen('PaymentScreen');
                }
            }

            //TODO::- check if template already exists or not [boolean]
            async checkTemplateExists(){

                const [template, ...other] = await rpc.query({
                    model: "whatsapp.template",
                    method: "search_read",
                    fields: ["status"],
                    args: [[["name", "=", "admin_discount_approval"],["language", "=", "en_US"]]]
                })
                if(!template){
                    const newTemplateObject = {
                        name: "admin_discount_approval",
                        body: "Hi, {{1}}. There is a POS order created by {{2}} with order number {{3}} that needs permission.  The discount percentage {{4}}% with value {{5}} {{6}}.",
                        language: "en_US",
                        buttons: [[0, 0, { "text": "Accept Discount", "payload_type": "QUICK_REPLY" }], [0, 1, { "text": "Reject Discount", "payload_type": "QUICK_REPLY" }]]
                    }
                    // create template
                    try{
                        const [template, ...other] = await rpc.query({
                            model: "whatsapp.template",
                            method: "create",
                            args: [newTemplateObject]
                        })
                        console.log("Template Created: ", template)
                    }catch (error){
                        console.log("Error While Creating whatsapp template", error)
                    }

                }
            }

            //TODO::- check if template approved or not [boolean]
            async checkTemplateApproved(templateID){
                try{
                    const [template, ...other] = await rpc.query({
                        model: "whatsapp.template",
                        method: "search_read",
                        fields: ["status"],
                        args: [[["id", "=", templateID]]]
                    })

                    if(!template){
                        return false;
                    }
                    return template.status === "APPROVED";
                }catch(error){
                    console.log("Can't founded template with this id", templateID)
                    return false
                }


            }


        }
    }

    Registries.Component.extend(ProductScreen, CustomProductScreen);
});