/** @odoo-module **/
import { Component, xml } from "@odoo/owl";

class HrAttendanceRound extends Component {}
HrAttendanceRound.template = xml`
<div class="d-flex flex-row" style="justify-content:space-between; align-items: center;">
<span class="round-status" t-att-style="'color: ' + this.props.color">
    <i class="fa fa-check" t-att-style="'color: ' + this.props.color"></i>
</span>
<h3 t-att-style="'color: ' + this.props.color">
<t t-esc="this.props.title"/>
</h3>
<h3 t-att-style="'cursor:pointer;color: ' + this.props.color">
    <i t-att-class="this.props.toogle ?'round-arrow fa fa-angle-double-up arrow-size':'round-arrow fa fa-angle-double-down arrow-size'" t-on-click="this.props.onClickToogle"></i>
</h3>
</div>`;

class HrAttendanceInfo extends Component {}
HrAttendanceInfo.template = xml`
<div t-if="this.props.toogle">
    <div class="d-flex flex-column" style="align-items: center" t-if="this.props.color == 'green'">
        <h5>Info:</h5>
        <span>
            <t t-esc="this.props.info"/>
        </span>
    </div>
    <div class="d-flex flex-column" style="align-items: center" t-else="">
        <h5>Error:</h5>
        <span>
            <t t-esc="this.props.error"/>
        </span>
    </div>
</div>`;

export { HrAttendanceInfo, HrAttendanceRound };
