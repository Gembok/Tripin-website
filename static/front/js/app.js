$.hashListen('/bio/?', function() {
	$.getJSON('/bio', {}, function(data) {
		fill(data.bio);
	});
});

$.hashListen('/music/?:id', function(id) {
	$.getJSON('/music/'+id, null, function(data) {
		fill(data);
	});
});

function slideDown(fn) {
	$('body').animate({left: '-400px'}, 300, 'swing', fn);
}

function fill(content) {
	slideDown(function() {
		$('#page').html(content);
		console.log('page filled with:\n'+content);
	});
}