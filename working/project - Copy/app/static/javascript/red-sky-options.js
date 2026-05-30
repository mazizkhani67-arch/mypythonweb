$(window).load(function() {
	$('#slider').nivoSlider();
});

$(document).ready(function(){
    $('.pretty').prettyPhoto();
    //photostream
    $('.rsFlickrWidget').each(function(){
        var stream = $(this);
        var stream_container = $('<div />').addClass('rsFlickrWidgetStream');//stream.find('.rsFlickrWidgetStream');
        var stream_userid = stream.attr('data-userid');
        var stream_items = parseInt(stream.attr('data-items'));
        stream.append(stream_container);
        $.getJSON("http://api.flickr.com/services/feeds/photos_public.gne?lang=en-us&format=json&id="+stream_userid+"&jsoncallback=?", function(stream_feed){
            for(var i=0;i<stream_items&&i<stream_feed.items.length;i++){
                var stream_function = function(){
                    if(stream_feed.items[i].media.m){
                        var stream_a = $('<a>').addClass('rsFlickrWidgetStreamImage').attr('href',stream_feed.items[i].link);
                        var stream_img = $('<img>').attr('src',stream_feed.items[i].media.m).attr('alt','').load(function(){
                            stream_a.append(stream_img);
                            if(stream_img.width()<stream_img.height())
                                stream_img.attr('style','width: 100% !important; height: auto !important; max-width: none !important; max-height: none !important;');
                            else
                                stream_img.attr('style','width: auto !important; height: 100% !important; max-width: none !important; max-height: none !important;');
                        });
                        stream_container.append(stream_a);
                    }
                }
                stream_function();
            }
        });
    });
});


// FULL WIDE SLIDER
$(document).ready(function(){
	var slides_change_time = 3000; //time of slide change
	var slides_fade_time = 800; //time of fade effect, MUST BE LESS or equal THAN slides_change_time
	var slides_timeout_time = 5000; //time to wait before autoplay resumes, MUST BE BIGGER or equal THAN slides_change_time
	resize_slider();
	var slides = $('#wide_slider').children('.slide');
	var slides_selector = $('#wide_slider').children('.slidenr');
	var slides_nr = slides.length;
	var slides_current = -1;
	for(var i=0;i<slides_nr;i++){
		slides_selector.append('<li></li>');
	}
	var slides_selector_dots = slides_selector.children('li');
	var slides_selector_dots_array = $.makeArray(slides_selector_dots);
	slides_selector.css('width',slides_selector.children('li:first').width()*slides_nr+'px');
	var slides_transition = function(){
                slides.filter('.slide_active').removeClass('.slide_active').stop().animate({opacity:'0'},{duration:slides_fade_time,queue:false,complete:function(){$(this).css('display','block')}});
		slides_selector_dots.filter('.active').removeClass('active');
		slides_current++;
		if(slides_current>=slides_nr)
			slides_current = 0;
		slides_selector_dots.filter(':eq('+slides_current+')').addClass('active');
		slides.filter(':eq('+slides_current+')').addClass('slide_active').css('display','block').stop().animate({opacity:'1'},{duration:slides_fade_time,queue:false});
	}
	var slides_interval;
	var slides_interval_function = function(){
		slides_transition();
		slides_interval = setInterval(slides_transition,slides_change_time);
	}
	slides_interval_function();
	var slides_timeout;
	slides_selector_dots.click(function(){
		slides_current = slides_selector_dots_array.indexOf(this);
                slides.filter('.slide_active').removeClass('.slide_active').stop().animate({opacity:'0'},{duration:slides_fade_time,queue:false,complete:function(){$(this).css('display','block')}});
		slides_selector_dots.filter('.active').removeClass('active');
		slides_selector_dots.filter(':eq('+slides_current+')').addClass('active');
		slides.filter(':eq('+slides_current+')').addClass('slide_active').css('display','block').stop().animate({opacity:'1'},{duration:slides_fade_time,queue:false});
		clearInterval(slides_interval);
		clearTimeout(slides_timeout);
		slides_timeout = setTimeout(slides_interval_function,slides_timeout_time);
	});
});
$(document).ready(function(){
	t_time = 400; //duration of animation in miliseconds
	var member_margin_top = $('.member').css('margin-top');
	$('.member').hover(function(){
		$(this).stop().animate({marginTop:0},{duration:t_time,queue:false})
		$(this).children('.memberinfo').stop().animate({opacity:'toggle',paddingTop:'toggle',paddingBottom:'toggle',height:'toggle'},{duration:t_time,queue:false});
	},function(){
		$(this).stop().animate({marginTop:member_margin_top},{duration:t_time,queue:false})
		$(this).children('.memberinfo').stop().animate({opacity:'toggle',paddingTop:'toggle',paddingBottom:'toggle',height:'toggle'},{duration:t_time,queue:false});
	});
});
$(window).resize(resize_slider);
function resize_slider(){
	var h = 400*$(window).width()/1443;
	$('#wide_slider').css('height',h+'px');
	var s = $('#wide_slider .slidenr');
	s.css('top',h-24+'px');
}
if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(obj, start) {
		for (var i = (start || 0), j = this.length; i < j; i++) {
			if (this[i] === obj) { return i; }
		}
		return -1;
	}
}

//TITLE TOOL
var custom_top = 0;
var custom_left = 15;
var fade_time = 0;

ShowTooltip = function (e) {
    var text = $(this).next('.show-tooltip-text');
    if (text.attr('class') != 'show-tooltip-text') return false;

    text.fadeIn(fade_time, function () {
        var text_width = text.outerWidth();
        var left = e.clientX + custom_left;
        if (left + text_width > $(window).width()) left = e.clientX - text_width - custom_left;
        text.css('top', e.clientY + custom_top).css('left', left);
    })


    $(this).on('mousemove', MoveTooltip);
    return false;
}
HideTooltip = function (e) {
    var text = $(this).next('.show-tooltip-text');
    if (text.attr('class') != 'show-tooltip-text') return false;

    text.fadeOut(fade_time);

    $(this).off('mousemove');
}

SetupTooltips = function () {
    $('.show-tooltip').each(function () {
        $(this).after($('<span/>').attr('class', 'show-tooltip-text').html($(this).attr('title'))).attr('title', '');
    }).hover(ShowTooltip, HideTooltip);
}

MoveTooltip = function (e) {
    var text = $(this).next('.show-tooltip-text');
    var text_width = text.outerWidth();
    var left = e.clientX + custom_left;
    if (left + text_width > $(window).width()) left = e.clientX - text_width - custom_left;
    text.css({
        top: e.clientY + custom_top,
        left: left
    });
}

$(document).ready(function () {
    SetupTooltips();
});

(function(){
    var t_browser_has_css3;
    var t_css3_array = ['transition','-webkit-transition','-moz-transition','-o-transition','-ms-transition'];
    var t_css3_index;
    $(document).ready(function(){
        var t_css3_test = $('body');
        for(t_css3_index=0, t_css3_test.css(t_css3_array[t_css3_index],'');t_css3_index<t_css3_array.length&&null==t_css3_test.css(t_css3_array[t_css3_index]);t_css3_test.css(t_css3_array[++t_css3_index],''));
        if(t_css3_index<t_css3_array.length)
            t_browser_has_css3 = true;
        else
            t_browser_has_css3 = false;
        load_twitter();
    });
    //TWITTER
    var load_twitter = function(){
        var linkify = function(text){
            text = text.replace(/(https?:\/\/\S+)/gi, function (s) {
                return '<a href="' + s + '">' + s + '</a>';
            });
            text = text.replace(/(^|)@(\w+)/gi, function (s) {
                return '<a href="http://twitter.com/' + s + '">' + s + '</a>';
            });
            text = text.replace(/(^|)#(\w+)/gi, function (s) {
                return '<a href="http://search.twitter.com/search?q=' + s.replace(/#/,'%23') + '">' + s + '</a>';
            });
            return text;
        }
        $('.rs_twitter').each(function(){
            var t = $(this);
            var t_date_obj = new Date();
            var t_loading = 'Loading tweets..'; //message to display before loading tweets
            var t_container = $('<ul>').addClass('twitter').append('<li>'+t_loading+'</li>');
            t.append(t_container);
            var t_user = t.attr('data-user');
            var t_posts = parseInt(t.attr('data-posts'));
            $.getJSON("http://api.twitter.com/1/statuses/user_timeline/"+t_user+".json?callback=?", function(t_tweets){
                t_container.empty();
                for(var i=0;i<t_posts&&i<t_tweets.length;i++){
                    var t_date = Math.floor((t_date_obj.getTime()-Date.parse(t_tweets[i].created_at))/1000);
                    var t_date_str;
                    var t_date_seconds = t_date%60;
                    t_date=Math.floor(t_date/60);
                    var t_date_minutes = t_date%60;
                    if(t_date_minutes){
                        t_date=Math.floor(t_date/60);
                        var t_date_hours = t_date%60;
                        if(t_date_hours){
                            t_date=Math.floor(t_date/60);
                            var t_date_days = t_date%24;
                            if(t_date_days){
                                t_date=Math.floor(t_date/24);
                                var t_date_weeks = t_date%7;
                                if(t_date_weeks)
                                    t_date_str = t_date_weeks+' week'+(1==t_date_weeks?'':'s')+' ago';
                                else
                                    t_date_str = t_date_days+' day'+(1==t_date_days?'':'s')+' ago';
                            }
                            else
                                t_date_str = t_date_hours+' hour'+(1==t_date_hours?'':'s')+' ago';
                        }
                        else
                            t_date_str = t_date_minutes+' minute'+(1==t_date_minutes?'':'s')+' ago';
                    }
                    else
                        t_date_str = t_date_seconds+' second'+(1==t_date_seconds?'':'s')+' ago';
                    var t_message =
                        '<li'+(i+1==t_tweets.length?' class="last"':'')+'>'+
                            linkify(t_tweets[i].text)+
                            '<span class="date">'+
                                t_date_str+
                            '</span>'+
                        '</li>';
                    t_container.append(t_message);
                }
                load_twitter_rotator();
            });
        });
    };
    
    var load_twitter_rotator = function(){
        var t_interval = 6000;   //time for tweet rotation in miliseconds
        var t_time = 1000;   //time for fade effect in miliseconds; NOTE: must be equal or lower then t_interval
        var t_active_class = 'active';
        var t_active_selector = '.'+t_active_class;
        var t_items = $('.rs_twitter ul li');
        var t_current = 0;
        var t_max = t_items.length;
        var t_height = 0;
        t_items.each(function(){
            t_height = Math.max(t_height,$(this).outerHeight(true));
        });
        $('.rs_twitter').css({height:t_height});
        t_items.filter(':first').addClass('active').css({opacity:1});
        if(t_max){
			t_max--;
            setInterval(function(){
                t_items.filter(':eq('+t_current+')').removeClass(t_active_class).stop().animate({opacity:0},{duration:t_time,queue:false});
                t_current = (t_current<t_max)?t_current+1:0;
                t_items.filter(':eq('+t_current+')').addClass(t_active_class).stop().animate({opacity:1},{duration:t_time,queue:false});
            },t_interval);
		}
    };
})();
