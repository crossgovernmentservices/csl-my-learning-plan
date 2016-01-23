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

import application.modules.lr_service as lr_service


learningresource = Blueprint('learningresource', __name__)

@learningresource.route('/learning-resource/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        # uncomment if JS version goes tits up
        
        # courses = lr_service.get_all_courses()
        # return render_template('learningresource/search.html', courses=courses)
        return render_template('learningresource/search.html')


    if request.method == 'POST':
        current_app.logger.info(request.data)
        
        filterJson = request.get_json()
        courses = lr_service.get_courses(filterJson)

        current_app.logger.info(json.dumps(courses))
        return json.dumps(courses)

