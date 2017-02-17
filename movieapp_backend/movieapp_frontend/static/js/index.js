$(document).ready(function() {
	movieRating = $('.movie_rating_int').length;
	for (i = 0; i < movieRating; i++) {
		convertToStars(i);
	};
	$('.filter_posts_field').text('By title');
	$('.filter_posts_field').click(function() {
		var next = nextOrFirst($(this));
		$this = $(this)
		$this.attr("value", next);
		if (next === 'movie_title') {
			$this.text("By Title");
		} else if (next === 'from_user') {
			$this.text("By User");
		} else {
			$this.text("By Rating");
		}
		filter_posts();
	});
	$('.active').removeClass('active');
	$('#home_link').parent().addClass('active');
	$('#filter_posts_input').on('keyup change', filter_posts);



});

var filter_posts = function() {
	var input_string = $('#filter_posts_input').val().toLowerCase();
	var filter_posts_field = $('.filter_posts_field').attr("value");
	var to_show = $('.movie_post').filter(function() {
		return ($("#" + filter_posts_field, this).text().indexOf(input_string) !== -1)
	});
	$('.movie_post').hide();
	to_show.show();
};

var nextOrFirst = function(selector) {
	var values = ['movie_title', 'from_user', 'movie_rating_int'];
	var start = selector.attr("value")
	return values[($.inArray(start, values) + 1) % values.length];
};

var convertToStars = function(i) {
	section = $('.movie_rating')[i];
	section = $('span.movie_rating_int', section);
	rating = section.text();
	fullStar = parseInt(rating);
	emptyStar = 10 - fullStar;
	for (i = 0; i < fullStar; i++) {
		section.parent().append("<span class='glyphicon glyphicon-star'></span>");
	};
	for (i = 0; i < emptyStar; i++) {
		section.parent().append("<span class='glyphicon glyphicon-star-empty'></span>");
	};
};