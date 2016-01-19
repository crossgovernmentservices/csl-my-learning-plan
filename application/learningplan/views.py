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


learningplan = Blueprint('learningplan', __name__, url_prefix='/learning-plan')


@learningplan.route('/<plan_id>')
@login_required
def view_plan(plan_id):
    return render_template('learningplan/view_plan.html', plan_id=plan_id)

