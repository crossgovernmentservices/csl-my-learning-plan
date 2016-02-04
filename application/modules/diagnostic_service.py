import json
import logging
from application.config import Config

DATA_FILEPATH='application/data/diagnostic-questions.json'

logger = logging.getLogger()

def get_all_questions():
    with open(DATA_FILEPATH) as data_file:
        questions = json.load(data_file)
    return questions


class MyStuff(object):

    def __init__(self):
        self.tangerine = "And now a thousand years between"

    def apple(self):
        print "I AM CLASSY APPLES!"