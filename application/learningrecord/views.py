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

import application.modules.lrs_service as lrs_service


learningrecord = Blueprint('learningrecord', __name__)

@learningrecord.route('/learning-record')
@login_required
def view_record():
    records = lrs_service.load_user_records(current_user.email)

    return render_template('learningrecord/view_record.html', records=records)


# JSON stuff here
@learningrecord.route('/learning-record/json')
@login_required
def view_record_json():
    records = lrs_service.load_user_records(current_user.email)
    return jsonify(records=records)
