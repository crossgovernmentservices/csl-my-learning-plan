import json
import logging
import math
from application.config import Config

import application.modules.lr_service as lr_service
import application.modules.system_recommendations as rec_service
import application.modules.dates as mls_dates
from application.modules.system_recommendations import BasisItem, RecommendationBasis
from application.modules.models import Question


QUESTIONS_DATA_FILEPATH = 'application/data/diagnostic-questions.json'
RESOURCES_DATA_FILEPATH = 'application/data/diagnostic-resources.json'

_SKILL_RATING = {
    1: "an awareness level",
    2: "an awareness level",
    3: "a working level",
    4: "a practitioner level",
    5: "an expert level"
}

_EDU_FRAMEWORK = 'Civil Service Digital Skills Framework'
_AREAS_DATA = [
    {
        'name': 'ProblemSolving',
        'title': 'Problem solving',
        'url': 'https://civilservicelearning.civilservice.gov.uk/digitalskillsf'
    },
    {
        'name': 'Communications',
        'title': 'Communicating',
        'url': 'https://civilservicelearning.civilservice.gov.uk/digitalskillsf'
    }
]

logger = logging.getLogger()

def get_questions_json():
    return _load_json_file(QUESTIONS_DATA_FILEPATH)

def get_resources_json():
    return _load_json_file(RESOURCES_DATA_FILEPATH)
   
def get_all_questions():
    return [Question.from_dict(q) for q in get_questions_json()]

def get_recommendations(answers):
    rule = Config.DGN_RULE
    basisItems = _transform_to_basis_items(answers)
    recBasis = RecommendationBasis(rule, basisItems)
    potential_resources = _get_resources_data()
    
    raw_recs = rec_service.recommend_resources(recBasis, potential_resources)
    return _transform_to_recommendations(raw_recs)


def _transform_to_basis_items(answers_dict):
    return [BasisItem('all', _EDU_FRAMEWORK, '%s#%s#%s' % (_get_framework_area(answer_key).get('url'), answer_key,json.loads(answers_dict.get(answer_key)).get('score')))
        for answer_key in answers_dict]

def _transform_to_recommendations(raw_recs):
    # for now we are using only 1 framework
    recommendations = raw_recs[0]

    for area in recommendations['areas']:
        area_info = _get_framework_area(area.get('name'))
        area['title'] = area_info.get('title')
        area['levelName'] = _SKILL_RATING[area.get('level')]

    return recommendations

def _get_framework_area(name):
    return next(area for area in _AREAS_DATA if area.get('name').lower() == name.lower())

def _get_resources_data():
    for i in lr_service.get_resources_with_tincanstatements():
        yield i

def _load_json_file(filepath):
    with open(filepath) as data_file:
        questions = json.load(data_file)
    return questions



