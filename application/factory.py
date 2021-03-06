# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
import logging
from flask import Flask, render_template
from flask.ext.security import Security

import application.modules.dates as mls_dates


def asset_path_context_processor():
    return {'asset_path': '/static/'}


def create_app(config_filename):
    ''' An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    '''
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_errorhandlers(app)
    register_blueprints(app)
    app.context_processor(asset_path_context_processor)
    register_extensions(app)
    register_filters(app)
    return app


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_blueprints(app):
    from application.mylearning.views import mylearning
    app.register_blueprint(mylearning)

    from application.profile.views import profile
    app.register_blueprint(profile)

    from application.learningrecord.views import learningrecord
    app.register_blueprint(learningrecord)

    from application.learningplan.views import learningplan
    app.register_blueprint(learningplan)

    from application.learningresource.views import learningresource
    app.register_blueprint(learningresource)

    from application.digitaldiagnostic.views import digitaldiagnostic
    app.register_blueprint(digitaldiagnostic)


def register_extensions(app):
    from application.assets import env
    env.init_app(app)

    from application.models import db
    db.init_app(app)

    # flask security setup
    from application.extensions import user_datastore
    Security(app, user_datastore)


def register_filters(app):
    logger = logging.getLogger()

    def format_duration(duration):
        try:
            return mls_dates.convert_duration(duration)
        except Exception as e:
            logger.exception('Error while formatting duration:' + str(e))
            return ''

    def format_date(date, format=None):
        try:
            return mls_dates.format_date(date, format)
        except Exception as e:
            logger.exception('Error while formatting:' + str(e))
            return ''

    app.jinja_env.filters['format_duration'] = format_duration
    app.jinja_env.filters['format_date'] = format_date
