/* @odoo-module */
	if ($('.o_note_details').length) {
        var state_options = $("select[name='task']:enabled option:not(:first)");
        $('.o_note_details').on('change', "select[name='project']", function () {
            var select = $("select[name='task']");
            state_options.detach();
            var displayed_state = state_options.filter("[data-project="+($(this).val() || 0)+"]");
            var nb = displayed_state.appendTo(select).show();
            select.parent().toggle(nb.length>=1);
        });
        $('.o_note_details').find("select[name='project']").change();
    }

    $(document).ready(function () {
        $('select.advanced-select').select2();
    });
