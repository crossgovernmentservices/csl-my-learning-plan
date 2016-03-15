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

css_csl_styleguide = Bundle(
    'sass/styleguide-csl.scss',
    filters='scss',
    output='stylesheets/styleguide-csl.css',
    depends='**/*.scss'
)

css_csl_elements = Bundle(
    'sass/csl_elements.scss',
    filters='scss',
    output='stylesheets/csl_elements.css',
    depends='**/*.scss'
)

css_learning_plan = Bundle(
    'sass/pages/learning_plan.scss',
    filters='scss',
    output='stylesheets/learning_plan.css',
    depends='**/*.scss'
)

css_learning_record = Bundle(
    'sass/pages/learning_record.scss',
    filters='scss',
    output='stylesheets/learning_record.css',
    depends='**/*.scss'
)

css_digital_diagnostic = Bundle(
    'sass/pages/digital_diagnostic.scss',
    filters='scss',
    output='stylesheets/digital_diagnostic.css',
    depends='**/*.scss'
)

css_learning_resource = Bundle(
    'sass/pages/learning_resource.scss',
    filters='scss',
    output='stylesheets/learning_resource.css',
    depends='**/*.scss'
)

env = Environment()
env.register('css_govuk_elements', css_govuk_elements)
env.register('css_main', css_main)
env.register('css_internal_interface', css_internal_interface)
env.register('css_rebrand', css_rebrand)
env.register('css_learning', css_learning)
env.register('css_csl_styleguide', css_csl_styleguide)
env.register('css_csl_elements', css_csl_elements)
env.register('css_learning_plan', css_learning_plan)
env.register('css_learning_record', css_learning_record)
env.register('css_digital_diagnostic', css_digital_diagnostic)
env.register('css_learning_resource', css_learning_resource)
