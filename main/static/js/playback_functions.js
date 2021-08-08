$(document).ready(function(){
    let prevActiveIndex = -1;
    Amplitude.init({
        "songs": [
        {
            "name": "Same Energy",
            "artist": "Kid Laroi",
            "url": "static/audio/attention.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "I Like That",
            "artist": "Bazzi",
            "url": "static/audio/bazzi.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "Attention",
            "artist": "Kid Laroi",
            "url": "static/audio/attention.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "Hotel",
            "artist": "Claire Rosenkranz",
            "url": "static/audio/hotel.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "comethru",
            "artist": "Jeremy Zucker",
            "url": "static/audio/comethru.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "Slow Dancing in a Burning Room",
            "artist": "John Mayer",
            "url": "static/audio/sdbr.mp3",
            "element": document.createElement("audio"),
        },
        {
            "name": "IFLY",
            "artist": "Bazzi",
            "url": "static/audio/ifly.mp3",
            "element": document.createElement("audio"),
        },
        ],
        playlists: {
            "1": {
                songs: [0, 3, 4, 5, 6, 1, 2]
            }
        },
        starting_playlist: "1",
        starting_playlist_song: 0,
        preload: "metadata",
        callbacks: {
            song_change: function(){
                let activeID = Amplitude.getActivePlaylistMetadata().active_index;
                let prev_item_c;
                let item_c;

                if(activeID == null){
                    Amplitude.setActivePlaylistMetadata("1", {active_index: 0});
                    activeID = Amplitude.getActivePlaylistMetadata().active_index;
                }
                if(prevActiveIndex != activeID){
                    prev_item_c = ".duration-" +  prevActiveIndex;
                    $(prev_item_c).css("display", "flex");
                    prev_item_c = ".current-time-" + prevActiveIndex;
                    $(prev_item_c).css("display", "none");
                    prev_item_c = ".play-" +  prevActiveIndex;
                    $(prev_item_c).css("display", "flex");
                    prev_item_c = ".pause-" + prevActiveIndex;
                    $(prev_item_c).css("display", "none");
                }
                item_c = ".duration-" +  activeID;
                $(item_c).css("display", "none");
                item_c = ".current-time-" + activeID;
                $(item_c).css("display", "flex");
                item_c = ".play-" +  activeID;
                $(item_c).css("display", "none");
                item_c = ".pause-" + activeID;
                $(item_c).css("display", "flex");
                prevActiveIndex = activeID;
            },
            next:function(){
                if(Amplitude.getActivePlaylistMetadata().active_index == 0){
                    let id = Amplitude.getActivePlaylistMetadata().active_index;
                    let item_c = ".duration-" +  id;
                    $(item_c).css("display", "flex");
                    item_c = ".current-time-" + id;
                    $(item_c).css("display", "none");
                    item_c = ".play-" +  id;
                    $(item_c).css("display", "flex");
                    item_c = ".pause-" + id;
                    $(item_c).css("display", "none");
                    prevActiveIndex = id;
                }
            }
        }
    });

    for(let i = 0; i < Amplitude.getActivePlaylistMetadata().songs.length; i++){
        var song = Amplitude.getActivePlaylistMetadata().songs[i];
        let au = song.element;
        au.src = song.url;
        au.id = i;
        au.preload = "auto";
        au.addEventListener('loadedmetadata', function(){
            var duration = Math.floor(au.duration);
            let mins = Math.floor(duration / 60); 
            let secs = duration % 60;
            secs = secs.toLocaleString('en-US', {
                minimumIntegerDigits: 2,
                useGrouping: false
            })
            let c = ".duration-" + i;
            $(c).html(mins + ":" + secs);
        },false);
    }

    $('.amplitude-song-played-progress').click(function(e){
        if( Amplitude.getActivePlaylistMetadata().active_index == ($(this).attr('data-amplitude-song-index')) ){
            var offset = this.getBoundingClientRect();
            var x = e.pageX - offset.left;

            Amplitude.setSongPlayedPercentage( ( parseFloat( x ) / parseFloat( this.offsetWidth) ) * 100 );
        }
    });


    $('.amplitude-play-pause').click(function(e){
        let id = $(this).attr('data-amplitude-song-index');
        let item_c;

        if(Amplitude.getPlayerState() == "playing"){
            item_c = ".duration-" +  id;
            $(item_c).css("display", "none");
            item_c = ".current-time-" + id;
            $(item_c).css("display", "flex");
            item_c = ".play-" +  id;
            $(item_c).css("display", "none");
            item_c = ".pause-" + id;
            $(item_c).css("display", "flex");
        }
        else{
            item_c = ".play-" +  id;
            $(item_c).css("display", "flex");
            item_c = ".pause-" + id;
            $(item_c).css("display", "none");
        }
        prevActiveIndex = Amplitude.getActivePlaylistMetadata().active_index;
    });
})




