$(function() {
	$('#media-photos').live('mouseenter', function() { $('span#photos').fadeIn(200);});
	$('#media-photos').live('mouseleave', function() { $('span#photos').fadeOut(300);});

	$('#media-videos').live('mouseenter', function() { $('span#videos').fadeIn(200);});
	$('#media-videos').live('mouseleave', function() { $('span#videos').fadeOut(300);});

	$('#media-presse').live('mouseenter', function() { $('span#presse').fadeIn(200);});
	$('#media-presse').live('mouseleave', function() { $('span#presse').fadeOut(300);});
});

$.hashListen('/', function() {
	fadeBack();
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

function fill(data, top) {
	var html = Mustache.to_html(data.template, data.data);
	
	function fill() {
		$('#page').html(html);
	}
	
	if ($('#pages').css('display') == 'none') {
		$('#home').fadeOut(300, function() {
			fill();
			$('#pages').fadeIn(300);
		});
	} else {
		$('#page').fadeOut(300, function() {
			fill();
			$(this).fadeIn(300);
		});
	}
}

function fadeBack() {
	$('#pages').fadeOut(300, function() {
		$('#home').fadeIn(300);
	});
}