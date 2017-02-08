$(document).ready(function(){
    $('#select_avatar_button').on('change', function(){
        var input_val = $(this).val().split('\\').slice(-1)[0];
        $('#selected_file_input').val(input_val);
    })

    $("#change_avatar_form").submit(function(e){
        if ($('#selected_file_input').val().trim() === '') {
                e.preventDefault(e);
                $('#selected_file_input').addClass('error');

        }
    });
    $("#change_name_form").submit(function(e){
        if ($('#change_name_input').val().trim() === '') {
                e.preventDefault(e);
                $('#change_name_input').addClass('error');
        }
    });
    $('#show_change_avatar_form').click(function(){
        $("#change_avatar_form").toggle();
    });

    $('#toggle_change_name_form').click(function(){
        $("#change_name_form").toggle();
    });
    $('#change_password_button').click(function(){
        $("#change_password_form").toggle();
    });
});