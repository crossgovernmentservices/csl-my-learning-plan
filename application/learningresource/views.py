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
from application.modules.models import *
from functools import reduce

learningresource = Blueprint('learningresource', __name__)

COOKIE_ANSWERS = 'courseanswers'

TYPE_PAGE = 'pages'
TYPE_QUESTION = 'questions'

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

    source_course = request.args.get('source')

    if current_user.is_authenticated:
        learning_records = lrs_service.load_course_learning_records(
            email=current_user.email,
            course_uri=url_for('.view_resource', resource_id=course['id'], _external=True))
        course['learningRecord'] = learning_records[0] if learning_records else None
        
        if pre_course:
            pre_learning_records = lrs_service.load_course_learning_records(
                email=current_user.email,
                course_uri=url_for('.view_resource', resource_id=pre_course['id'], _external=True))
            pre_course['learningRecord'] = pre_learning_records[0] if pre_learning_records else None


    return render_template('learningresource/view_resource.html',
        course=course, pre_course=pre_course, user_logged_in=current_user.is_authenticated, source_course=source_course)

@learningresource.route('/learning-resource/course/<resource_id>/start')
@login_required
def start(resource_id):
    resp = make_response(redirect(url_for('.view_course_page', 
        resource_id=resource_id, res_type=TYPE_PAGE, number=0, source=request.args.get('source'))))
    resp.set_cookie(COOKIE_ANSWERS, '', expires=0)
    return resp


@learningresource.route('/learning-resource/course/<resource_id>/<res_type>/<int:number>', methods=['GET', 'POST'])
@login_required
def view_course_page(resource_id, res_type, number):
    course = lr_service.get_resource(resource_id)
    page_number = number or 0
    page_count = len(course['course'][res_type])
    current_page = course['course'][res_type][page_number]
    source_course = request.args.get('source')


    if res_type == TYPE_QUESTION:
        current_page = Question.from_dict(current_page)

        if COOKIE_ANSWERS in request.cookies:
            cookie_answers = request.cookies.get(COOKIE_ANSWERS)
            current_app.logger.info(cookie_answers)

            cookie_json = json.loads(cookie_answers)
            current_answer = cookie_json.get(current_page.tag)

            current_page.answer = json.loads(current_answer).get('selected') if current_answer else None
        else:
            cookie_json = {}

    if request.method == 'POST':
        is_last = (page_number + 1) >= page_count
        if is_last:
            if res_type == TYPE_PAGE:
                res_type = TYPE_QUESTION
                page_number = 0
            elif res_type == TYPE_QUESTION:
                # clean this up !
                resp = make_response(redirect(url_for('.view_course_complete', resource_id=resource_id, source=source_course)))
                if type(current_page) is Question:
                    current_page.answer = request.form
                    # save cookies only if it's a question
                    cookie_json[current_page.tag] = json.dumps({
                        'selected': request.form,
                        'score': current_page.get_score()
                    })
                    resp.set_cookie(COOKIE_ANSWERS, json.dumps(cookie_json))
                return resp
        else:
            page_number+=1


        redirect_url = url_for('.view_course_page', resource_id=resource_id, res_type=res_type, number=page_number, source=source_course)
        resp = make_response(redirect(redirect_url))

        if type(current_page) is Question:
            current_page.answer = request.form
            # save cookies only if it's a question
            cookie_json[current_page.tag] = json.dumps({
                'selected': request.form,
                'score': current_page.get_score()
            })
            resp.set_cookie(COOKIE_ANSWERS, json.dumps(cookie_json))

        return resp


    return render_template('/learningresource/course_page.html',
        res_type=res_type, course=course, page_number=page_number, page=current_page, page_count=page_count, source_course=source_course)

@learningresource.route('/learning-resource/course/<resource_id>/complete')
@login_required
def view_course_complete(resource_id):
    course = lr_service.get_resource(resource_id)
    
    cookie_answers = json.loads(request.cookies.get(COOKIE_ANSWERS))
    source_course_id = request.args.get('source')
    source_course = lr_service.get_resource(source_course_id)

    final_score = reduce(lambda x, y: (json.loads(cookie_answers[x]).get('score', 0) + json.loads(cookie_answers[y]).get('score', 0)) / 2, cookie_answers)

    record = Statement(
        actor=current_user.email,
        verb='complete',
        statement_obj=Statement.create_activity_obj(
            uri=url_for('.view_resource', resource_id=resource_id, _external=True),
            name=course['title'],
            resource_type=course['type'])).to_json()

    record['result'] = {
        "score": {
            "min": 0,
            "max": 5,
            "raw": final_score
        }
    }

    lrs_result = lrs_service.save_statement(record)

    resp = make_response(redirect(url_for('.view_course_result', resource_id=resource_id, source=source_course_id)))
    resp.set_cookie(COOKIE_ANSWERS, '', expires=0)
    return resp

@learningresource.route('/learning-resource/course/<resource_id>/result')
@login_required
def view_course_result(resource_id):

    course = lr_service.get_resource(resource_id)
    record = lrs_service.load_course_learning_records(
        email=current_user.email,
        course_uri=url_for('.view_resource', resource_id=resource_id, _external=True))[0]

    source_course = lr_service.get_resource(request.args.get('source'))
    
    current_app.logger.info(record)

    return render_template('/learningresource/course_result.html', course=course, record=record, source_course=source_course)



# API
@learningresource.route('/api/learning-resource/course/<resource_id>')
def api_view_resource(resource_id):
    course = lr_service.get_resource(resource_id)
    return jsonify(course)
