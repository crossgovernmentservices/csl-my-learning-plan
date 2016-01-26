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
      filterJson = filterJson || { 'filter': '' };

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
          console.error(jqXHR);
          console.error(jqXHR.responseText);
          var $jsInfoPanel = $(".js-info-panel");
          $jsInfoPanel.removeClass("visually-hidden");
          $jsInfoPanel.removeClass("success-summary");
          $jsInfoPanel.html("Oops that's embarrassing (see browser logs): "+errorThrown);
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

    parseISO08601Duration: function(iso8601Duration){
      var iso8601DurationRegex = /(-)?P(?:([\.,\d]+)Y)?(?:([\.,\d]+)M)?(?:([\.,\d]+)W)?(?:([\.,\d]+)D)?(?:T)?(?:([\.,\d]+)H)?(?:([\.,\d]+)M)?(?:([\.,\d]+)S)?/;
      var matches = iso8601Duration.match(iso8601DurationRegex);
      console.log(matches);
      console.log(iso8601Duration);
      return {
          sign: matches[1] === undefined ? '+' : '-',
          years: matches[2] === undefined ? 0 : matches[2],
          months: matches[3] === undefined ? 0 : matches[3],
          weeks: matches[4] === undefined ? 0 : matches[4],
          days: matches[5] === undefined ? 0 : matches[5],
          hours: matches[6] === undefined ? 0 : matches[6],
          minutes: matches[7] === undefined ? 0 : matches[7],
          seconds: matches[8] === undefined ? 0 : matches[8]
      };
    },

    formatISO08601Duration: function(dateTime){
      return dateTime.hours + " Hours " + dateTime.minutes + " Minutes ";
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
            $('<div/>',{ 'class': 'column-two-thirds' }).html(function(){
              if (course.type=='face2face')
                return [$('<i/>', { 'class': 'fa fa-book' }), $('<span/>').text('Workshop')]
              else if (course.type=='video')
                return [$('<i/>', { 'class': 'fa fa-youtube' }),$('<span/>').text('Video')]
              else if (course.type=='website')
                return [$('<i/>', { 'class': 'fa fa-firefox' }),$('<span/>').text('Web')]
              else if (course.type=='document')
                return [$('<i/>', { 'class': 'fa fa-file' }),$('<span/>').text('Document')]
              else
                return [$('<i/>', { 'class': 'fa fa-laptop' }),$('<span/>').text('e-Learning')];
              }),
            $('<div/>', { 'class': 'column-third ta-right'}).html(
              $('<span/>').text(course.duration ? this.formatISO08601Duration(this.parseISO08601Duration(course.duration)) : 'No time specified')
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

  // run on the page
  GOVUK.CSL.CourseSearch = CourseSearch;
  var search = new CourseSearch('.js-course-search-input');
  search.registerOnEvent('.js-search-form', 'submit');
  search.runQuery();


}(jQuery, window));
