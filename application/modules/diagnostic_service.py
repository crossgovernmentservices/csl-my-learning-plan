import json
import logging
import math
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

