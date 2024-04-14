function openMeasurementPopup(lineId) {
    $('#line_id').val(lineId);
    console.log(lineId,"cccccccccccccccc")
    $("#measurement_popup_" + lineId).modal('show');
}

function closeMeasurementPopup(lineId) {
    $('#line_id').val(lineId);
    $("#measurement_popup_" + lineId).modal('hide');
}

$(document).on('click', 'button[name="open_measurement_popup"]', function() {
    var lineId = $(this).data('line-id');
    console.log(lineId,"aaaaaaaaaaaaaaaa")
    openMeasurementPopup(lineId);
});

$(document).on('click', 'button[name="close_measurement_popup"]', function() {
    var lineId = $(this).data('line-id');
    closeMeasurementPopup(lineId);
});


