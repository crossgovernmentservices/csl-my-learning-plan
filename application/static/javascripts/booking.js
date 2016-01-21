;(function($) {
  "use strict";

  var QueryString = function () {
    // This function is anonymous, is executed immediately and 
    // the return value is assigned to QueryString!
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
      var pair = vars[i].split("=");
          // If first entry with this name
      if (typeof query_string[pair[0]] === "undefined") {
        query_string[pair[0]] = decodeURIComponent(pair[1]);
          // If second entry with this name
      } else if (typeof query_string[pair[0]] === "string") {
        var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
        query_string[pair[0]] = arr;
          // If third or later entry with this name
      } else {
        query_string[pair[0]].push(decodeURIComponent(pair[1]));
      }
    }
    return query_string;
  }();

  $(function() {
    var $courses = $(".course-result");
    var $search__input = $(".top-search form .search__input");

    var displayResults = function(searchTerm) {
      var searchTerm = searchTerm || "";

      // should normalise case, take it out of the equation
      var numOfResults = $courses
        .hide()
        .filter(function(ind, el) {
            var listingText = $(el).text().toLowerCase();
            return listingText.indexOf( searchTerm.toLowerCase() ) !== -1; 
          })
          .show().length;
        $(".numofresults").text(numOfResults);
    };

    $(".top-search form").on("submit", function() {
      var term = $( this ).find(".search__input").val();
      displayResults( term );
      return false;
    });

    var init = function() {
      if ( QueryString.q !== "" ) {
        $search__input.val( QueryString.q );
        displayResults( QueryString.q );
      }
    }();

});

}(jQuery));