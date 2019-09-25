(function($) {
  "use strict"; // Start of use strict

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: (target.offset().top)
        }, 1000, "easeInOutExpo");
        return false;
      }
    }
  });

  // Closes responsive menu when a scroll trigger link is clicked
  $('.js-scroll-trigger').click(function() {
    $('.navbar-collapse').collapse('hide');
  });

  // Activate scrollspy to add active class to navbar items on scroll
  //$('body').scrollspy({
  //  target: '#sideNav'
 // });

})(jQuery); // End of use strict

/*
$(function () {
  $('#nate_refresh').click(function () {
      $.ajax({
          type: 'GET',
          url: '/second/index/naterefresh',
          data: {
          },
          dataType: 'json',
          success: function(content){
            console.log(content);
            var target = document.getElementById("nate_refresh");
            //target.innerHTML = "button was clicked"
            console.log(target.innerHTML);
            if(target.innerHTML === "button was clicked")
            {
              target.innerHTML = "nate_refresh";
            }
            else
            {
              target.innerHTML = "button was clicked";
            }
        },
        error: function(xhr, status, error) {
            alert(error);
        }  
        })
  });
});
*/