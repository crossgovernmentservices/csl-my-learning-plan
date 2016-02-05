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
            'educationalFramework': 'communication',
            'target': '5',
            'audience': 'all',
            'name': 'staff forums',
            'type': 'article',
            'duration': 'PT15M',
            'resourceUrl': 'http://test.com/item'
        },
        {
            'educationalFramework': 'communication',
            'target': '4',
            'audience': 'all',
            'name': 'thermomix scandal',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/thermo'
        },
        {
            'educationalFramework': 'communication',
            'target': '2',
            'audience': 'all',
            'name': 'onions',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/onions'
        },
        {
            'educationalFramework': 'communication',
            'target': '2',
            'audience': 'all',
            'name': 'sominkelse',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/sominkelse'
        },
        {
            'educationalFramework': 'communication',
            'target': '1',
            'audience': 'all',
            'name': 'somink else for dummies',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/sominkelsedummy'
        },
        {
            'educationalFramework': 'basicproblemsolving',
            'target': '4',
            'audience': 'all',
            'name': 'word for advanced',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/item4'
        },
        {
            'educationalFramework': 'basicproblemsolving',
            'target': '1',
            'audience': 'all',
            'name': 'word for dummies',
            'type': 'course',
            'duration': 'PT5M',
            'resourceUrl': 'http://test.com/item0'
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

    items = [ BasisItem('all', answer_key, json.loads(cookie_answers.get(answer_key)).get('score'))
        for answer_key in cookie_answers]

    basis = RecommendationBasis("dummypage", items)

    raw_reccomendations = rec_service.recommend_resources(basis, get_dummypage_data())
    current_app.logger.info(raw_reccomendations)

    page_data = {
        "communication": "Communicating",
        "basicproblemsolving": "Problem solving"
    }

    recommendations = [{
            "title": page_data.get(recommendation.get('educationalFramework')),
            "tag": recommendation.get('educationalFramework'),
            "recommendedItems": recommendation.get('recommendations')
        } 
        for recommendation in raw_reccomendations]

    current_app.logger.info(recommendations)

    return render_template('/digitaldiagnostic/result.html', 
        answers=cookie_answers, raw_reccomendations=raw_reccomendations, recommendations=recommendations)


@digitaldiagnostic.route('/digital-diagnostic/questions-json')
@login_required
def questions_json():
    return json.dumps(dgn_service.get_json())
