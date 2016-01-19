from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request
)

from flask.ext.security import login_required
from flask.ext.login import current_user


learningrecord = Blueprint('learningrecord', __name__, url_prefix='/learning-record')


@learningrecord.route('/<record_id>')
@login_required
def view_record(record_id):
    return render_template('learningrecord/view_record.html', record_id=record_id)

