$(function() {
		$('.socialtip').tooltip({ /*or use any other selector, class, ID*/
			placement: "bottom",
			trigger: "hover"
		});
} );

$(document).ready(function() {
  $(window).load(function () {
    $('#banner-logo-wrapper').addClass('logo-fixed-top');      
  });

  $(window).scroll(function () {  
    if ($(window).scrollTop() > 80) {
      $('#banner').addClass('banner-fix');      
      $('#navbar').addClass('navbar-fixed-top');
      $('.banner-text').css({"display": "none"});
      $('#banner-logo-wrapper').css({"width": "inherit"});
      /*$('#banner-logo').addClass('logo-margin-fix');      
			var scores_width = $('#home-scores').width();
			$('#home-scores').width(scores_width);
			$('#home-scores').addClass('fix-scores');*/
    }
    if ($(window).scrollTop() < 80) {
      $('#banner').removeClass('banner-fix');
      $('#navbar').removeClass('navbar-fixed-top');
      $('.banner-text').css({"display": "inline"});
      $('#banner-logo-wrapper').css({"width": "70%"});
      /*$('#banner-logo').removeClass('logo-margin-fix');  
			$('#home-scores').removeClass('fix-scores');*/
    }
    var bannerTextColor = "255,255,255";//color attr for rgba
    var bannerHeight = $('#banner').height(); 
    var navbarHeight = $('#navbar').height();
    var bannerLogoHeight = 60; 
    
    var textOpacity = (1-($(window).scrollTop() / bannerHeight)); 
    var logoHeight = ((1-($(window).scrollTop() / (bannerHeight+navbarHeight)))*bannerLogoHeight); 

    if (textOpacity > 1) { textOpacity = 1; }
    if (textOpacity < 0 ) { textOpacity = 0; }
    if (logoHeight > 60) { logoHeight = 60; }
    if (logoHeight < 32 ) { logoHeight = 32; }
    var newBannerTextColor = 'rgba(' + bannerTextColor + ',' + textOpacity + ')';
    $('.banner-text').css({"color": newBannerTextColor});
    $('#banner-logo').css({"height": logoHeight});
  });
});


$(function() {
var selector = '.link-wrapper';

  $(selector).on('click', function(){
      $(selector).removeClass('active');
      $(this).addClass('active');
  });
});

$(function() {
        $('#color').colorpicker();
    });