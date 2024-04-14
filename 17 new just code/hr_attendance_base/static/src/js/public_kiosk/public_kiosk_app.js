/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import App from "@hr_attendance/public_kiosk/public_kiosk_app";
import { KioskKonfirm } from "@hr_attendance_base/js/kiosk_confirm/kiosk_confirm";

// в компонент киоска добавлен компонент подтверждения
App.kioskAttendanceApp.components = {
  ...App.kioskAttendanceApp.components,
  KioskKonfirm,
};

// добавлен скрин подтверждения
patch(App.kioskAttendanceApp.prototype, {
  switchDisplay(screen) {
    if (screen === "kiosk_confirm") {
      this.state.active_display = screen;
      return;
    }
    super.switchDisplay(screen);
  },
});
