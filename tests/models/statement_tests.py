import sys
import os
import json
import unittest

sys.path.append(os.path.join('..', '..'))
from application.modules.models import *

class StatementTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

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


    def test_create_activity_obj_string_type(self):
        sut_activity = Statement.create_activity_obj(
            uri='www.test.com',
            name='test name',
            resource_type='elearning')

        expected_obj = {
            'id': 'www.test.com',
            'definition': {
                'name': {
                    'en': 'test name'
                },
                'type': 'http://adlnet.gov/expapi/activities/course'
            }
        }

        self.assertEqual(expected_obj, sut_activity)


    def test_create_activity_obj_with_type(self):
        sut_activity = Statement.create_activity_obj(
            uri='www.test.com',
            name='test name',
            resource_type='http://activitystrea.ms/schema/1.0/offer')

        expected_obj = {
            'id': 'www.test.com',
            'definition': {
                'name': {
                    'en': 'test name'
                },
                'type': 'http://activitystrea.ms/schema/1.0/offer'
            }
        }

        self.assertEqual(expected_obj, sut_activity)



    # GROUPING
    def test_property_grouping_set_with_string(self):
        sut_statement = Statement()
        sut_statement.grouping = 'http://www.tincanapi.co.uk/wiki/learning_plan:1234-1234-1234-1234'

        self.assertEqual('http://www.tincanapi.co.uk/wiki/learning_plan:1234-1234-1234-1234', sut_statement.grouping)

    def test_property_grouping_set_with_json(self):
        sut_statement = Statement()
        sut_statement.grouping = {
            'objectType': 'Activity',
            'id': 'http://www.tincanapi.co.uk/wiki/learning_plan:1234-1234-1234-1234'
        }
        self.assertEqual('http://www.tincanapi.co.uk/wiki/learning_plan:1234-1234-1234-1234', sut_statement.grouping)


    # PLAN SPECIFIC
    def test_create_plan(self):
        sut_plan = Statement.create_plan('Test plan',
            learner_actor='learner@test-email.com',
            planner_actor='planner@test-email.com',
            verb_name='enrolled onto test plan')

        self.assertEqual('learner@test-email.com', sut_plan.actor)

        expected_verb = {
            'id': 'http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan',
            'display': {'en': 'enrolled onto test plan'}
        }
        self.assertEqual(expected_verb, sut_plan.verb)
        
        self.assertEqual('Test plan', sut_plan.get_statement_obj_display_name())
        self.assertIn('http://www.tincanapi.co.uk/wiki/learning_plan:', sut_plan.statement_obj.get('id'))


    def test_add_planned_item(self):
        sut_plan = Statement.create_plan(
            plan_name='Test plan',
            learner_actor='learner@test-email.com',
            planner_actor='planner@test-email.com')

        sut_plan.add_planned_item(Statement(
            actor='learner@test-email.com',
            verb='read',
            statement_obj=Statement.create_activity_obj(
                uri='http://www.someurl.com',
                name='Some website')))

        self.assertEqual(1, len(sut_plan.planned_items))
        sut_item = sut_plan.planned_items[0]
        self.assertEqual('learner@test-email.com', sut_item.actor)



    # JSON GENERATION
    def test_to_json_for_simple_activity(self):
        with open('../data/statement-activity.json') as expected_activity:
            expected_json = json.load(expected_activity)
        sut_statement = Statement()
        sut_statement.actor = 'test@email.com'
        sut_statement.verb = 'read'
        sut_statement.statement_obj = Statement.create_activity_obj(
            uri='http://www.someurl.com',
            name='Some website')
        
        self.assertEqual(expected_json, sut_statement.to_json())


    def test_to_json_for_planned_item(self):
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

        self.assertEqual(expected_json, sut_statement.to_json())


    def test_to_json_for_learning_plan(self):
        sut_plan = Statement.create_plan(
            plan_name='Test plan',
            learner_actor='learner@test-email.com',
            verb_name='test enrollment')

        sut_plan.add_planned_item(Statement(
            actor='test-1@email.com',
            verb=Statement.create_verb('read', 'read test'),
            statement_obj=Statement.create_activity_obj(
                uri='http://www.someurl-1.com',
                name='Some website - 1'),
            required=True,
            duration='PT6H0M'))

        sut_plan.add_planned_item(Statement(
            actor='test-2@email.com',
            verb='read',
            statement_obj=Statement.create_activity_obj(
                uri='http://www.someurl-2.com',
                name='Some website - 2')))

        sut_json = sut_plan.to_json()

        self.assertEqual(3, len(sut_json))

        sut_enroll_item = sut_json[0]
        self.assertEqual(
            {
                'objectType': 'Agent',
                'mbox': 'mailto:learner@test-email.com'
            },
            sut_enroll_item['actor'])

        self.assertEqual(
            {
                'id': 'http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan',
                'display': {'en': 'test enrollment'}
            },
            sut_enroll_item['verb'])

        self.assertEqual({'name': {'en': 'Test plan'}}, sut_enroll_item['object']['definition'])
        self.assertEqual('Activity', sut_enroll_item['object']['objectType'])
        sut_enroll_item_id = sut_enroll_item['object']['id']
        self.assertRegex(sut_enroll_item_id, 'http://www.tincanapi.co.uk/wiki/learning_plan:\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
 
        self._assert_planned_item(
            sut_planned_item=sut_json[1],
            expected_substatement={
                'objectType': 'SubStatement',
                'actor': {
                    'objectType': 'Agent',
                    'mbox': 'mailto:learner@test-email.com'
                },
                'verb': {
                    'id': 'http://activitystrea.ms/schema/1.0/read',
                    'display': {'en': 'read test'}
                },
                'object': {
                    'objectType': 'Activity',
                    'id': 'http://www.someurl-1.com',
                    'definition': {
                        'name': {'en': 'Some website - 1'}
                    }
                },
                'context': {
                    'contextActivities': {
                        'grouping': [
                            {
                                'objectType': 'Activity',
                                'id': sut_enroll_item_id
                            }
                        ]
                    }
                },
                'result': {
                    'duration': 'PT6H0M',
                    'completion': True
                }
            })
        
        self._assert_planned_item(
            sut_planned_item=sut_json[2],
            expected_substatement={
                'objectType': 'SubStatement',
                'actor': {
                    'objectType': 'Agent',
                    'mbox': 'mailto:learner@test-email.com'
                },
                'verb': {
                    'id': 'http://activitystrea.ms/schema/1.0/read',
                    'display': {'en': 'read'}
                },
                'object': {
                    'objectType': 'Activity',
                    'id': 'http://www.someurl-2.com',
                    'definition': {
                        'name': {'en': 'Some website - 2'}
                    }
                },
                'context': {
                    'contextActivities': {
                        'grouping': [
                            {
                                'objectType': 'Activity',
                                'id': sut_enroll_item_id
                            }
                        ]
                    }
                }
            })


    def _assert_planned_item(self, sut_planned_item, expected_substatement):
        self.assertEqual(
            {
                'objectType': 'Agent',
                'mbox': 'mailto:%s' % Statement.DEFAULT_PLANNER_EMAIL
            },
            sut_planned_item['actor'])

        self.assertEqual(
            {
                'id': 'http://www.tincanapi.co.uk/verbs/planned_learning',
                'display': {'en': 'planned'}
            },
            sut_planned_item['verb'])

        self.assertEqual(expected_substatement, sut_planned_item['object'])

if __name__ == '__main__':
    unittest.main()
