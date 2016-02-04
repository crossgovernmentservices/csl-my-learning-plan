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

digitaldiagnostic = Blueprint('digitaldiagnostic', __name__)


@digitaldiagnostic.route('/digital-diagnostic')
@login_required
def intro():
    return render_template('digitaldiagnostic/intro.html')

@digitaldiagnostic.route('/digital-diagnostic/start')
@login_required
def start():
    return redirect(url_for('digitaldiagnostic.question'))

@digitaldiagnostic.route('/digital-diagnostic/question', methods=['GET', 'POST'])
@login_required
def question():
    return render_template('/digitaldiagnostic/question.html')
