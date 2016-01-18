var selectizeInit = function(data) {
    var items = data.map(function(x) { return { item: x }; });
    $('.input-tags').selectize({
      delimiter: ',',
      openOnFocus: false,
      closeAfterSelect: true,
      labelField: "item",
      valueField: "item",
      sortField: "item",
      searchField: "item",
      options: items,
      create: true
  });
};


var tagsInit = function() {
  $.ajax({
    url: '/my-log/tags.json',
    type: 'GET',
    success: function(data) {
      var tags = [];
      $.each(data.tags, function(i, tag) {
        tags.push(tag.name);
      });
      selectizeInit(tags);
    }
  });
};

$(document).ready(function() {
  tagsInit();
});
