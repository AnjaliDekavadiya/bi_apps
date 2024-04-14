/** @odoo-module **/

import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";


patch(
  Message.prototype,
//  "ks_office365_mails/static/src/js/message/ks_message.js",
  {
    willStart() {
      this._super(...arguments);
      const id = this.messageView.message.id;
      const l10n = _t.database.parameters;

      this.messageView.message.datetime_format = time.strftime_to_moment_format(
        _t.database.parameters.date_format + " " + l10n.time_format
      );
      const self = this;

      this.rpc({
        model: "mail.message",
        method: "ks_get_fields_data",
        args: [[id], [id]],
      }).then(function (data) {
        if (data) {
          self.messageView.message._ks_partner_ids = data.ks_partner_ids;

          self.messageView.message._ks_cc = data.ks_cc;
          self.messageView.message._ks_bcc = data.ks_bcc;
          self.messageView.message._ks_send_to = data.ks_send_to;
          self.state.isdataReceived = true;
        }
      });
    },
  }
);
