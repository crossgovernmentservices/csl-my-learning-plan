from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    current_app,
    jsonify
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
        tincan_data = resource.get('tincan', '{}')
        verb = tincan_data.get('verb') or 'read'
        statement_obj = tincan_data.get('object') or Statement.create_activity_obj(
            uri=resource.get('url'),
            name=resource.get('title'))
        
        tincan_result = tincan_data.get('result')
        required = tincan_result.get('completion', resource.get('required'))
        duration = tincan_result.get('duration', resource.get('duration'))

        planned_item = Statement(
            verb=verb,
            statement_obj=statement_obj,
            required=required,
            duration=duration)

        learning_plan.add_planned_item(planned_item)

    lrs_result = lrs_service.save_learning_plan(learning_plan)

    resp = jsonify({
        'postData': post_data,
        'plan': learning_plan.to_json(),
        'lrsResult': lrs_result
    })
    resp.status_code = lrs_result.get('code', 200) if type(lrs_result) is dict else 200
    return resp



# API stuff
@learningplan.route('/learning-plan/api/load_learning_plans')
@login_required
def api_load_learning_plans():
    return json.dumps(lrs_service.load_learning_plans(current_user.email))

@learningplan.route('/learning-plan/api/load_learning_plan/<plan_id>')
@login_required
def api_load_learning_plan(plan_id):
    return json.dumps(lrs_service.load_learning_plan(plan_id))

@learningplan.route('/learning-plan/api/load_learning_plan_items/<plan_id>')
@login_required
def api_load_learning_plan_items(plan_id):
    return json.dumps(lrs_service.load_learning_plan_items(plan_id))

@learningplan.route('/learning-plan/api/load_learning_plan_item/<statement_id>')
@login_required
def api_load_learning_plan_item(statement_id):
    return json.dumps(lrs_service.load_learning_plan_item(statement_id))

@learningplan.route('/learning-plan/api/load_learning_plan_item_learning_records/<plan_item_id>')
@login_required
def api_load_learning_plan_item_learning_records(plan_item_id):
    return json.dumps(lrs_service.load_learning_plan_item_learning_records(current_user.email, plan_item_id))

