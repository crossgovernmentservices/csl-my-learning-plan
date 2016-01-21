;(function($) {
  "use strict";

  var tabNavSelector = ".activity-navigation .tabs",
      tabContentClass = "tab-content",
      $tabContentCol;

  var switchTab = function( currentContentSel ) {
    var currentContentSel = currentContentSel || $( tabNavSelector ).find( ".current" ).data( "tab-section");

    // make correct tab current
    $( tabNavSelector )
      .find('a')
      .removeClass("current")
      .filter('[data-tab-section="'+ currentContentSel +'"]')
        .addClass('current');

    // show correct content
    $tabContentCol
      .hide()
      .filter("#" + currentContentSel )
        .show();

    // update hash, has legacy browser fallback
    // if(history.pushState) {
    //     history.pushState(null, null, "#" + currentContentSel);
    // }
    // else {
    //     location.hash = "#" + currentContentSel;
    // }
    // plus ARIA
  };

  $(function() {

    // close all but current tab or value of hash
    $tabContentCol = $( "." + tabContentClass );
    var currentContent = (window.location.hash) ? window.location.hash.substring(1) : undefined;
    switchTab(currentContent);

    // bind event handler
    $( tabNavSelector ).on('click', "a", function(){
      switchTab( $(this).data("tab-section") );
      return false;
    });

    // would cause issues if multiple flat-tab sections on page
    var $tabPanes = $( ".tab-pane ");
    $(".flat-tabs").on("click", "li", function() {
      var $me = $( this );

      $me.parents(".flat-tabs").find("li").removeClass("active").filter( $me ).addClass("active");
      $tabPanes.hide().filter( "#" + $me.data("tab-pane" ) ).show();
      return false;
    });
    $(".flat-tabs li.active").trigger("click");

    // mocking checking radio buttons
    $(".form-group").on("click", "input[type='radio']", function() {
      var $me = $( this );
      $me
        .parents(".form-group")
          .find("label")
          .removeClass("selected")
          .end()
        .end()
        .parent("label")
        .addClass("selected");
    });

    // for accordian course listings on profile
    $(".accordian-head").on("click", function() {
      $( this ).parent("li").toggleClass("accordian--open");
    });

    // for the search box on the profile
    $(".profile-search-form").on("submit", function(e) {
      var term = $( this ).find(".search__input").val();
      var url = window.location.origin + "/rebrand/search?q=" + term;
      window.location.href = url;
      e.preventDefault();
    });

    // for selecting a specific date
    $(".date-selection").on("click", function() {
      var $table = $( this ).parents(".course-select-table"),
          $row = $( this ).parents("tr");

      $table.find("tr").removeClass("currently-selected");
      $row.addClass("currently-selected");
      return false;
    })

  });

}(jQuery));
