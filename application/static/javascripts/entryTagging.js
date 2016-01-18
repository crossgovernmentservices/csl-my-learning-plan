var selectizeInit = function() {
    $('.input-tags').selectize({
      delimiter: ',',
      openOnFocus: false,
      closeAfterSelect: true,
      labelField: "item",
      valueField: "item",
      sortField: "item",
      searchField: "item",
      create: true,
      onChange: function(value) {
        console.log('onChange', value);
      },
      onItemAdd: function(value, $item) {
        console.log('onItemAdd', value);
      },
      onInitialize:  function() {
       console.log('onInitialize');
      },
      onDelete: function(value) {
        console.log('onDelete', value);
        //TODO remove tag with name==value from entry
      }
  });
};

var toggleEditable = function(event) {
  event.preventDefault();
  $('.selectize-control').toggle();
  $('.current-tags').toggle();
  $('.submit').toggle();
  $('.cancel-edit').toggle();
  $('.edit').toggle();
  $('.entry-content').toggle();
  $('.entry-content--edit').toggle();

};


$(document).ready(function() {
  selectizeInit();
  $('.selectize-control').hide();
  $('.edit').click(toggleEditable);
});
