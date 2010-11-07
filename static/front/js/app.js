$(function() {
	$('#media-photos').live('mouseenter', function() { $('span#photos').fadeIn(200);});
	$('#media-photos').live('mouseleave', function() { $('span#photos').fadeOut(300);});

	$('#media-videos').live('mouseenter', function() { $('span#videos').fadeIn(200);});
	$('#media-videos').live('mouseleave', function() { $('span#videos').fadeOut(300);});

	$('#media-presse').live('mouseenter', function() { $('span#presse').fadeIn(200);});
	$('#media-presse').live('mouseleave', function() { $('span#presse').fadeOut(300);});
	
	// $(".gallery").live('click', function(){ $(this).fancybox(); });
	
	$('#newsletter').submit(newsletter);
	$('#guestbook_link').click(function() {$('#guestbook_form').slideToggle(); return false;});
	$('#guestbook_form').submit(guestbook);
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
		
	$('#page').fadeOut(300, function() {
		$('#page').html(html);
		$('#page').fadeIn(300);
	});
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
				var mess = 'not subbmitted';
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
			// if (data == '1') {
			// 	window.location = '#/guestbook';
			// }
			window.location = '#/guestbook';
		}
	});
	
	return false;
}