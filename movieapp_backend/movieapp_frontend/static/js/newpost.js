$(document).ready(function(){
    var send_to_value = ''

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

       console.log( options );
       return false;
    });
});