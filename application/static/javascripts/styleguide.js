;(function($) {
  "use strict";

  $(function() {

    // would cause issues if multiple flat-tab sections on page
    var $tabPanes = $( ".tab-pane ");
    $(".flat-tabs").on("click", "li", function() {
      var $me = $( this );

      $me.parents(".flat-tabs").find("li").removeClass("active").filter( $me ).addClass("active");
      $tabPanes.hide().filter( "#" + $me.data("tab-pane" ) ).show();
      return false;
    });
    $(".flat-tabs li.active").trigger("click");

    // for accordian course listings on profile
    $(".accordion-head").on("click", function() {
      console.log(this)
      $( this ).parent(".accordion").toggleClass("accordion--open");
    });

  });

}(jQuery));
