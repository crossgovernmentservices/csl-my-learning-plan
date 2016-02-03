(function($, root) {
  "use strict";
  root.GOVUK = root.GOVUK || {};
  GOVUK.Modules = GOVUK.Modules || {};

  GOVUK.modules = {
    find: function(container) {
      var modules,
          moduleSelector = '[data-module]',
          container = container || $('body');

      modules = container.find(moduleSelector);

      // Container could be a module too
      if (container.is(moduleSelector)) {
        modules = modules.add(container);
      }

      return modules;
    },

    start: function(container) {
      var modules = this.find(container);

      for (var i = 0, l = modules.length; i < l; i++) {
        var module,
            element = $(modules[i]),
            type = camelCaseAndCapitalise(element.data('module')),
            started = element.data('module-started');

        if (typeof GOVUK.Modules[type] === "function" && !started) {
          module = new GOVUK.Modules[type]();
          module.start(element);
          element.data('module-started', true);
        }
      }

      // eg selectable-table to SelectableTable
      function camelCaseAndCapitalise(string) {
        return capitaliseFirstLetter(camelCase(string));
      }

      // http://stackoverflow.com/questions/6660977/convert-hyphens-to-camel-case-camelcase
      function camelCase(string) {
        return string.replace(/-([a-z])/g, function (g) {
          return g[1].toUpperCase();
        });
      }

      // http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
      function capitaliseFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
      }
    }
  }
})(jQuery, window);


(function(Modules) {
  "use strict";

  Modules.Disclosure = function() {

    this.start = function($element) {

      // Get all of the disclosure buttons
      var $buttons = $element.find('.js-toggle-disclosure button');

      // Set all subsections to be closed initially
      var $subsections = $buttons.closest('.subsection');
      $subsections.addClass('js-subsection-closed');

      // Get the open/close all button
      var $openOrCloseAll = $element.find('.js-open-close');

      // Open all
      function openAll() {
        $buttons.each(function() {
          var $button = $(this);
          var target = $button.attr('aria-controls');
          var $target = $('#' + target);
          var $subsection = $button.closest('.subsection');

          $target.removeAttr('class','if-js-hide');

          $target.attr('aria-hidden', 'false');
          $button.attr('aria-expanded', 'true');

          $subsection.removeClass('js-subsection-closed');
          $subsection.addClass('js-subsection-open');
        });
      }

      // Close all
      function closeAll() {
        $buttons.each(function() {
          var $button = $(this);
          var target = $button.attr('aria-controls');
          var $target = $('#' + target);
          var $subsection = $button.closest('.subsection');

          $target.attr('class','if-js-hide');
          $target.attr('aria-hidden', 'true');

          $button.attr('aria-expanded', 'false');

          $subsection.removeClass('js-subsection-open');
          $subsection.addClass('js-subsection-closed');
        });
      }

      // Find out the state of open or closed
      // If text is open all, open all
      $openOrCloseAll.on('click', openOrCloseAll);

      function openOrCloseAll() {

        var openOrCloseText = $openOrCloseAll.text();

        if (openOrCloseText == "Open all") {
          openAll();
          openOrCloseText = "Close all";
          $openOrCloseAll.text(openOrCloseText);
        }
        else {
          closeAll();
          openOrCloseText = "Open all";
          $openOrCloseAll.text(openOrCloseText);
        }

        // Set focus back to the button?
        $openOrCloseAll.focus();

      }

      // For each of the disclosure buttons
      $buttons.each(function() {

        // Save the button
        var $button = $(this);

        // Save the button target
        var target = $button.attr('aria-controls');
        var $target = $('#' + target);

        var $subsection = $button.closest('.subsection');

        // On click, toggle
        $button.on('click', toggle);

        function toggle() {
          var buttonState = $button.attr('aria-expanded');
          var targetState = $target.attr('aria-hidden');
          // console.log("Initial state: button aria-expanded="+buttonState+" target aria-hidden="+targetState);
          $target.toggleClass('if-js-hide');
          setAriaAttr();
          setSubsectionState();
        }

        function setAriaAttr() {
          if ($target.attr("aria-hidden") == "true") {
            $target.attr("aria-hidden", "false");
            $button.attr("aria-expanded", "true");
          }
          else {
            $target.attr("aria-hidden", "true");
            $button.attr("aria-expanded", "false");
          }
        }

        // Set the open or closed state
        function setSubsectionState() {
          if ($target.attr("aria-hidden") == "true") {
            $subsection.removeClass('js-subsection-open');
            $subsection.addClass('js-subsection-closed');
          }
          else {
            $subsection.removeClass('js-subsection-closed');
            $subsection.addClass('js-subsection-open');
          }
        }

      });

    }

  };
})(window.GOVUK.Modules);



$(document).ready(function(){
  console.log('starting GDS modules');
  GOVUK.modules.start();
});
