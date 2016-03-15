from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    current_app,
    jsonify,
    make_response
)

from flask.ext.security import login_required
from flask.ext.login import current_user
import json

import application.modules.lr_service as lr_service
import application.modules.lrs_service as lrs_service
from application.modules.models import Question



learningresource = Blueprint('learningresource', __name__)

COOKIE_COURSE='learningcourse'

TYPE_PAGE='pages'
TYPE_QUESTION='questions'

@learningresource.route('/learning-resource/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        filterJson = request.get_json()
        current_app.logger.info(filterJson)
        current_app.logger.info(filterJson['filter'])
        current_app.logger.info(type(filterJson['filter']))

        current_app.logger.info('getting items')
        try:
            courses = lr_service.get_courses(filterJson)
        except Exception as e:
            current_app.logger.exception(e, exc_info=True)
            raise
        current_app.logger.info('got items')
        return json.dumps(courses)

    return render_template('learningresource/search.html')

@learningresource.route('/learning-resource/course/<resource_id>')
def view_resource(resource_id):
    course = lr_service.get_resource(resource_id)
    pre_course = lr_service.get_course_prerequisites(resource_id)

    if current_user.is_authenticated:
        course['learningRecord'] = lrs_service.load_course_learning_records(
            email=current_user.email,
            course_uri=url_for('learningresource.view_resource', resource_id=course['id'], _external=True))
        
        if pre_course:
            pre_course['learningRecord'] = lrs_service.load_course_learning_records(
                email=current_user.email,
                course_uri=url_for('learningresource.view_resource', resource_id=pre_course['id'], _external=True))


    return render_template('learningresource/view_resource.html', course=course, pre_course=pre_course, user_logged_in=current_user.is_authenticated)

@learningresource.route('/learning-resource/course/<resource_id>/start')
@login_required
def start(resource_id):
    resp = make_response(redirect(url_for('learningresource.view_course_page', resource_id=resource_id, res_type=TYPE_PAGE, number=0)))
    resp.set_cookie(COOKIE_COURSE, '', expires=0)
    return resp


@learningresource.route('/learning-resource/course/<resource_id>/<res_type>/<number>', methods=['GET', 'POST'])
@login_required
def view_course_page(resource_id, res_type, number):
    course = lr_service.get_resource(resource_id)
    page_number = int(number or 0)
    page_count = len(course['course'][res_type])
    current_page = course['course'][res_type][page_number]

    if res_type == TYPE_QUESTION:
        current_page = Question.from_dict(current_page)

    if request.method == 'POST':
        is_last = (page_number + 1) >= page_count
        if is_last:
            if res_type == TYPE_PAGE:
                res_type = TYPE_QUESTION
                page_number = 0
            elif res_type == TYPE_QUESTION:
                return redirect(url_for('learningresource.view_course_complete', resource_id=resource_id))
        else:
            page_number+=1

        redirect_url = url_for('learningresource.view_course_page', resource_id=resource_id, res_type=res_type, number=page_number)
        return redirect(redirect_url)


    return render_template('/learningresource/course_page.html',
        res_type=res_type, course=course, page_number=page_number, page=current_page, page_count=page_count)

@learningresource.route('/learning-resource/course/<resource_id>/success')
@login_required
def view_course_complete(resource_id):
    course = lr_service.get_resource(resource_id)
    # learning_record ??
    return render_template('/learningresource/course_result.html', course=course, learninig_record=None)



# API
@learningresource.route('/api/learning-resource/course/<resource_id>')
def api_view_resource(resource_id):
    course = lr_service.get_resource(resource_id)
    return jsonify(course)
