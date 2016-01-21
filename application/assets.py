import os

from flask_assets import Bundle, Environment
from webassets.filter import get_filter

scss = get_filter('scss', as_output=True)

scss.load_paths = [os.path.join(os.path.dirname(__file__), 'static/sass'),
                   os.path.join(os.path.dirname(__file__),
                   'static/govuk_frontend_toolkit/stylesheets'),
                   os.path.join(os.path.dirname(__file__),
                   'static/govuk_elements/public/sass/elements')]


css_govuk_elements = Bundle(
    'sass/govuk_elements.scss',
    filters=scss,
    output='stylesheets/govuk_elements.css',
    depends=['/static/govuk_elements/public/sass/**/*.scss',
             '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']
)

css_internal_interface = Bundle(
    'sass/internal_interface.scss',
    filters=scss,
    output='stylesheets/internal_interface.css',
    depends=['/static/sass/internal_interface/**/*.scss',
             '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']
)

css_main = Bundle(
    'sass/main.scss',
    filters=scss,
    output='stylesheets/main.css',
    depends=['/static/sass/main/**/*.scss',
             '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']
)

css_learning = Bundle(
  'sass/learning.scss',
  filters='scss',
  output='stylesheets/learning.css',
  depends="**/*.scss"
)

css_rebrand = Bundle(
  'sass/rebrand/rebrand.scss',
  filters='scss',
  output='stylesheets/rebrand.css',
  depends='**/*.scss'
)

# js_rebrand = Bundle(
#     'sass/rebrand/js/rebrand.js',
#     filters='jsmin',
#     output='gen/js/rebrand.js'
# )

# js_booking = Bundle(
#     'sass/rebrand/js/booking.js',
#     filters='jsmin',
#     output='gen/js/booking.js'
# )

env = Environment()
env.register('css_govuk_elements', css_govuk_elements)
env.register('css_main', css_main)
env.register('css_internal_interface', css_internal_interface)
env.register('css_rebrand', css_rebrand)
env.register('css_learning', css_learning)
