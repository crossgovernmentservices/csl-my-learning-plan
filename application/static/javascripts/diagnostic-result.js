;(function($, win) {
  "use strict";

  
  $(".js-item-toggle").on("click", function(){
    var $this = $(this);
    var parentRow = $this.closest("tr");

    if($this.hasClass("js-added")){
      parentRow.removeClass("js-selected-res");
      parentRow.find(".js-plan-message").text("");
      $this.text("add to plan");
      $this.removeClass("js-added");
      
    } else {
      parentRow.addClass("js-selected-res");
      parentRow.find(".js-plan-message").text("added to plan");
      $this.text("remove from plan");
      $this.addClass("js-added");
    }

    event.preventDefault();
  });

  $(".js-continue").on("click", function(){
    var payload = [];

    $(".js-selected-res").each(function(idx, tableRow){
      var $tableRow = $(tableRow);
      var planItem = {
        url: $(tableRow).data("url"),
        title: $(tableRow).data("title"),
        duration: $(tableRow).data("duration"),
        type: $(tableRow).data("type"),
        required: $(tableRow).data("required"),
        tincan: $(tableRow).data("tincan-data")
      };
      payload.push(planItem);
    });

    $.ajax({
      url: redirect_url,
      type: 'POST',
      data : JSON.stringify(payload),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      success: function(data, textStatus, jqXHR){
        console.log("success");
        console.log(data);
        // win.location = "/learning-plan";
      },
      error: function(jqXHR, textStatus, errorThrown){
        console.error(errorThrown);
        console.error(jqXHR);
        console.error(jqXHR.responseText);
        var $jsInfoPanel = $(".js-info-panel");
        $jsInfoPanel.removeClass("visually-hidden");
        $jsInfoPanel.removeClass("success-summary");
        $jsInfoPanel.html("Oops that's embarrassing (see browser logs): "+errorThrown);
      }
    });

  });



}(jQuery, window));