from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    current_app,
    make_response
)

import json
import application.modules.diagnostic_service as dgn_service

from flask.ext.security import login_required
from flask.ext.login import current_user

import application.digitaldiagnostic.forms as dgn_forms


digitaldiagnostic = Blueprint('digitaldiagnostic', __name__)


@digitaldiagnostic.route('/digital-diagnostic')
@login_required
def intro():
    return render_template('digitaldiagnostic/intro.html')

@digitaldiagnostic.route('/digital-diagnostic/start')
@login_required
def start():
    resp = make_response(redirect(url_for('digitaldiagnostic.question', number=0)))
    resp.set_cookie('answers', '', expires=0)
    return resp

@digitaldiagnostic.route('/digital-diagnostic/question/<number>', methods=['GET', 'POST'])
@login_required
def question(number):
    questions = dgn_service.get_all_questions()

    questionNo = int(number or 0)
    questionNo = questionNo if questionNo<len(questions) else len(questions) -1

    current_question = questions[questionNo]
    cookie_answers = request.cookies.get('answers')
    
    if cookie_answers:
        cookie_json = json.loads(cookie_answers)
        current_answer = cookie_json.get(current_question.tag)
        current_question.answer = json.loads(current_answer) if current_answer else None
    else:
        cookie_json = {}

    if request.method == 'POST':
        current_app.logger.info(json.dumps(request.form))

        form = dgn_forms.generate_form_for(current_question)

        if (questionNo+1) < len(questions):
            redirect_url = url_for('digitaldiagnostic.question', number=questionNo+1)
        else:
            redirect_url = url_for('digitaldiagnostic.result')

        resp = make_response(redirect(redirect_url))
        # resp.set_cookie('answer-%i' % questionNo, json.dumps(request.form))
        cookie_json[current_question.tag] = json.dumps(request.form)
        resp.set_cookie('answers', json.dumps(cookie_json))
        return resp

    current_app.logger.info(cookie_json)
    current_app.logger.info(current_question.answer)
    # if cookie_answer: 
    #     current_question.answer = json.loads(cookie_answer)
    # current_app.logger.info(cookie_answer) 

    form = dgn_forms.generate_form_for(current_question)
    return render_template('/digitaldiagnostic/question.html', 
        form=form, questionNo=questionNo, question=current_question, question_count=len(questions))

@digitaldiagnostic.route('/digital-diagnostic/result')
@login_required
def result():
    return "nice, look at cookies :)"

@digitaldiagnostic.route('/digital-diagnostic/questions-json')
@login_required
def questions_json():
    return json.dumps(dgn_service.get_json())
