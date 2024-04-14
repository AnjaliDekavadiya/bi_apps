
/**@odoo-module */
const { Component, onMounted, useState } = owl;
import { registry } from "@web/core/registry";
const actionRegistry = registry.category("actions");
export class KitchenOrders extends Component {
    static props = { orders: [] };
    setup(){
        super.setup(...arguments);
        onMounted(()=>{
            this.start();
        })
    }
    start() {
    }

    render() {
        let result = `
        <div class="row">`;
        result += this.props.orders.map((order) => {
            return `<div class="col kitchen_order">
                <div class="title_wrapper">
                    <div class="row">
                        <div class="waiter col">
                            <div>${order.user_id}</div>
                            <div>${order.create_date}</div>
                        </div>
                        <div class="title col">
                            ${order.name} <span>(${order.table_id || ''})</span>
                        </div>
                        <div class="pos-reference col">
                            <div>Guests: ${order.customer_count}</div>
                            <div>${order.pos_reference || ''}</div>
                        </div>
                    </div>
                </div>
                <div class="content">
                    <table>
                        <thead>
                            <tr>
                                <td class="name-column">Name</td>
                                <td class="qty-column">Qty</td>
                                <td>State</td>
                                <td>Avg Time</td>
                                <td>Action</td>
                            </tr>
                        </thead>
                            <tbody>
                                ${this.renderLines(order)}
                            </tbody>
                    </table>
                </div>
                <div class="footer">
                </div>
            </div>`;
        });
        result += '</div>';
        result = result.replaceAll('</div>,<div class="col kitchen_order">', '</div><div class="col kitchen_order">');
        return (
            result
        )
    }

    renderLines(order) {
        let result = '';
        order.lines.map((line) => {
            result += `
                <tr> 
                    <td class="name-column">
                        <div>
                            <span title="Recipie" data-product="${line.product_id}" class="show_receipie"><i class="fa fa-cutlery"></i></span>
                            <span class="text">${line.full_product_name}</span>
                        </div>
                        <div data-note="${line.note}" data-customer-note="${line.customer_note}" data-product="${line.full_product_name}" class="line-note">
                            ${line.customer_note || line.note ? '<span class="badge badge-note"><i class="fa fa-eye"></i> See notes</span>' : ''}
                        </div>
                    </td>
                    <td class="qty-column">${line.qty}</td>
                    <td>
                        ${this.renderBadge(line)}
                    </td>
                    <td><span${line.avg_completion_time}</span></td>
                    <td data-id="${line.id}" >
                        ${this.renderLineActionButtons(line)}
                    </td>
                </tr>`;
        });
        return result;
    }

    renderLineActionButtons(line) {
        if (line.kitchen_state == 'done') {
            return '';
        }
        if (line.kitchen_state == 'in_progress') {
            return `
            <button data-id="${line.id}" data-type="end" class="end_order_line btn btn-success">Done <i class="fa fa-check-square-o"></i></button>
            `;
        }
        if (line.kitchen_state == 'pending') {
            return `
            <button data-id="${line.id}" data-type="start" class="start_order_line btn btn-info">Start <i class="fa fa-arrow-circle-right fa-lg"></i></button>
            `;
        }
    }

    renderBadge(line) {
        if (line.kitchen_state == 'done') {
            return ('<span class="badge badge-success">Done</span>');
        }
        if (line.kitchen_state == 'in_progress') {
            return ('<span class="badge badge-warning">In progress</span>');
        }
        if (line.kitchen_state == 'pending') {
            return ('<span class="badge badge-danger">Pending</span>');
        }
    }
}
KitchenOrders.template = "kitchen_orders";