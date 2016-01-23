(function($, root) {
  "use strict";
  root.GOVUK = root.GOVUK || {};
  GOVUK.CSL = GOVUK.CSL || {};

  var CourseSearch = function(inputElemsSelector) {
    this.$inputElems = $(inputElemsSelector);
    this.that = this;
  };

  CourseSearch.prototype = {
    registerOnEvent: function(elmsSelector, eventName){
      var that = this;
      var $elms = $(elmsSelector);
      $elms.on(eventName, function(){
        var payload = { 'filter': that._getFilterString() };

        that.runQuery(payload);
        event.preventDefault();
      });
    },

    runQuery: function(filterJson){
      var that = this;

      $.ajax({
        type: 'POST',
        data : JSON.stringify(filterJson),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(data, textStatus, jqXHR){
          console.log(filterJson);
          console.log(data);
          that.renderCourses(data);
          that.updateStatusLabels(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
          console.error(errorThrown);
          $('.js-error').text(errorThrown);
        }
      });
    },

    renderCourses: function(courses){
      var that = this;
      var $listElem = $('.js-courses-list');
      $listElem.children().remove();

      $.each(courses, function(cIdx, course){
        $listElem.append(that._generateCourseItemHTML(course));
      });
    },

    updateStatusLabels: function(courses){
      $('.js-courses-count').text(courses.length);
    },

    _getFilterString: function(){
      return this.$inputElems.val();
    },

    _generateCourseItemHTML: function(course){
      return $('<li/>', { 'class': 'course-result' }).html([
          $('<div/>',{ 'class': 'grid-row course-result__meta' }).html([
            $('<div/>',{ 'class': 'column-two-thirds' }).html(
              (course.type=='face2face')?
              [
                $('<i/>', { 'class': 'fa fa-book' }),
                $('<span/>').text('Workshop')
              ]:[
                $('<i/>', { 'class': 'fa fa-laptop' }),
                $('<span/>').text('e-learning')
              ]),
            $('<div/>', { 'class': 'column-third ta-right'}).html(
              $('<span/>').text(course.duration ? course.duration : '1 hr')
            )
          ]),

          $('<h3/>', { 'class': 'heading-small course-result__title'}).html(
            $('<a/>', { 'href': course.url }).text(course.title)
          ),

          $('<p/>', { 'class': 'text' }).text(course.desc),

          $('<ul/>', { 'class': 'skills' }).html(function(){
            return $.map(course.topics, function(topic, tIndex){
              return $('<li/>').text(topic);
            });
          })
        ]);
    }
  
  };

  GOVUK.CSL.CourseSearch = CourseSearch;
  var search = new CourseSearch('.js-course-search-input');
  search.registerOnEvent('.js-search-form', 'submit');



}(jQuery, window));
