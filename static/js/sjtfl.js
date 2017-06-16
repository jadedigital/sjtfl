$(function() {
		$('.socialtip').tooltip({ /*or use any other selector, class, ID*/
			placement: "bottom",
			trigger: "hover"
		});
} );

$(document).ready(function() {

  $(window).scroll(function () {  
      console.log($(window).scrollTop())
    if ($(window).scrollTop() > 80) {
      $('#navbar').addClass('navbar-fixed-top');
			var scores_width = $('#home-scores').width();
			$('#home-scores').width(scores_width);
			$('#home-scores').addClass('fix-scores');
    }
    if ($(window).scrollTop() < 80) {
      $('#navbar').removeClass('navbar-fixed-top');
			$('#home-scores').removeClass('fix-scores');
    }
  });
});

$(function() {
        $('#color').colorpicker();
    });