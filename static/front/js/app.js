$(function() {
	$('#media-photos').live('mouseenter', function() { $('span#photos').fadeIn(200);});
	$('#media-photos').live('mouseleave', function() { $('span#photos').fadeOut(300);});

	$('#media-videos').live('mouseenter', function() { $('span#videos').fadeIn(200);});
	$('#media-videos').live('mouseleave', function() { $('span#videos').fadeOut(300);});

	$('#media-presse').live('mouseenter', function() { $('span#presse').fadeIn(200);});
	$('#media-presse').live('mouseleave', function() { $('span#presse').fadeOut(300);});
});

$.hashListen('/', function() {
	slideUp();
});

$.hashListen('/:action/?', function(action) {
	var url = '/'+action;
	$.getJSON(url, null, function(data) {
		fill(data);
	});
});

$.hashListen('/:action/([0-9]+)/?', function(action, id) {
	var top = 500;
	if (action == 'media') {
		top = 300;
	}
	var url = '/'+action+'/'+id;
	$.getJSON(url, null, function(data) {
		fill(data, top);
	});
});


function slideDown(top) {
	var top = 500;
	$('#slide').height(top);
	$('#container').animate({top: top}, 300, 'swing');
}

function slideUp() {
	$('#page').fadeOut(150);
	$('#container').animate({top: 0}, 300, 'swing');
}

function fill(data, top) {
	var html = Mustache.to_html(data.template, data.data);
	
	$('#page').fadeOut(150, function() {
		$(this).html(html);
		slideDown(top);
		$(this).fadeIn(500);
	});
}