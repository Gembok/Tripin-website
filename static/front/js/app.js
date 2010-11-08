$(function() {
	window.location.hash = '#/home';
	
	var media = ['photos', 'videos', 'presse'];
	
	for (x in media) {
		var med = media[x];
		var logo = $('#media-'+med);
		var text = $('span#'+med);
		logo.live('mouseenter', function() { text.fadeIn(200);});
		logo.live('mouseleave', function() { text.fadeOut(300);});
	}
	
	$('#agenda li').click(agenda);
	
	// $(".gallery").live('click', function(){ $(this).fancybox(); });
	
	$('#newsletter').submit(newsletter);
	$('#guestbook_link').click(function() {$('#guestbook_form').slideToggle(); return false;});
	$('#guestbook_form').submit(guestbook);
});

$.hashListen('/', function() {
	window.location.hash = '#/home';
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
	
	$('#page').fadeOut(300, function() {
		$('#page').html(html);
		$('#page').fadeIn(300);
	});
}


function agenda(evt) {
	$(this).children('.infos').toggle();
}


function newsletter() {
	var form = $('#newsletter');
	
	$.ajax({
		url: form.attr('action'),
		data: form.serialize(),
		type: 'GET',
		format: 'text',
		success: function(data) {
			var conf = $('#confirm');
			if (data.confirm == 0) {
				var mess = 'not submitted';
			} else if(data.confirm == 2) {
				var mess = 'already subscribed';
			} else {
				var mess = 'inscrit !';
			}
			conf.html(mess);
		}
	});
	
	return false;
}

function guestbook() {
	var form = $('#guestbook_form');
	
	$.ajax({
		url: form.attr('action'),
		data: form.serialize(),
		type: 'POST',
		format: 'text',
		success: function(data) {
			window.location = '#/guestbook';
		}
	});
	
	return false;
}
