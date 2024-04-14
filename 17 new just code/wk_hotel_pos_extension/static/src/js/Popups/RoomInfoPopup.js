/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
/**
 * Props:
 *  {
 *      info: {object of data}
 *  }
 */
export class RoomInfoPopup extends AbstractAwaitablePopup {
    static template = "wk_hotel_pos_expension.RoomInfoPopup";
    static defaultProps = { confirmKey: false };

    setup() {
        super.setup();
        this.pos = usePos();
        Object.assign(this, this.props.info);
    }
    //--------------------------------------------------------------------------
    // Handler
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onChangeSelection(ev) {
        const selected_option = $(ev.currentTarget).find(":selected");
        let booking_name = selected_option.data('booking_name');
        let booking_customer = selected_option.data('customer');
        $('#booking_name').val(booking_name);
        $('#booking_customer').val(booking_customer);

        console.log(this);

    }

    confirm_booking(ev) {
        const selected_option = $("#room_no_selection").find(":selected");
        let current_order = this.pos.get_order();
        let customer = this.pos.db.get_partner_by_id(parseInt(selected_option.data('customer_id')));
        current_order['booking_id'] = selected_option.data('booking_id');
        current_order.set_partner(customer);
        current_order.updatePricelistAndFiscalPosition(customer);
        this.confirm()
    }
}