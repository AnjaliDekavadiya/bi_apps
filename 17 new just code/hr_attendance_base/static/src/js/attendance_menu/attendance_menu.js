/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { systrayAttendance } from "@hr_attendance/components/attendance_menu/attendance_menu";
import {
  HrAttendanceInfo,
  HrAttendanceRound,
} from "@hr_attendance_base/js/shared/shared";

// добавляются расшаренные компоненты необходимые для красивого отображения
systrayAttendance.Component.components = {
  ...systrayAttendance.Component.components,
  HrAttendanceInfo,
  HrAttendanceRound,
};

patch(systrayAttendance.Component.prototype, {
  checkAccess() {
    if (
      this.employee.geolocation_enable &&
      !Object.keys(this.resultGeolocation).length
    )
      return "geolocation";
    if (this.employee.geospatial_enable && !this.resultGeospatialId)
      return "geospatial";

    return false;
  },
  async signInOut() {
    // добавляет при входе или выходе контекст
    // в контексте могут быть различные данные от модулей
    // например фото от модуля по распознования, для сохранения
    // или геокоординаты или геозоны
    const context = this.context;
    const isAccessDenied = this.checkAccess();
    if (isAccessDenied) {
      alert(`You are not have access by ${isAccessDenied}`);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async ({ coords: { latitude, longitude } }) => {
        await this.rpc("/hr_attendance/systray_check_in_out", {
          latitude,
          longitude,
          context,
        });
        await this.searchReadEmployee();
      },
      async (err) => {
        await this.rpc("/hr_attendance/systray_check_in_out", { context });
        await this.searchReadEmployee();
      },
    );
  },
});
