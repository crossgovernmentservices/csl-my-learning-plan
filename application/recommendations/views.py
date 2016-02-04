from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    current_app
)

import json

from flask.ext.security import login_required
from flask.ext.login import current_user

digitaldiagnostic = Blueprint('recommendations', __name__)
