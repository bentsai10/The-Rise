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

    let audio_snippets = []

    navigator.mediaDevices.getUserMedia({audio:true, video:false}).then(stream => {handlerFunction(stream)});

    function handlerFunction(stream){
        rec = new MediaRecorder(stream);
        rec.ondataavailable = e => {
            audio_snippets.push(e.data);
            if (rec.state == "inactive"){
                let blob = new Blob(audio_snippets, {type:'audio/mp3'});
                let recorded_audio = $('#recorded_audio');
                recorded_audio.attr('src', URL.createObjectURL(blob));
                sendData(blob);
            }
        }
    }

    function sendData(data){
        let file_input = document.getElementById('audio_input');
        let container = new DataTransfer();
        const d = new Date();
        let file_name = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}-${d.getHours()}-${d.getMinutes()}-${d.getSeconds()}-${d.getMilliseconds()}.mp3`

        let file = new File([data], file_name, {type: "audio/mp3", lastModified: d.getTime()});
        container.items.add(file);
        console.log(container.items);
        file_input.files = container.files;
    }

    let max_time = 120000;
    let remaining_time;

    let time_date_handling = {
        get_elapsed_duration: function (start_time) {
            let end_time = new Date();
            let duration = end_time.getTime() - start_time.getTime();
            duration = duration / 1000;
            let secs = Math.floor(duration % 60); 
            let secs_string = secs < 10 ? "0" + secs : secs + "";
    
            duration = Math.floor(duration / 60);
            let mins = duration % 60; 
            let mins_string = mins < 10 ? "0" + mins : mins + "";
            return mins_string + ":" + secs_string;
        }
    }

    let start_recording = function(){
        $('#record_button').css('display', 'none');
        $('#stop_button').css('display', 'flex');
        $('#recording_input_bar').css('display', 'block');
        $('#recorded_audio').css('display', 'none');
        rec.start();
        let progress = $('#recording_progress_dicussion');
        start_time = new Date();
        progress.animate({width: '100%'}, 120000, stop_recording_at_limit);
        elapsed_duration_interval = setInterval(() => {
            $('#elapsed_duration_display').html(time_date_handling.get_elapsed_duration(start_time));
        }, 1000);
    }

    let stop_recording = function(){
        if(typeof elapsed_duration_interval != "undefined"){
            clearInterval(elapsed_duration_interval);
            elapsed_duration_interval = undefined;
        }
        let progress = $('#recording_progress_dicussion');
        progress.stop();
        $('#stop_button').css('display', 'none');
        $('#record_button').css('display', 'flex');
        $('#recording_input_bar').css('display', 'none');
        if(MediaRecorder.state != 'inactive'){
            rec.stop();
        }
        $('#recorded_audio').css('display', 'flex');
        $('#clear_recording_button').css('display', 'flex');
    }

    let stop_recording_at_limit = function(){
        if(typeof elapsed_duration_interval != "undefined"){
            clearInterval(elapsed_duration_interval);
            elapsed_duration_interval = undefined;
        }
        let progress = $('#recording_progress_dicussion');
        progress.stop();
        $('#stop_button').css('display', 'none');
        $('#record_button').css('display', 'flex');
        $('#recording_input_bar').css('display', 'none');
        if(MediaRecorder.state != 'inactive'){
            rec.stop();
        }
        $('#recorded_audio').css('display', 'flex');
        $('#clear_recording_button').css('display', 'flex');
        $('#record_button').off('click');
    }


    let start_time;
    $('#record_button').click(start_recording);


    $('#stop_button').click(stop_recording);

    $('#clear_recording_button').click(function(){
        audio_snippets = [];
        $('#elapsed_duration_display').html('00:00');
        $('#recorded_audio').css('display', 'none');
        $('#clear_recording_button').css('display', 'none');
        let progress = $('#recording_progress_dicussion');
        progress.css('width', '0%');
        $('#recording_input_bar').css('display', 'block');
        $('#record_button').click(start_recording);
        let file_input = document.getElementById('audio_input');
        file_input.files = null;
    });
    
})


