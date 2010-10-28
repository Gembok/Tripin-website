$.hashListen('/', function() {
	slideUp();
});

$.hashListen('/:action/?', function(action) {
	var url = '/'+action;
	$.getJSON(url, null, function(data) {
		fill(data);
	});
});

$.hashListen('/:action/:id/?', function(action, id) {
	var url = '/'+action+'/'+id;
	console.log(url);
	$.getJSON(url, null, function(data) {
		fill(data);
	});
});


function slideDown(fn) {
	$('#container').animate({top: '500px'}, 300, 'swing', fn);
}

function slideUp() {
	$('#page').fadeOut(150);
	$('#container').animate({top: '0px'}, 300, 'swing');
}

function fill(data) {
	var html = Mustache.to_html(data.template, data.data);
	
	$('#page').fadeOut(150, function() {
		$(this).html(html);
		slideDown();
		$(this).fadeIn(500);
	});
}