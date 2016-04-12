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

from flask.ext.security import login_required
from flask.ext.login import current_user

import application.modules.openlrs_service as lrs_service


learningrecord = Blueprint('learningrecord', __name__)

@learningrecord.route('/learning-record')
@login_required
def view_record():
    records = lrs_service.load_user_records(current_user.email)
    return render_template('learningrecord/view_record.html', records=records)


@learningrecord.route('/learning-record/clean-all-records')
@login_required
def clean_all():
    records = lrs_service.clean_learning_plans(current_user.email)
    back_url = url_for('learningrecord.view_record')
    return render_template('learningrecord/clean.html', back_url=back_url)


# API stuff here
@learningrecord.route('/api/learning-record/json')
@login_required
def view_record_json():
    records = lrs_service.load_user_records(current_user.email)
    return jsonify(records=records)


@learningrecord.route('/api/learning-record/clean_learning_record')
@login_required
def api_clean_learning_record():
    return jsonify(result=lrs_service.clean_learning_record(current_user.email))
