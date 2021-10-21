$(document).on('click', '#resend_button', function() {
    $.ajax({
        type: 'GET',
        url: 'https://therise.online/resend_verification',
        success: function (data) {
            $('.body').html(data);
        },
        error: function(data) {
        }
    });
    return false;
});