$.hashListen('^/$', function() {
	slideUp();
});

$.hashListen('/bio/?', function() {
	$.getJSON('/bio', {}, function(data) {
		fill(data);
	});
});

$.hashListen('/music/?:id', function(id) {
	console.log('ok');
	$.getJSON('/music/'+id, null, function(data) {
		fill(data);
	});
});

function slideDown(fn) {
	$('#container').animate({top: '500px'}, 300, 'swing', fn);
}

function slideUp() {
	$('#page').fadeOut(200);
	$('#container').animate({top: '0px'}, 300, 'swing');
}

function fill(data) {
	var html = Mustache.to_html(data.template, data.data);
	
	$('#page').fadeOut(200, function() {
		$(this).html(html);
		$(this).fadeIn(400);
		slideDown();
	});
}