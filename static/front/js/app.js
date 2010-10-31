$(function() {
	$('#media-photos').live('mouseenter', function() { $('span#photos').fadeIn(200);});
	$('#media-photos').live('mouseleave', function() { $('span#photos').fadeOut(300);});

	$('#media-videos').live('mouseenter', function() { $('span#videos').fadeIn(200);});
	$('#media-videos').live('mouseleave', function() { $('span#videos').fadeOut(300);});

	$('#media-presse').live('mouseenter', function() { $('span#presse').fadeIn(200);});
	$('#media-presse').live('mouseleave', function() { $('span#presse').fadeOut(300);});
	
	// $(".gallery").live('click', function(){ $(this).fancybox(); });
	
	$('#newsletter').submit(newsletter);
	
	$('#player').jPlayer({
		ready: play,
		swfPath: '/static/front/Jplayer.swf',
		bgcolor: '#000000'
	});
});


function play() {
	
}


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
			$('#pages').fadeIn(300, function() {
				$('.pages-background').fadeIn(300);
			});
		});
	} else {
		$('.pages-background').fadeOut(200, function() {
			$('#page').fadeOut(200, function() {
				fill();
				$(this).fadeIn(200, function() {
					$('.pages-background').fadeIn(200);
				});
			});
		});
	}
}

function fadeBack() {
	$('.pages-background').fadeOut(200, function() {
		$('#pages').fadeOut(200, function() {
			$('#home').fadeIn(200);
		});
	});
}


function newsletter() {
	var form = $('#newsletter');
	var value = $('#newsletter input').val();
	
	$.ajax({
		url: form.attr('action'),
		data: {email: value},
		method: 'get',
		format: 'text',
		success: function(data) {
			console.log(data);
			var conf = $('#confirm');
			if (data.confirm == 0) {
				var mess = 'not subbmitted';
			} else if(data.confirm == 2) {
				var mess = 'already subscribed';
			} else {
				var mess = 'ok';
			}
			conf.html(mess);
		}
	});
	
	return false;
}