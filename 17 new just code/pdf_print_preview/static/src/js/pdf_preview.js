/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import PreviewDialog from "@pdf_print_preview/js/preview_dialog";



/**
 * Generates the report url given a report action.
 *
 * @private
 * @param {ReportAction} action
 * @param {env} env
 * @returns {string}
 */
function _getReportUrl(action, env, filename) {
    let url = `/report/pdf/${action.report_name}`;
    const actionContext = action.context || {};
    filename = filename || action.name;
     if(filename !== undefined)
        filename = filename.replace(/[/?%#&=]/g, "_") + ".pdf";
    if (action.data && JSON.stringify(action.data) !== "{}") {
        const options = encodeURIComponent(JSON.stringify(action.data));
        const context = encodeURIComponent(JSON.stringify(actionContext));
        url += `?filename=${filename}&options=${options}&context=${context}&`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}?filename=${filename}&context=${encodeURIComponent(JSON.stringify(env.services.user.context))}&`;
        }
    }

    return url;
}

async function PdfPrintPreview(action, options, env) {
    const link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';
    const WKHTMLTOPDF_MESSAGES = {
        broken:
            _t(
                "Your installation of Wkhtmltopdf seems to be broken. The report will be shown " +
                    "in html."
            ) + link,
        install:
            _t(
                "Unable to find Wkhtmltopdf on this system. The report will be shown in " + "html."
            ) + link,
        upgrade:
            _t(
                "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to " +
                    "get a correct display of headers and footers as well as support for " +
                    "table-breaking between pages."
            ) + link,
        workers: _t(
            "You need to start Odoo with at least two workers to print a pdf version of " +
                "the reports."
        ),
    };

    if (action.report_type === "qweb-pdf" && env.services.menu.getCurrentApp() !== undefined && (session.preview_print || session.automatic_printing)) {
        let getReportResult = env.services.rpc("pdf_print_preview/get_report_name", {
            report_name: action.report_name,
            data: JSON.stringify(action.context)
        });
        const result = await getReportResult;
        const state = result["wkhtmltopdf_state"];

        // display a notification according to wkhtmltopdf's state
        if (state in WKHTMLTOPDF_MESSAGES) {
            env.services.notification.add(WKHTMLTOPDF_MESSAGES[state], {
                sticky: true,
                title: _t("Report"),
            });
        }

        if (state === "upgrade" || state === "ok") {
            let url = _getReportUrl(action, env, result["file_name"]);
            if(session.preview_print) {
                PreviewDialog.createPreviewDialog(self, url,  action.name);
            }
            if (session.automatic_printing) {
                try {
                    var pdf = window.open(url);
                    pdf.print();
                }
                catch(err) {
                    env.services.notification.add(
                        _t("Please allow pop up in your browser to preview report in another tab."),
                        {
                        sticky: true,
                        title: _t("Report"),
                    });
                }
            }
            return true;
        }
    }
}

registry
    .category("ir.actions.report handlers")
    .add("pdf_print_preview", PdfPrintPreview);
