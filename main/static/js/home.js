$(document).ready(function(){
    
    $(document).on('input', '#discussion_title', function(){
        $('#discussion_title_input').val($('#discussion_title').val()); 
    });

    $(document).on('click', '.discussion_type_radio_button', function(){
        $('.discussion_type_radio_button').removeClass("selected");
        $('.person_button').attr('src', "/static/img/filled_person.svg");
        $(this).addClass("selected");
        let id = "#filled_person_" + $(this).attr('data-option');
        $(id).attr('src', "/static/img/filled_person_white.svg")
        
        $('#discussion_participant_cap_input').attr('value', $(this).attr('data-option'));
    });

    var audio_snippets = [];

    navigator.mediaDevices.getUserMedia({audio:true, video:false}).then(stream => {handlerFunction(stream)});

    function handlerFunction(stream){
        rec = new MediaRecorder(stream);
        rec.ondataavailable = e => {
            audio_snippets.push(e.data);
            if (rec.state == "inactive"){
                let blob = new Blob(audio_snippets, {type:'audio/mp3'});
                let recorded_audio = $('.recorded_audio');
                recorded_audio.attr('src', URL.createObjectURL(blob));
                sendData(blob);
            }
        }
    }

    function sendData(data){
        let file_input = document.getElementsByClassName('audio_input');
        let container = new DataTransfer();
        const d = new Date();
        let file_name = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}-${d.getHours()}-${d.getMinutes()}-${d.getSeconds()}-${d.getMilliseconds()}.mp3`

        let file = new File([data], file_name, {type: "audio/mp3", lastModified: d.getTime()});
        container.items.add(file);
        for(let i = 0; i < file_input.length; i++){
            file_input[i].files = container.files;
        }
    }

    const time_limit = 120000;
    var remaining_time = time_limit;
    var elapsed_time;

    var time_date_handling = {
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

    var start_recording = function(){
        console.log('here')
        $('.record_button').css('display', 'none');
        $('.stop_button').css('display', 'flex');
        $('.recording_input_bar').css('display', 'block');
        $('.recorded_audio').css('display', 'none');
        if(rec.state == "inactive"){
            rec.start();
        }
        let progress = $('.recording_progress');
        start_time = new Date();
        if (elapsed_time){
            start_time.setMinutes(start_time.getMinutes() - elapsed_time.mins);
            start_time.setSeconds(start_time.getSeconds() - elapsed_time.secs);
        }
        progress.animate({width: '100%'}, remaining_time, stop_recording_at_limit);
        elapsed_duration_interval = setInterval(() => {
            $('.elapsed_duration_display').html(time_date_handling.get_elapsed_duration(start_time));
        }, 1000);
    }

    var stop_recording = function(){
        
        if(typeof elapsed_duration_interval != "undefined"){
            clearInterval(elapsed_duration_interval);
            elapsed_duration_interval = undefined;
        }
        const elapsed_time_text = $('.elapsed_duration_display').html().split(":");
        const elapsed_time_as_nums = elapsed_time_text.map(num_string => parseInt(num_string));
        elapsed_time = {
            mins: elapsed_time_as_nums[0],
            secs: elapsed_time_as_nums[1],
        };
        remaining_time = 120000 - (elapsed_time.mins * 60000 + elapsed_time.secs * 1000);
        let progress = $('.recording_progress');
        progress.stop();
        $('.stop_button').css('display', 'none');
        $('.record_button').css('display', 'flex');
        $('.recording_input_bar').css('display', 'none');
        if(MediaRecorder.state != 'inactive'){
            rec.stop();
        }
        $('.recorded_audio').css('display', 'flex');
        $('.clear_recording_button').css('display', 'flex');
    }

    var stop_recording_at_limit = function(){
        if(typeof elapsed_duration_interval != "undefined"){
            clearInterval(elapsed_duration_interval);
            elapsed_duration_interval = undefined;
        }
        let progress = $('#recording_progress_dicussion');
        progress.stop();
        $('.stop_button').css('display', 'none');
        $('.record_button').css('display', 'flex');
        $('.recording_input_bar').css('display', 'none');
        if(MediaRecorder.state != 'inactive'){
            rec.stop();
        }
        $('.recorded_audio').css('display', 'flex');
        $('.clear_recording_button').css('display', 'flex');
        $('.record_button').off('click');
    }

    var clear_recording = function(){
        audio_snippets = [];
        $('.elapsed_duration_display').html('00:00');
        $('.recorded_audio').css('display', 'none');
        $('.clear_recording_button').css('display', 'none');
        $('.recording_progress').css('width', '0%');
        $('.recording_input_bar').css('display', 'block');
        if(remaining_time == 0){
            $(document).on("click", '.record_button', start_recording);
        }
        let file_input = document.getElementsByClassName('audio_input');
        for(let i = 0; i < file_input.length; i++){
            file_input[i].files = null;
        }
        remaining_time = time_limit;
        elapsed_time = null;
    }


    var start_time;
    $(document).on('click', '.record_button', start_recording);


    $(document).on('click', '.stop_button', stop_recording);

    $(document).on('click', '.clear_recording_button', clear_recording);



    $(document).on('click', '.post_discussion_button', function(){
        $('#discussion_form').submit();
    });
    $(document).on('click', '.post_response_button', function(){
        $('#response_form').submit();
    });

    $(document).on('click', '.space_heading', function(){
        $.ajax({
            type: 'GET',
            url: $(this).attr('href'),
            success: function (data) {
                $('.discussion_posts_block').html(data)
                $.ajax({
                    type: 'GET',
                    url: "http://localhost:8000/load_discussion_banner",
                    success: function (data) {
                        $('.discussion_banner').html(data);
                    },
                    error: function(data) {
                    }
                });
            },
            error: function(data) {
            }
        });
        return false;
    });

    $(document).on('click', '#plus_discussion_button_big', function(){
        $('#plus_discussion_button_big').css('display', 'none');
        $('#discussion_form_block').css('display', 'flex');
        $('.post_discussion_banner').css('display', 'flex');
        $('.response_banner').css('display', 'none');
        $('.responses_block').css('display', 'none');
        $('#response_form_block').css('display', 'none');
    });

    $(document).on('click', '#plus_response_button_big', function(){
        $('#discussion_form_block').css('display', 'none');
        $('#response_form_block').css('display', 'flex');
        $('.response_banner').css('display', 'flex');
        $('.responses_block').css('display', 'none');
        $('.post_discussion_banner').css('display', 'none');
    });

    $(document).on('click', '.discussion', function(){
        let discussion_id = $(this).attr('data-discussion-id')
        let discussion_index = $(this).attr('data-discussion-index')
        $.ajax({
            type: 'GET',
            url: `http://localhost:8000/load_response/${discussion_id}/${discussion_index}`,
            success: function (data) {
                $('.response_posts_block').html(data)
                $.ajax({
                    type: 'GET',
                    url: "http://localhost:8000/load_response_banner",
                    success: function (data) {
                        console.log("here");
                        $('.response_banner').html(data);
                        $('.response_banner').css('display', 'flex');
                        $('.responses_block').css('display', 'flex');
                        $('.post_discussion_banner').css('display', 'none');
                        $('.discussion_form_block').css('display', 'none');
                        $('#plus_discussion_button_big').css('display', 'flex');
                        $('#plus_response_button_big').css('display', 'flex');
                        $('.error_list').css('display', 'none');
                    },
                    error: function(data) {
                    }
                });
            },
            error: function(data) {
            }
        });
        return false;
    });

    $(document).on('click', '.favorite_button', function(){
        if($(this).attr('data-active') != "favorited"){
            $('.star').attr('src', '/static/img/filled_star.svg');
            $(this).attr('data-active', "unfavorited");
        }else{
            $('.star').attr('src', '/static/img/star.svg');
            $(this).attr('data-active', "favorited");
        }
        $.ajax({
            type: 'GET',
            url: $(this).attr('href'),
            success: function (data) {
                $('.spaces_block').html(data)
            },
            error: function(data) {
            }
        });
        return false;
    });

    $(document).on('click', '.discussion_tab_button', function(){
        $('.discussion_tab_button').removeClass('selected_discussion_button');
        $(this).addClass('selected_discussion_button');
        $.ajax({
            type: 'GET',
            url: $(this).attr('href'),
            success: function (data) {
                $('.discussion_posts_block').html(data);
            },
            error: function(data) {
            }
        });
        return false;
    });

    $(document).on('click', '.bookmark_link_block', function(){
        if($(this).attr('data-active') != "saved"){
            $('.bookmark').attr('src', '/static/img/filled_bookmark.svg');
            $(this).attr('data-active', "unsaved");
        }else{
            $('.bookmark').attr('src', '/static/img/empty_bookmark.svg');
            $(this).attr('data-active', "favorited");
        }
        $.ajax({
            type: 'GET',
            url: $(this).attr('href'),
            success: function (data) {
                $('.discussion_posts_block').html(data);
            },
            error: function(data) {
            }
        });
        return false;
    });

    
})


