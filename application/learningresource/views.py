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
import json

learningresource = Blueprint('learningresource', __name__)

@learningresource.route('/learning-resource/search')
@login_required
def search():

    with open('application/data/courses-for-search.json') as data_file:
        courses = json.load(data_file)
    return render_template('learningresource/search.html', courses=courses)

