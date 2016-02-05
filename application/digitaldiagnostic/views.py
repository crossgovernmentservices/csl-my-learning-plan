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
import application.modules.system_recommendations as rec_service
from application.modules.system_recommendations import BasisItem, RecommendationBasis


from flask.ext.security import login_required
from flask.ext.login import current_user

digitaldiagnostic = Blueprint('digitaldiagnostic', __name__)

def get_dummypage_data():
    data = [
        {
            'educationalFramework': '1to5',
            'audience': 'all',
            'targetUrl': '1to5:5',
            'resourceUrl': 'http://urlecho.appspot.com/echo?body=Target 5 resource'
        },
        {
            'educationalFramework': '1to5',
            'audience': 'all',
            'targetUrl': '1to5:4',
            'resourceUrl': 'http://urlecho.appspot.com/echo?body=Target 4 resource'
        },
        {
            'educationalFramework': '1to5',
            'audience': 'all',
            'targetUrl': '1to5:3',
            'resourceUrl': 'http://urlecho.appspot.com/echo?body=Target 3 resource'
        },
        {
            'educationalFramework': '1to5',
            'audience': 'all',
            'targetUrl': '1to5:2',
            'resourceUrl': 'http://urlecho.appspot.com/echo?body=Target 2 resource'
        }
    ]
    for i in data:
        yield i


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
    

    if 'answers' in request.cookies:
        cookie_answers = request.cookies.get('answers')
        current_app.logger.info(cookie_answers)
        
        cookie_json = json.loads(cookie_answers)
        current_answer = cookie_json.get(current_question.tag)

        current_question.answer = json.loads(current_answer).get('selected') if current_answer else None
    else:
        cookie_json = {}

    if request.method == 'POST':
        current_app.logger.info(json.dumps(request.form))
        current_question.answer = request.form
        if (questionNo+1) < len(questions):
            redirect_url = url_for('digitaldiagnostic.question', number=questionNo+1)
        else:
            redirect_url = url_for('digitaldiagnostic.result')

        resp = make_response(redirect(redirect_url))
        cookie_json[current_question.tag] = json.dumps({
            "selected": request.form,
            "score": current_question.get_score()
        })
        resp.set_cookie('answers', json.dumps(cookie_json))
        return resp

    current_app.logger.info(current_question.answer)
    return render_template('/digitaldiagnostic/question.html',
        questionNo=questionNo, question=current_question, question_count=len(questions))


@digitaldiagnostic.route('/digital-diagnostic/result')
@login_required
def result():
    cookie_answers = json.loads(request.cookies.get('answers'))

    items = [ BasisItem('all', '1to5', '1to5:%s' % json.loads(cookie_answers.get(answer_key)).get('score')) for answer_key in cookie_answers]
    basis = RecommendationBasis("1to5", items)

    recommendation = rec_service.recommend_resources(basis, get_dummypage_data())
    current_app.logger.info(recommendation)

    return render_template('/digitaldiagnostic/result.html', answers=cookie_answers, recommendation=recommendation)


@digitaldiagnostic.route('/digital-diagnostic/questions-json')
@login_required
def questions_json():
    return json.dumps(dgn_service.get_json())
