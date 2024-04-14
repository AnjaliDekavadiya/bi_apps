odoo.define('helpdesk_ticket_knowledge_base.website_forum', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $('textarea#content').each(function () {
        var $textarea = $(this);
        var editor_karma = $textarea.data('karma') || 30;  // default value for backward compatibility
        if (!$textarea.val().match(/\S/)) {
            $textarea.val("<p><br/></p>");
        }
        var $form = $textarea.closest('form');
        var toolbar = [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['history', ['undo', 'redo']],
            ];
        toolbar.push(['insert', ['link', 'picture']]);
        $textarea.summernote({
                height: 150,
                toolbar: toolbar,
                styleWithSpan: false
            });

        // pull-left class messes up the post layout OPW 769721
        $form.find('.note-editable').find('img.pull-left').removeClass('pull-left');
        $form.on('click', 'button, .a-submit', function () {
            $textarea.html($form.find('.note-editable').code());
        });
    });

});
