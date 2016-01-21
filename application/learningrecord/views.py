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

@learningrecord.route('/learning-record/<record_id>')
@login_required
def view_record(record_id):
    records = lrs_service.get_user_records(current_user.email)
    current_app.logger.info(records)

    return render_template('learningrecord/view_record.html', learning_records=records)


# JSON stuff here
@learningrecord.route('/learning-record/<record_id>/json')
@login_required
def view_record_json(record_id):
    records = lrs_service.get_user_records(current_user.email)
    return jsonify(records=records)
