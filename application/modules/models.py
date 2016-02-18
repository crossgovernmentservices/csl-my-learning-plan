# added here as the other models imports flasks etc
import json
import uuid
from copy import deepcopy

class Statement:
    VERBS = {
        'read': {
            'id': 'http://activitystrea.ms/schema/1.0/read',
            'display': {'en': 'read'}
        },
        'complete': {
            'id': 'http://activitystrea.ms/schema/1.0/complete',
            'display': {'en': 'complete'}
        },
        'plan': {
            'id': 'http://www.tincanapi.co.uk/verbs/planned_learning',
            'display': {'en': 'planned'}
        },
        'enroll': {
            'id': 'http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan',
            'display': {'en': 'enrolled onto plan'}
        }
    }

    def __init__(self, actor=None, verb=None, statement_obj=None):
        self._actor = None
        self.actor = actor
        self._verb = None
        self.verb = verb
        self._statement_obj = None
        self.statement_obj = statement_obj
        self._uuid = uuid.uuid1()

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, actor):
        if type(actor) is dict:
            self._actor = actor.get('mbox').replace('mailto:', '')
        else:
            self._actor = actor

    @property
    def verb(self):
        return self._verb

    @verb.setter
    def verb(self, verb):
        if verb is not None:
            if type(verb) is dict:
                self._verb = verb
            else:
                self._verb = Statement.create_verb(verb)

    def get_verb_display_name(self):
        return self.verb.get('display').get('en')


    @property
    def statement_obj(self):
        return self._statement_obj

    @statement_obj.setter
    def statement_obj(self, statement_obj):
        if statement_obj is not None:
            if type(statement_obj) is dict:
                self._statement_obj = statement_obj
            else:
                self._statement_obj = Statement.create_substatement_obj(statement_obj)

    def get_statement_obj_display_name(self):
        return self.statement_obj.get('definition').get('name').get('en')

    # @property
    # def has_substatement(self):
    #     return self.statement_obj.get('objectType') == 'SubStatement'


    def to_json(self):
        return {
            'actor': self._actor_to_json(),
            'verb': self._verb_to_json(),
            'object': self._statement_obj_to_json()
        }

    def _actor_to_json(self):
        return {
            'objectType': 'Agent',
            'mbox': 'mailto:%s' % self._actor
        }

    def _verb_to_json(self):
        return self.verb

    def _statement_obj_to_json(self):
        if type(self.statement_obj) is Statement:
            result_json = self.statement_obj.to_json()
            result_json['objectType'] = 'SubStatement'
            return result_json
        else:
            result_json = self.statement_obj
            result_json['objectType'] = 'Activity'
            return result_json


    @classmethod
    def create_verb(cls, verb_key, name=None):
        if name:
            verb = deepcopy(Statement.VERBS[verb_key])
            verb['display']['en'] = name
            return verb
        else:
            return Statement.VERBS[verb_key]

    @classmethod
    def create_activity_obj(cls, uri, name):
        return {
            'id': uri,
            'definition': {
                'name': {
                    'en': name
                }
            }
        }

    @classmethod
    def create_substatement_obj(cls, statement):
        # substatemetn_obj = statement.to_json()
        # substatemetn_obj['objectType'] = 'SubStatement'
        return statement





    @classmethod
    def from_dict(cls, json_dict):
        return cls(**json_dict)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return from_dict(json_dict)


