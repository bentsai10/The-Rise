$(document).ready(function(){
    
    $('#discussion_title').on("input", function(){
        $('#discussion_title_input').val($('#discussion_title').val()); 
    });
    $('.discussion_type_radio_button').click(function(){
        $('.discussion_type_radio_button').removeClass("selected");
        $('.person_button').attr('src', "https://humanely-test-bucket-1.s3.amazonaws.com/static/img/filled_person.svg?AWSAccessKeyId=AKIAUEMTDJETX2E2IUBE&Signature=5Gr6QWNAs1TwIUBxKTGNxjmNdNo%3D&Expires=1628075595");
        $(this).addClass("selected");
        let id = "#filled_person_" + $(this).attr('data-option');
        $(id).attr('src', "https://humanely-test-bucket-1.s3.amazonaws.com/static/img/filled_person_white.svg?AWSAccessKeyId=AKIAUEMTDJETX2E2IUBE&Signature=p7M7SM8j2hLsBM6AT6vW0g2exd4%3D&Expires=1628075595")
        $('#discussion_participant_cap_input').attr('value', $(this).attr('data-option'));
    });
})


