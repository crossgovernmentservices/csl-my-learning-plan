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

import application.modules.lrs_service as lrs_service

learningplan = Blueprint('learningplan', __name__)


@learningplan.route('/learning-plan')
@login_required
def view_plan():
    learning_plan = lrs_service.get_user_learning_plan(current_user.email)
    return render_template('learningplan/view_plan.html', learning_plan=learning_plan)
