/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import Class from "@web/legacy/js/core/class";
import Widget from "@web/legacy/js/core/widget";
import { renderToElement } from "@web/core/utils/render";
import { uniqueId } from "@web/core/utils/functions";


var pdfPreview = Class.extend({

    preview: function( url ) {
        var result = new $.Deferred();
        var urlTempalte = "/pdf_print_preview/static/lib/pdfjs/web/viewer.html?file=" + url;
        result.resolve($(renderToElement("PDFjsFrame", {url: urlTempalte})));
        return $.when(result);
    }
});

var PreviewDialog = Widget.extend({
	init: function(parent, pdfPreview, url, title) {
		this._super(parent);
        this._opened = $.Deferred();
        this.title = title || _t("Preview");
        this.url = url;
		this.$modal = $(renderToElement("PreviewDialog", {title: this.title, url: this.url, uniqueId: uniqueId("modal_")}));
        this.$modal.on("hidden.bs.modal", this.destroy.bind(this));

        this.$modal.find(".preview-maximize").on("click", this.maximize.bind(this));
        this.$modal.find(".preview-minimize").on("click", this.minimize.bind(this));
        this.$modal.find(".preview-minimize").toggle();

		this.pdfPreview = pdfPreview;
	},
    renderElement: function() {
        this._super();
        var self = this;
        var def = new $.Deferred();
        this.pdfPreview.preview(this.url).then(function($content) {
            def.resolve(self.$modal.find(".modal-body").append($content));
        });

        return $.when(def);
	},
    open: function() {
        var self = this;
        $(".tooltip").remove();
        this.renderElement().then(function(){
            self.$modal.modal("show");
            self._opened.resolve();
        });
        return self;
    },
    maximize: function(e) {
        this.$modal.find(".preview-minimize").toggle();
        this.$modal.find(".preview-maximize").toggle();
        this.$modal.find(".modal-dialog").addClass("modal-full");

    },
    minimize: function(e) {
    	this.$modal.find(".preview-maximize").toggle();
        this.$modal.find(".preview-minimize").toggle();
        this.$modal.find(".modal-dialog").removeClass("modal-full");
    },
    close: function() {
        this.$modal.modal("hide");
    },
    destroy: function(reason) {
        $(".tooltip").remove();
        if(this.isDestroyed()) {
            return;
        }
        this.trigger("closed", reason);
        this._super();
        this.$modal.modal("hide");
        this.$modal.remove();
        setTimeout(function () {
            var modals = $("body > .modal").filter(":visible");
            if(modals.length) {
                modals.last().focus();
                $("body").addClass("modal-open");
            }
        }, 0);
    }
});

PreviewDialog.createPreviewDialog = function (parent, url, title) {
    return new PreviewDialog(parent, new pdfPreview(), url, title).open();
};

export default PreviewDialog;
