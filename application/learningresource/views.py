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
        filterJson = request.get_json()
        current_app.logger.info('getting items')
        try:
            courses = lr_service.get_courses(filterJson)    
        except Exception as e:
            current_app.logger.exception(e, exc_info=True)
        current_app.logger.info('got items')
        current_app.logger.info(json.dumps(courses))
        return json.dumps(courses)

