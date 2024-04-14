/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { deserializeDateTime } from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
const { DateTime } = luxon;
import {
  HrAttendanceInfo,
  HrAttendanceRound,
} from "@hr_attendance_base/js/shared/shared";

export class KioskKonfirm extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.employee = this.props.employeeData;
    this.context = this.props.context;
    this.state = useState({
      checkedIn: false,
      isDisplayed: false,
    });
    this.date_formatter = registry.category("formatters").get("float_time");
    this.onClickSignInOut = useDebounced(this.onManualSelection, 200, true);
    // load data but do not wait for it to render to prevent from delaying
    // the whole webclient
    this.searchReadEmployee();
  }

  checkAccess() {
    if (
      this.employee.kiosk_geolocation_enable &&
      !Object.keys(this.resultGeolocation).length
    )
      return "geolocation";
    if (this.employee.kiosk_geospatial_enable && !this.resultGeospatialId)
      return "geospatial";

    return false;
  }

  async searchReadEmployee() {
    console.log(this.employee);
    // просто парсинг данных по сотруднику для отображения в компоненте
    if (this.employee.id) {
      this.hoursToday = this.date_formatter(this.employee.hours_today);
      this.hoursPreviouslyToday = this.date_formatter(
        this.employee.hours_previously_today,
      );
      this.lastAttendanceWorkedHours = this.date_formatter(
        this.employee.last_attendance_worked_hours,
      );
      this.lastCheckIn = deserializeDateTime(
        this.employee.last_check_in,
      ).toLocaleString(DateTime.TIME_SIMPLE);
      this.state.checkedIn = this.employee.attendance_state === "checked_in";
      this.isFirstAttendance = this.employee.hours_previously_today === 0;
      this.state.isDisplayed = this.employee.display_systray;
    }
  }

  onClickBack() {
    location.reload();
    // if (this.props.kioskMode !== 'manual'){
    //     this.switchDisplay('main')
    // }else{
    //     this.switchDisplay('manual')
    // }
  }

  async onManualSelection(enteredPin = false) {
    let result;
    const isAccessDenied = this.checkAccess();
    if (isAccessDenied) {
      alert(`You are not have access by ${isAccessDenied}`);
      return;
    }

    // TODO: work with pin too
    if (true) {
      result = await this.rpc("manual_selection", {
        token: this.props.token,
        employee_id: this.employee.id,
        pin_code: enteredPin,
        context: this.context,
      });
    } else {
      result = await this.rpc("manual_selection", {
        token: this.props.token,
        employee_id: this.employee.id,
        pin_code: enteredPin,
      });
    }

    if (result && result.attendance) {
      this.props.kioskReturn(result, "greet");
    } else {
      if (enteredPin) {
        this.displayNotification(_t("Wrong Pin"));
      }
    }
  }
}

// добавляются расшаренные компоненты необходимые для красивого отображения
KioskKonfirm.components = {
  ...KioskKonfirm.components,
  HrAttendanceInfo,
  HrAttendanceRound,
};

KioskKonfirm.template = "hr_attendance_base.kiosk_confirm";
KioskKonfirm.props = {
  employeeData: { type: Object },
  token: { type: String },
  kioskReturn: { type: Function },
};
