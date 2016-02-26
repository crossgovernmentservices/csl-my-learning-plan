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
from application.modules.models import Statement

learningplan = Blueprint('learningplan', __name__)


@learningplan.route('/learning-plan')
@login_required
def view_plan():
    learning_plan = lrs_service.get_user_learning_plan(current_user.email)
    # diagnostic_plan = next((plan for plan in learning_plan if plan.get('addedBy') == "diagnostic"), None)

    return render_template('learningplan/view_plan.html', learning_plan=learning_plan, diagnostic_plan=None)

@learningplan.route('/learning-plan/assign', methods=['POST'])
@login_required
def assign_learning_plan():

    post_data = json.loads(request.data.decode('utf-8'))

    # this is only for current user for now
    learner_email = current_user.email
    learning_plan = Statement.create_plan(plan_name='Actions from diagnostic', learner_actor=learner_email)

    for resource in post_data:
        # replace this horrible replace here!
        tincan_data = json.loads(resource.get('tincan', '{}').replace('\'', '\"'))
        verb = tincan_data.get('verb') or 'read'
        statement_obj = tincan_data.get('object') or Statement.create_activity_obj(
            uri=resource.get('url'),
            name=resource.get('title'))
        planned_item = Statement(verb=verb, statement_obj=statement_obj)
        learning_plan.add_planned_item(planned_item)


    # lrs_service.save_to_json(learner_email, post_data)
    lrs_result = lrs_service.save_learning_plan(learning_plan)

    return json.dumps({
            'postData': post_data,
            'plan': learning_plan.to_json(),
            'lrsResult': lrs_result
        })

@learningplan.route('/learning-plan/remove')
@login_required
def remove_learning_plan():
    return lrs_service.remove_json()


@learningplan.route('/learning-plan/api/load_learning_plans')
@login_required
def api_load_learning_plans():
    return json.dumps(lrs_service.load_learning_plans(current_user.email))
