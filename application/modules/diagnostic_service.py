import json
import logging
from application.config import Config

DATA_FILEPATH='application/data/diagnostic-questions.json'

logger = logging.getLogger()

def get_json():
    with open(DATA_FILEPATH) as data_file:
        questions = json.load(data_file)
    return questions

def get_all_questions():
    return [Question.from_dict(q) for q in get_json()]

class Question:
    def __init__(self, title, tag, description, guide, multichoice, choices, answer=None):
        self.title = title
        self.tag = tag
        self.description = description
        self.guide = guide
        self.is_multichoice = multichoice
        self.choices = choices
        self.answer = answer

    def get_choices_vals(self):
        return [(str(index), caption) for (index, caption) in enumerate(self.choices, start=1)]

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_dict(cls, json_dict):
        return cls(**json_dict)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return from_dict(json_dict)