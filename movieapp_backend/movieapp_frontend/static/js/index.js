$(document).ready(function(){
      movieRating = $('.movie_rating_int').length;
      for (i=0; i<movieRating; i++){
        convertToStars(i);
      }


});

var convertToStars = function(i){
        section = $('.movie_rating')[i]
        section = $('span.movie_rating_int', section)
        rating = section.text()
        fullStar = parseInt(rating);
        emptyStar = 10 - fullStar
        for (i=0; i < fullStar; i++){
            section.parent().append("<span class='glyphicon glyphicon-star'></span>")
        }
        for (i=0; i < emptyStar; i++){
            section.parent().append("<span class='glyphicon glyphicon-star-empty'></span>")
        }
}