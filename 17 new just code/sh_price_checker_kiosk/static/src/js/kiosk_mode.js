/** @odoo-module **/

import { BarcodeScanner } from "@barcodes/components/barcode_scanner";
import { Component, onWillStart } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";

export class PriceCheckerKioskMode extends Component {
    setup() {
        this.actionService = useService("action");
        this.companyService = useService("company");
        this.notification = useService("notification");
        this.rpc = useService("rpc");
        this.orm = useService("orm");

        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", (ev) => this.onBarcodeScanned(ev.detail.barcode));

        this.lockScanner = false;

        onWillStart(this.onWillStart);
        // Make a RPC call every day to keep the session alive
        browser.setInterval(() => this.callServer(), 60 * 60 * 1000 * 24);
    }

    async onWillStart() {
        const companyId = this.companyService.currentCompany.id;
        const currentCompany = (
            await this.orm.searchRead(
                "res.company",
                [["id", "=", companyId]],
                [
                    "name",
                    "sh_product_code",
                    "sh_product_barcode",
                    "sh_product_pricelist",
                    "sh_product_weight",
                    "sh_product_sale_description",
                    "sh_product_sale_price",
                    "sh_touch_kyboard",
                    "sh_product_stock",
                    "sh_product_attribute",
                    "sh_product_image",
                    "sh_product_category",
                    "sh_welcome_message",
                    "sh_message",
                    "sh_company_logo",
                    "sh_display",
                    "sh_display_view",
                    "sh_display_landscape",
                    "sh_display_portrait",
                    "sh_delay_screen",
                    "sh_warehouse_ids",
                ]
            )
        )[0];
        this.company_name = currentCompany.name;
        this.company_image_url = url("/web/image", {
            model: "res.company",
            id: companyId,
            field: "logo",
        });
        this.sh_product_code = currentCompany.sh_product_code;
        this.sh_product_barcode = currentCompany.sh_product_barcode;
        this.sh_product_weight = currentCompany.sh_product_weight;
        this.sh_product_pricelist = currentCompany.sh_product_pricelist;
        this.sh_product_sale_description = currentCompany.sh_product_sale_description;
        this.sh_product_sale_price = currentCompany.sh_product_sale_price;
        this.sh_touch_kyboard = currentCompany.sh_touch_kyboard;
        this.sh_product_stock = currentCompany.sh_product_stock;
        this.sh_product_attribute = currentCompany.sh_product_attribute;
        this.sh_product_image = currentCompany.sh_product_image;
        this.sh_product_category = currentCompany.sh_product_category;
        this.sh_welcome_message = currentCompany.sh_welcome_message;
        this.sh_message = currentCompany.sh_message;
        this.sh_company_logo = currentCompany.sh_company_logo;
        this.sh_display = currentCompany.sh_display;
        this.sh_display_view = currentCompany.sh_display_view;
        this.sh_display_landscape = currentCompany.sh_display_landscape;
        this.sh_display_portrait = currentCompany.sh_display_portrait;
        this.sh_delay_screen = currentCompany.sh_delay_screen;
        this.sh_warehouse_ids = currentCompany.sh_warehouse_ids;
    }
    async onClickGo() {
        var barcode = $("#code").val();
        const result = await this.orm.call("product.product", "all_scan_search", [barcode]);
        if (result.issuccess == 1) {
            /* success msg */
            if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                $("#screen_div").removeClass("col-12");
                $("#screen_div").addClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                $("#specification_div").removeClass("o_hidden");
            }
            $("#main_div").removeClass("o_hidden");
            $("#sh_product_name").html(result.sh_product_name);
            $("#sh_product_code").html(result.sh_product_code);
            $("#sh_product_weight").html(result.sh_product_weight);
            $("#sh_product_image").html("");
            $("#sh_product_image").append('<div class="sh_image_box"><img class="img img-responsive sh_product_image" src="data:image/jpeg;base64,' + result.sh_product_image + '" alt="Product Image" /></div>');
            $("#sh_product_barcode").html(result.sh_product_barcode);
            $("#sh_product_weight").html(result.sh_product_weight);
            $("#sh_product_pricelist").html(result.sh_product_pricelist);
            $("#sh_product_sale_price").html(result.sh_product_sale_price);
            if(result.warehouse_wise_stock == true){
                var count = 1;
                result.sh_product_stock.forEach((object) => {
                    for (let key in object) {
                        var obj = object[key];
                        var warehouse_id = "#sh_product_warehouse_name_" + count;
                        var stock_id = "#sh_product_stock_" + count;
                        $(warehouse_id).html(key);
                        $(stock_id).html(obj);
                        count = count + 1;
                    }
                });
            }
            else{
                $("#product_stock").html(result.sh_product_stock);
            }
            $("#sh_product_category").html(result.sh_product_category);
            if (result.sh_product_attribute == "") {
                $("#attribute_tr").addClass("o_hidden");
            } else if (result.sh_product_attribute != "") {
                $("#attribute_tr").removeClass("o_hidden");
                $("#sh_product_attribute").html(result.sh_product_attribute);
            }
            if (result.sh_product_sale_description == "") {
                $("#sale_description_tr").addClass("o_hidden");
            } else if (result.sh_product_sale_description != "") {
                $("#sale_description_tr").removeClass("o_hidden");
                $("#sh_product_sale_description").html(result.sh_product_sale_description);
            }
            $("#success").css("display", "block");
            $("#success").html(result.msg);
            $("#fail").css("display", "none");
            $("#code").val("");
            if (this.myvar) {
                clearTimeout(self.myvar);
            }
            var delay = $("#screen_delay").val() * 1000;
            this.myvar = setTimeout(function () {
                if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                    $("#screen_div").addClass("col-12");
                    $("#screen_div").removeClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                }
                $("#main_div").addClass("o_hidden");
                $("#success").css("display", "none");
            }, delay);
        } else {
            if (!barcode) {
                alert("Please enter any barcode number");
            } else {
                if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                    $("#screen_div").addClass("col-12");
                    $("#screen_div").removeClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                }
                $("#main_div").addClass("o_hidden");
                $("#success").css("display", "none");
                $("#fail").css("display", "block");
                $("#fail").html(result.msg);
                $("#code").val("");
            }
            /* Fail msg */
        }
        var barcode = $("#mono").val("");
    }
    async onBarcodeScanned(barcode) {
        if (this.lockScanner) {
            return;
        }
        this.lockScanner = true;
        const result = await this.orm.call("product.product", "all_scan_search", [barcode]);
        if (result.issuccess == 1) {
            /* success msg */
            if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                $("#screen_div").removeClass("col-12");
                $("#screen_div").addClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                $("#specification_div").removeClass("o_hidden");
            }
            $("#main_div").removeClass("o_hidden");
            $("#sh_product_name").html(result.sh_product_name);
            $("#sh_product_code").html(result.sh_product_code);
            $("#sh_product_weight").html(result.sh_product_weight);
            $("#sh_product_image").html("");
            $("#sh_product_image").append('<div class="sh_image_box"><img class="img img-responsive" width="auto !important;" style="max-height:100%;max-width:100%;" src="data:image/jpeg;base64,' + result.sh_product_image + '" alt="Product Image" /></div>');
            $("#sh_product_barcode").html(result.sh_product_barcode);
            $("#sh_product_weight").html(result.sh_product_weight);
            $("#sh_product_pricelist").html(result.sh_product_pricelist);
            $("#sh_product_sale_price").html(result.sh_product_sale_price);
            if(result.warehouse_wise_stock == true){
                var count = 1;
                result.sh_product_stock.forEach((object) => {
                    for (let key in object) {
                        var obj = object[key];
                        var warehouse_id = "#sh_product_warehouse_name_" + count;
                        var stock_id = "#sh_product_stock_" + count;
                        $(warehouse_id).html(key);
                        $(stock_id).html(obj);
                        count = count + 1;
                    }
                });
            }
            else{
                $("#product_stock").html(result.sh_product_stock);
            }
            $("#sh_product_category").html(result.sh_product_category);
            if (result.sh_product_attribute == "") {
                $("#attribute_tr").addClass("o_hidden");
            } else if (result.sh_product_attribute != "") {
                $("#attribute_tr").removeClass("o_hidden");
                $("#sh_product_attribute").html(result.sh_product_attribute);
            }
            if (result.sh_product_sale_description == "") {
                $("#sale_description_tr").addClass("o_hidden");
            } else if (result.sh_product_sale_description != "") {
                $("#sale_description_tr").removeClass("o_hidden");
                $("#sh_product_sale_description").html(result.sh_product_sale_description);
            }
            $("#success").css("display", "block");
            $("#success").html(result.msg);
            $("#fail").css("display", "none");
            $("#code").val("");
            if (this.myvar) {
                clearTimeout(self.myvar);
            }
            var delay = $("#screen_delay").val() * 1000;
            this.myvar = setTimeout(function () {
                if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                    $("#screen_div").addClass("col-12");
                    $("#screen_div").removeClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                }
                $("#main_div").addClass("o_hidden");
                $("#success").css("display", "none");
            }, delay);
        } else {
            if (!barcode) {
                alert("Please enter any barcode number");
            } else {
                if ($("#display_landscape").val() == "left" || $("#display_landscape").val() == "right") {
                    $("#screen_div").addClass("col-12");
                    $("#screen_div").removeClass("col-xxl-7 col-xl-7 col-lg-7 col-md-12 col-sm-12 col-xs-12");
                }
                $("#main_div").addClass("o_hidden");
                $("#success").css("display", "none");
                $("#fail").css("display", "block");
                $("#fail").html(result.msg);
                $("#code").val("");
            }
            /* Fail msg */
        }
    }
}

class PriceCheckerKioskModeBarcodeScanner extends BarcodeScanner {
    get facingMode() {
        if (this.props.barcodeSource == "front") {
            return "user";
        }
        return super.facingMode;
    }
}
PriceCheckerKioskModeBarcodeScanner.props = {
    ...BarcodeScanner.props,
    barcodeSource: String,
};
PriceCheckerKioskMode.template = "MrpKioskKioskMode";
PriceCheckerKioskMode.components = { BarcodeScanner: PriceCheckerKioskModeBarcodeScanner };

registry.category("actions").add("checker_kiosk_kiosk_mode", PriceCheckerKioskMode);
