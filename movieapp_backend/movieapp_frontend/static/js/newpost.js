$(document).ready(function(){
    var send_to_value = ''
    $(".glyphicon-star-empty").hover( rating_hover_in, rating_hover_out );

    $(".glyphicon").click(function () {
            $(this).addClass('glyphicon-star');
            $(this).addClass('clicked');
            $(this).removeClass('glyphicon-star-empty');
            $(this).unbind("mouseenter mouseleave");
            $(this).prevAll().addClass('glyphicon-star');
            $(this).prevAll().addClass('clicked');
            $(this).prevAll().removeClass('glyphicon-star-empty');
            $(this).prevAll().unbind("mouseenter mouseleave");
            $(this).nextAll().hover( rating_hover_in, rating_hover_out);
            $(this).nextAll().removeClass("clicked");
            $(this).nextAll().addClass('glyphicon-star-empty');
            $(this).nextAll().removeClass("glyphicon-star");
            bind_stars_to_int();

    });
    $("input").click(function(){
        if ($(this).hasClass('error')) {
            $(this).removeClass('error');
        }
    });
    $("#newpost_form").submit(function(e){
        if ($('#title_input').val().trim() === '') {
                e.preventDefault(e);
                $('#title_input').addClass('error');
        }
        else if ($('#rating_input').val().trim() === ''){
                e.preventDefault(e);
                $('#rating_input').addClass('error');
        }

        $("#send_to_input").val(options);
    });

    var options = [];

    $( '.dropdown-menu a' ).on( 'click', function( event ) {

       var $target = $( event.currentTarget ),
           val = $target.attr( 'data-value' ),
           $inp = $target.find( 'input' ),
           idx;

       if ( ( idx = options.indexOf( val ) ) > -1 ) {
          options.splice( idx, 1 );
          setTimeout( function() { $inp.prop( 'checked', false ) }, 0);
       } else {
          options.push( val );
          setTimeout( function() { $inp.prop( 'checked', true ) }, 0);
       }

       $( event.target ).blur();

       return false;
    });
});

var rating_hover_in = function() {
    $(this).addClass('glyphicon-star');
    $(this).removeClass('glyphicon-star-empty');
    $(this).prevAll().addClass('glyphicon-star');
    $(this).prevAll().removeClass('glyphicon-star-empty');
}

var rating_hover_out = function() {
    $(this).addClass('glyphicon-star-empty');
    $(this).removeClass('glyphicon-star');
    $(this).prevUntil('span.clicked').addClass('glyphicon-star-empty');
    $(this).prevUntil('span.clicked').removeClass('glyphicon-star');
}

var bind_stars_to_int = function(){
    var num = $('.glyphicon-star').length;
    $('#rating_input').val(num);
}