$(document).ready(function(){
    movieRating = $('#movie_rating').text();
    convertToStars(movieRating);


});

var convertToStars = function(rating){
        fullStar = parseInt(rating);
//        fullStar = Math.floor(rating);
        console.log(fullStar);
//        if (rating % 1 === 0.5) {
//            halfStar = 1;
//            emptyStar = 5 - fullStar - halfStar;
//        }
//        else {
//            halfStar = 0;
//            emptyStar = 5 - fullStar;
//        }
//        console.log(halfStar);
        emptyStar = 10 - fullStar
        console.log(emptyStar);
        for (i=0; i < fullStar; i++){
            $('#movie_rating').append("<span class='glyphicon glyphicon-star'></span>")
        }
//        if (halfStar === 1) {
//            $('#movie_rating').append("<span class='glyphicon glyphicon-star half'></span>")
//        }
        for (i=0; i < emptyStar; i++){
            $('#movie_rating').append("<span class='glyphicon glyphicon-star-empty'></span>")
        }
    }