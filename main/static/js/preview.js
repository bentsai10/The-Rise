$(document).ready(function(){
    $(document).on('click', '.amplitude-play-pause', function(e){
        /**
         * Get index of song in playlist and playlist id
         */
        let song_id = $(this).attr('data-amplitude-song-index');
        let playlist_id = $(this).attr("data-amplitude-playlist");
       
        let current_song_element;

        if(prevActiveIndex != song_id || prevActivePlaylist != playlist_id){
            let prev_song_element = ".duration-" + prevActivePlaylist + "-" + prevActiveIndex;
            $(prev_song_element).css("display", "flex");
            prev_song_element = ".current-time-" + prevActivePlaylist + "-" + prevActiveIndex;
            $(prev_song_element).css("display", "none");
            prev_song_element = ".play-" +  + prevActivePlaylist + "-" + prevActiveIndex;
            $(prev_song_element).css("display", "flex");
            prev_song_element = ".pause-" + prevActivePlaylist + "-" + prevActiveIndex;
            $(prev_song_element).css("display", "none");
        }
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
        prevActiveIndex = Amplitude.getActiveSongMetadata().index;
        prevActivePlaylist = Amplitude.getActivePlaylist();
    });

    var prevActiveIndex = -1;
    var prevActivePlaylist = -1;
    let songs = [];

    songs = [
        {
            "name": "Meaning of Education",
            "artist": "Jonathan Noel",
            "url": "https://the-rise-media-bucket.s3.us-east-2.amazonaws.com/audio/jon_noel_audio.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "Younger When We're Older",
            "artist": "Claudia Yang",
            "url": "https://the-rise-media-bucket.s3.us-east-2.amazonaws.com/audio/discussions/85/2021-11-05-04-34-05.mp3",
            "element": document.createElement("audio"),
        }, 
        {
            "name": "Why I Make Music",
            "artist": "Nick Popolizio",
            "url": "https://the-rise-media-bucket.s3.us-east-2.amazonaws.com/audio/nick_pop_audio.mp3",
            "element": document.createElement("audio"),
        }
    ]
    Amplitude.init({
        "songs": songs,
        playlists: {
            "0": {
                songs: [0,1,2]
            },
        },
        starting_playlist: "0",
        starting_playlist_song: "0",
        preload: "metadata",
        callbacks: {
            /**
             * Function to handle the event of a song change
             */
            song_change: function(){
                let song_id = Amplitude.getActiveSongMetadata().index;
                let playlist_id = Amplitude.getActivePlaylist();
                if(prevActiveIndex != song_id || prevActivePlaylist != playlist_id){
                    let prev_song_element = ".duration-" + prevActivePlaylist + "-" + prevActiveIndex;
                    $(prev_song_element).css("display", "flex");
                    prev_song_element = ".current-time-" + prevActivePlaylist + "-" + prevActiveIndex;
                    $(prev_song_element).css("display", "none");
                    prev_song_element = ".play-" +  + prevActivePlaylist + "-" + prevActiveIndex;
                    $(prev_song_element).css("display", "flex");
                    prev_song_element = ".pause-" + prevActivePlaylist + "-" + prevActiveIndex;
                    $(prev_song_element).css("display", "none");
                }
                
                if(prevActiveIndex != -1 || prevActivePlaylist != -1){
                    let current_song_element = ".duration-" + playlist_id + "-" + song_id;
                    $(current_song_element).css("display", "none");
                    current_song_element = ".current-time-" + playlist_id + "-" + song_id;
                    $(current_song_element).css("display", "flex");
                    current_song_element = ".play-" +  + playlist_id + "-" + song_id;
                    $(current_song_element).css("display", "none");
                    current_song_element = ".pause-" + playlist_id + "-" + song_id;
                    $(current_song_element).css("display", "flex");
                }

                prevActiveIndex = song_id;
                prevActivePlaylist = playlist_id;
            },
            /**
             * Function to handle the event of a song jumping to the next song
             */
            next:function(){
                /**
                 * If we have reached the end of the playlist
                 */
                if(Amplitude.getActiveSongMetadata().index == 0){
                    let id = Amplitude.getActiveSongMetadata().index;
                    let playlist = Amplitude.getActivePlaylist();
                    let current_song_element = ".duration-" +  playlist + "-" + id;
                    $(current_song_element).css("display", "flex");
                    current_song_element = ".current-time-" +  playlist + "-" + id;
                    $(current_song_element).css("display", "none");
                    current_song_element = ".play-" +  playlist + "-" + id;
                    $(current_song_element).css("display", "flex");
                    current_song_element = ".pause-" +  playlist + "-" + id;
                    $(current_song_element).css("display", "none");
                    prevActiveIndex = id;
                    prevActivePlaylist = Amplitude.getActivePlaylist();
                }
            },
        }
    });
})