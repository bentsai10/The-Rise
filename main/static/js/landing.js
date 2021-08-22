$(document).ready(function(){
    function animateLoopText(){
        $('.loop_text').animate({marginLeft: '-64vw'}, 20000, 'linear', function(){
            $('.loop_text').animate({marginLeft: '0vw'}, 20000, 'linear', function(){
                animateLoopText();
            });
        });
    }

    function animateLoopTextSmall(){
        $('.loop_text_small').animate({marginLeft: '-39em'}, 15000, 'linear', function(){
            $('.loop_text_small').animate({marginLeft: '0em'}, 15000, 'linear', function(){
                animateLoopTextSmall();
            });
        });
    }

    function animateLoopTextSmallest(){
        $('.loop_text_smallest').animate({marginLeft: '-20em'}, 8000, 'linear', function(){
            $('.loop_text_smallest').animate({marginLeft: '0em'}, 8000, 'linear', function(){
                animateLoopTextSmallest();
            });
        });
    }

    function animateTopicBlock(){
        $('.topic_block').animate({marginLeft: '-150em'}, 70000, 'linear', function(){
            $('.topic_block').animate({marginLeft: '0em'}, 70000, 'linear', function(){
                animateTopicBlock();
            });
        });
    }

    function animateTopicBlockSmall(){
        $('.topic_block_small').animate({marginLeft: '-135em'}, 60000, 'linear', function(){
            $('.topic_block_small').animate({marginLeft: '0em'}, 60000, 'linear', function(){
                animateTopicBlockSmall();
            });
        });
    }

    function animateAudioBlock(){
        $('.audio_block').animate({marginLeft: '-177em'}, 70000, 'linear', function(){
            $('.audio_block').animate({marginLeft: '0em'}, 70000, 'linear', function(){
                animateAudioBlock();
            });
        });
    }
    function animateAudioBlockSmall(){
        $('.audio_block_small').animate({marginLeft: '-140em'}, 60000, 'linear', function(){
            $('.audio_block_small').animate({marginLeft: '0em'}, 60000, 'linear', function(){
                animateAudioBlockSmall();
            });
        });
    }
    function animateAudioBlockSmallest(){
        $('.audio_block_smallest').animate({marginLeft: '-172em'}, 60000, 'linear', function(){
            $('.audio_block_smallest').animate({marginLeft: '0em'}, 70000, 'linear', function(){
                animateAudioBlockSmallest();
            });
        });
    }

    function closeMenu(){
        $('body').removeClass('no_scroll');
        $('.overlay_menu').css('margin-left', '100vw');
        $('#menu_icon').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/hamburger.png');
        $('#menu_button').attr('data-open', 'no');
}

    $(document).on('click', '.menu_block', function(){
        if($('#menu_button').attr('data-open') == 'no'){
            $('body').addClass('no_scroll');
            $('.overlay_menu').css('margin-left', '0vw');
            $('#menu_icon').attr('src', 'https://the-rise-online-bucket.s3.us-east-2.amazonaws.com/img/purple_x.png');
            $('#menu_button').attr('data-open', 'yes');
        }else{
            closeMenu();
        }
    });

    $(document).on('click', '.menu_link', closeMenu);
    animateLoopText();
    animateLoopTextSmall();
    animateLoopTextSmallest();
    animateTopicBlock();
    animateTopicBlockSmall();
    animateAudioBlock();
    animateAudioBlockSmall();
    animateAudioBlockSmallest();

});
