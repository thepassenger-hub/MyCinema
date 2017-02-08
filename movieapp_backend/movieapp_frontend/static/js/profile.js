$(document).ready(function(){
    movieRating = $('#movie_rating').text();
    convertToStars(movieRating);


});

var convertToStars = function(rating){
        fullStar = parseInt(rating);
        console.log(fullStar);
        emptyStar = 10 - fullStar
        for (i=0; i < fullStar; i++){
            $('#movie_rating').append("<span class='glyphicon glyphicon-star'></span>")
        }
        for (i=0; i < emptyStar; i++){
            $('#movie_rating').append("<span class='glyphicon glyphicon-star-empty'></span>")
        }
    }