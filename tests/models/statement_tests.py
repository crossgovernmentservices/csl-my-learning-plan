import sys
import os
import json
import unittest

sys.path.append(os.path.join('..', '..'))
from application.modules.models import *

class StatementTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_property_actor_set_with_string(self):
        sut_statement = Statement()
        sut_statement.actor = 'test@email.com'

        self.assertEqual('test@email.com', sut_statement.actor)


    def test_property_actor_set_with_json(self):
        sut_statement = Statement()
        sut_statement.actor = {
            'objectType': 'Agent',
            'mbox': 'mailto:test@email.com'
        }
        self.assertEqual('test@email.com', sut_statement.actor)


    def test_property_verb_set_with_string(self):
        sut_statement = Statement()
        sut_statement.verb = 'read'

        expected_verb = Statement.create_verb('read')
        self.assertEqual(expected_verb, sut_statement.verb)

    def test_property_verb_set_with_json(self):
        sut_statement = Statement()
        sut_statement.verb = {
            'id': 'http://activitystrea.ms/schema/1.0/complete',
            'display': {'en': 'complete'}
        }

        expected_verb = Statement.create_verb('complete')
        self.assertEqual(expected_verb, sut_statement.verb)


    def test_create_verb(self):
        sut_statement = Statement(verb=Statement.create_verb('plan'))
        self.assertEqual('planned', sut_statement.get_verb_display_name())

    def test_create_verb_with_custom_name(self):
        sut_statement = Statement(verb=Statement.create_verb('plan', 'test_name'))
        self.assertEqual('test_name', sut_statement.get_verb_display_name())


    def test_to_json_for_simple_activity(self):
        with open('../data/statement-activity.json') as expected_activity:
            expected_json = json.load(expected_activity)
        sut_statement = Statement()
        sut_statement.actor = 'test@email.com'
        sut_statement.verb = 'read'
        sut_statement.statement_obj = Statement.create_activity_obj(
            uri='http://www.someurl.com',
            name='Some website')
        
        self.maxDiff = None
        self.assertEqual(expected_json, sut_statement.to_json())

    def test_to_json_for_plan_with_substatement(self):
        with open('../data/statement-plan.json') as expected_activity:
            expected_json = json.load(expected_activity)
        sut_statement = Statement()
        sut_statement.actor = 'planner@test.com'
        sut_statement.verb = 'plan'
        sut_statement.statement_obj = Statement.create_substatement_obj(
            Statement(
                actor='test@email.com',
                verb='read',
                statement_obj=Statement.create_activity_obj(
                    uri='http://www.someurl.com',
                    name='Some website')))

        self.maxDiff = None
        self.assertEqual(expected_json, sut_statement.to_json())


if __name__ == '__main__':
    unittest.main()
