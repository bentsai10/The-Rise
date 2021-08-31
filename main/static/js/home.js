$(document).ready(function(){
    /**
     * Allow discussion title input element to change hidden discussion form value even if it's not physically in the form block
     */
    $(document).on('input', '#discussion_title', function(){
        $('#discussion_title_input').val($('#discussion_title').val()); 
    });

    /**
     * Change hidden discussion form value of participant cap based on clicked participant button
     */
    $(document).on('click', '.discussion_type_radio_button', function(){
        $('.discussion_type_radio_button').removeClass("selected");
        $('.person_button').attr('src', "https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/filled_person.svg");
        $(this).addClass("selected");
        let id = "#filled_person_" + $(this).attr('data-option');
        $(id).attr('src', "https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/filled_person_white.svg")
        
        $('#discussion_participant_cap_input').attr('value', $(this).attr('data-option'));
    });

    var audio_snippets = [];

    navigator.mediaDevices.getUserMedia({audio:true, video:false}).then(stream => {handlerFunction(stream)});

    /**
     * Handle function for when recorded audio detected
     */
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

    /**
     * function to transfer recorded audio to file input element in HTML
     */
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

    //object to get elapsed time thus far
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

    /**
     * Function to start recording
     */
    var start_recording = function(){
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

    /**
     * Function to stop recording when user stops recording
     */
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
        $('.duration_input').val($('.elapsed_duration_display').html());
    }

    /**
     * Function to stop recording when time limit is reached
     */
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
        $('.duration_input').val($('.elapsed_duration_display').html());
        $('.record_button').off('click');
    }

    /**
     * Function to clear recorded audio
     */
    var clear_recording = function(){
        audio_snippets = [];
        $('.elapsed_duration_display').html('00:00');
        $('.duration_input').val('00:00');
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
        $('audio').each(function(){
            this.pause(); // Stop playing
            this.currentTime = 0; // Reset time
        }); 
    }

    var load_responses = function(){
        let discussion_id = $(this).attr('data-discussion-id');
        let discussion_index = $(this).attr('data-discussion-index');
        $.ajax({
            type: 'GET',
            url: `http://localhost:8000/load_response/${discussion_id}/${discussion_index}`,
            success: function (data) {
                $('.response_posts_block').html(data);
                $.ajax({
                    type: 'GET',
                    url: "http://localhost:8000/load_response_banner",
                    success: function (data) {
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
    }

    var start_time;

    /**
     * Process click on start recording button
     */
    $(document).on('click', '.record_button', start_recording);

    /**
     * Process click on stop recording button
     */
    $(document).on('click', '.stop_button', stop_recording);
    
    /**
     * Process click on clear recording button
     */
    $(document).on('click', '.clear_recording_button', clear_recording);


    /**
     * Process post button click for discussions
     */
    $(document).on('click', '.post_discussion_button', function(){
        $('#discussion_form').submit();
    });

    /**
     * Process post button click for responses
     */
    $(document).on('click', '.post_response_button', function(){
        $('#response_form').submit();
    });

    /**
     * Process a click on a link for a space
     */
    $(document).on('click', '.space_heading', function(){
        $.ajax({
            type: 'GET',
            url: $(this).attr('href'),
            success: function (data) {
                $('.discussion_posts_block').html(data);
                prevActiveIndex = -1;
                prevActivePlaylist = -1;
                $.ajax({
                    type: 'GET',
                    url: "http://localhost:8000/load_discussion_banner",
                    success: function (data) {
                        $('.discussion_banner').html(data);
                        $('.response_banner').html('');
                        $('.response_posts_block').html('');
                        $.ajax({
                            type: 'GET',
                            url: 'http://localhost:8000/display_spaces',
                            success: function (data) {
                                $('.spaces_block').html(data)
                            },
                            error: function(data) {
                            }
                        });
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

    /**
     * Process click on the button to add discussion
     */
    $(document).on('click', '#plus_discussion_button_big', function(){
        $('#plus_discussion_button_big').css('display', 'none');
        $('#discussion_form_block').css('display', 'flex');
        $('.post_discussion_banner').css('display', 'flex');
        $('.response_banner').css('display', 'none');
        $('.responses_block').css('display', 'none');
        $('#response_form_block').css('display', 'none');
        $('.error_list').css('display', 'flex');
    });

    /**
     * Process click on the button to add response
     */
    $(document).on('click', '#plus_response_button_big', function(){
        $('#discussion_form_block').css('display', 'none');
        $('#response_form_block').css('display', 'flex');
        $('.response_banner').css('display', 'flex');
        $('.responses_block').css('display', 'none');
        $('.post_discussion_banner').css('display', 'none');
        $('.error_list').css('display', 'flex');
    });

    /**
     * Process click on a discussion element (only specific sections of it b/c don't want reload if play button pressed)
     */
    $(document).on('click', '.discussion_bottom', load_responses);
    $(document).on('click', '.discussion_top_middle', load_responses);

    /**
     * Process a click of the favorite button
     */
    $(document).on('click', '.favorite_button', function(){
        if($(this).attr('data-active') != "favorited"){
            $('.star').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/filled_star.svg');
            $(this).attr('data-active', "favorited");
        }else{
            $('.star').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/star.svg');
            $(this).attr('data-active', "unfavorited");
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

    /**
     * Process a click of the discussion filtering buttons (Recent/Top/Saved)
     */
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

    /**
     * Process a click of the bookmark button
     */
    $(document).on('click', '.bookmark_link_block', function(){
        if($(this).attr('data-active') != "saved"){
            $('.bookmark').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/filled_bookmark.svg');
            $(this).attr('data-active', "unsaved");
        }else{
            $('.bookmark').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/empty_bookmark.svg');
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

    /**
     * Process the click on play/pause button
     */
    $(document).on('click', '.amplitude-play-pause', function(e){
        /**
         * Get index of song in playlist and playlist id
         */
        let song_id = $(this).attr('data-amplitude-song-index');
        let playlist_id = $(this).attr("data-amplitude-playlist");
       
        let current_song_element;
        /**
         * Confusing b/c once amplitude-play-pause is clicked, state changes, so
         * this is run when PLAY button is pressed
         * 
         * Hide PAUSE, display PLAY
         * Hide DURATION, display CURRENT-TIME
         */
        if(Amplitude.getPlayerState() == "playing"){
            current_song_element = ".duration-" + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "none");
            current_song_element = ".current-time-" + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "flex");
            current_song_element = ".play-" +  + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "none");
            current_song_element = ".pause-" + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "flex");
        }
        /**
         * Run when PAUSE button pressed
         * 
         * Hide PLAY, display PAUSE
         */
        else{
            current_song_element = ".play-" + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "flex");
            current_song_element = ".pause-" + playlist_id + "-" + song_id;
            $(current_song_element).css("display", "none");
        }
        /**
         * Save current playlist and index so when we change songs we can change visual elements of current song
         */
        prevActiveIndex = Amplitude.getActiveSongMetadata().index
        prevActivePlaylist = Amplitude.getActivePlaylist();
    });

    /**
     * Function to make progress bar interactive for the active song
     */
    $(document).on('click', '.amplitude-song-played-progress', function(e){
        if( Amplitude.getActiveSongMetadata().index == ($(this).attr('data-amplitude-song-index')) ){
            var offset = this.getBoundingClientRect();
            var x = e.pageX - offset.left;

            Amplitude.setSongPlayedPercentage( ( parseFloat( x ) / parseFloat( this.offsetWidth) ) * 100 );
        }
    });

    /**
     * Process input to space search bar
     */
    $(document).on('input', '#space_search_input', function(){
        $('#space_search_form').submit();
    })

    /**
     * Process submit of space search query
     */
    $(document).on('submit', '#space_search_form', function(){
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (data) {
                $('.spaces_block').html(data)
            },
            error: function(data) {
            }
        });
        return false;
    })
})


