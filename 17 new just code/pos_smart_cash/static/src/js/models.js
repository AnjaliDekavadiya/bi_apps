/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentTerminal } from '@pos_smart_cash/js/payment';

    register_payment_method('smart_cash', PaymentTerminal);
