import json
import logging
import math
from application.config import Config

import application.modules.lr_service as lr_service
import application.modules.system_recommendations as rec_service
from application.modules.system_recommendations import BasisItem, RecommendationBasis


QUESTIONS_DATA_FILEPATH = 'application/data/diagnostic-questions.json'
RESOURCES_DATA_FILEPATH = 'application/data/diagnostic-resources.json'

_SKILL_RATING = {
    1: "Inadequate",
    2: "Fair",
    3: "Moderate",
    4: "Good",
    5: "Excellent"
}

_EDU_FRAMEWORK = 'Civil Service Skills and Knowledge Framework'
_AREAS_DATA = [
    {
        'name': 'ProblemSolving',
        'title': 'Problem solving',
        'url': 'https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf'
    },
    {
        'name': 'Communications',
        'title': 'Communicating',
        'url': 'https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf'
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
    for i in lr_service.get_resources():
        yield i

def _load_json_file(filepath):
    with open(filepath) as data_file:
        questions = json.load(data_file)
    return questions


class Question:
    def __init__(self, title, tag, description, guide, multichoice, choices, answer=None):
        self.title = title
        self.tag = tag
        self.description = description
        self.guide = guide
        self.is_multichoice = multichoice
        self.choices = choices
        self.answer = answer

    def get_score(self):
        score = 0
        if self.answer:
            if self.is_multichoice:
                score = math.ceil((len(self.answer)/len(self.choices)) * 5)
            else:
                # we don't have option weight so we've got to reverse scoring as 1st item is 0 but
                # it's actually the highes score at the moment - this will change
                score = math.ceil(5 - (int(self.answer.get(self.tag))/(len(self.choices)-1)) * 5)
        return score

    def get_choices_vals(self):
        return [(str(index), caption) for (index, caption) in enumerate(self.choices, start=0)]

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_dict(cls, json_dict):
        return cls(**json_dict)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return from_dict(json_dict)

