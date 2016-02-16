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
import application.models as Statement

learningplan = Blueprint('learningplan', __name__)


@learningplan.route('/learning-plan')
@login_required
def view_plan():
    learning_plan = lrs_service.get_user_learning_plan(current_user.email)
    return render_template('learningplan/view_plan.html', learning_plan=learning_plan)

@learningplan.route('/learning-plan/assign', methods=['POST'])
# @login_required
def assign_learning_plan():
    learner_email = json.loads(request.data.decode('utf-8')).get('email')
    # current_app.logger.info(learner_email)


    learning_plan = lrs_service.create_plan(learner_email)
    current_app.logger.info(learning_plan)





    result = lrs_service.post(learning_plan)
    current_app.logger.info(result)
    # return render_template('learningplan/view_plan.html', learning_plan=learning_plan)
    return json.dumps(result)
