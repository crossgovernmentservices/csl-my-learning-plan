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
      create: true,
      onChange: function(value) {
        console.log('onChange', value);
      },
      onItemAdd: function(value, $item) {
        currentInput = $item.parent().parent().prev();
        addTagToEntry(value, currentInput.data().entryId);
        $item.click(itemClicked);
      },
      onInitialize:  function() {
        $('.item').click(itemClicked);
      },
      onDelete: function(value) {
        console.log('onDelete', value);
        //TODO remove tag with name==value from entry
      }
  });
};

var addTagToEntry = function(tag, entryId) {
   $.ajax({
    url: '/my-log/entry/'+entryId+'/tags',
    type: 'POST',
    contentType: 'application/json',
    data:  JSON.stringify({"tag": tag}),
    success: function(data) {
      console.log('all done');
    }
  });
}

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

var itemClicked = function(event) {
    event.stopPropagation();
    var tagName = $(event.currentTarget).data().value;
    window.location = '/my-log?tag='+tagName;
};

$(document).ready(function() {
  tagsInit();
});
