odoo.define('helpdesk_ticket_knowledge_base.ticket_html_textarea', function (require) {
    'use strict';

    require('web.dom_ready');
    var weDefaultOptions = require('web_editor.wysiwyg.default_options');

    var publicWidget = require('web.public.widget');
    var wysiwygLoader = require('web_editor.loader');

publicWidget.registry.TicketKnowledgeBase = publicWidget.Widget.extend({
    selector: '.div_knowledge_base_helpdesk',
    events: {},
    start: function () {
        var self = this;

        _.each($('textarea.o_wysiwyg_loader_helpdesk'), function (textarea) {
            var $textarea = $(textarea);
            var editorKarma = $textarea.data('karma') || 0; // default value for backward compatibility
            var $form = $textarea.closest('form');
            var hasFullEdit = parseInt($("#karma").val()) >= editorKarma;
            var toolbar = [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
            ];
            if (hasFullEdit) {
                toolbar.push(['insert', ['linkPlugin', 'mediaPlugin']]);
            }
            toolbar.push(['history', ['undo', 'redo']]);

            var options = {
                height: 200,
                minHeight: 80,
                toolbar: toolbar,
                styleWithSpan: false,
                styleTags: _.without(weDefaultOptions.styleTags, 'h1', 'h2', 'h3'),
//                recordInfo: {
//                    context: _getContext(),
//                    res_model: 'helpdesk.support',
//                    res_id: +window.location.pathname.split('-').pop(),
//                },
            };
            if (!hasFullEdit) {
                options.plugins = {
                    LinkPlugin: false,
                    MediaPlugin: false,
                };
            }
            wysiwygLoader.load(self, $textarea[0], options).then(wysiwyg => {
                // float-left class messes up the post layout OPW 769721
                $form.find('.note-editable').find('img.float-left').removeClass('float-left');
                $form.on('click', 'button .a-submit', () => {
                    wysiwyg.save();
                });
            });
        });
        return this._super.apply(this, arguments);
    }
    });

});
