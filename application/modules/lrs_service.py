import json
import http.client
import uuid
import ssl
import os
from application.config import Config
import requests
from application.modules.models import Statement
import application.modules.dates as mls_dates

LEARNING_PLAN_DATA_FILEPATH = 'application/data/learning-plan.json'

def get_user_records(email):
    pipeline = [
        _create_match_user_by(email),
        PROJECTIONS['learning_record'],
        {'$sort': {'when': -1}}
    ]

    return _query(pipeline)['result']

def get_user_learning_plan(email):
    # all of them lines of code be here for now
    with open(LEARNING_PLAN_DATA_FILEPATH) as data_file:
        learning_plan = json.load(data_file)

    plans = load_learning_plans(email)

    for plan in plans:
        planned_items = [{
                'title': '%s %s' % (item['verb']['display']['en'].capitalize(), item['object']['definition']['name']['en']),
                'required': item.get('result', {}).get('completion', False),
                'descriptionLines': [],
                'infoLines': [
                    Statement.get_resource_type(item['object']['definition']['type'])['name'],
                    ('Average time: ' + mls_dates.convert_duration(item['result']['duration']) 
                        if item.get('result', {}).get('duration') else item.get('result', {}).get('duration'))
                ],
                'actions': [{
                    'title': 'Start now',
                    'url': item['object']['id']
                }]
            } for item in load_learning_plan_items(plan['object']['id'])]

        dgn_learning_plan = {
            'title': plan['object']['definition']['name']['en'],
            'addedBy': 'diagnostic',
            'descriptionLines': [],
            'sections': [],
            'items': planned_items
        }

        learning_plan.insert(len(learning_plan)-1, dgn_learning_plan)

    return learning_plan

def load_learning_plans(email):
    return _query([
        _create_match_learning_plan_by_email(email),
        PROJECTIONS['plan']
    ])['result']

def load_learning_plan(plan_id):
    return _query([
        _create_match_learning_plan_by_plan_id(plan_id),
        PROJECTIONS['plan']
    ])['result'][0]

def load_learning_plan_items(plan_id):
    return _query([
        _create_match_learning_plan_items_by(plan_id),
        PROJECTIONS['plan_item']
    ])['result']

def load_learning_plan_item(statement_id):
    return _query([
        _create_match_learning_plan_item_by(statement_id),
        PROJECTIONS['plan_item']
    ])['result'][0]

def load_learning_plan_item_learning_records(email, plan_item_id):
    plan_item = load_learning_plan_item(plan_item_id)
    return _query([
        _create_match_learning_plan_item_learning_records(email, plan_item),
        PROJECTIONS['learning_record']
    ])['result']


def save_learning_plan(learning_plan):
    return _post(learning_plan.to_json())


def create_sample_plan(learner_email):
    sample_plan = Statement.create_plan(
        plan_name='Sample learning plan',
        learner_actor=learner_email)

    # maybe here assignee_actor then add_planneditem can take it if it's there - do it later
    sample_plan.add_planned_item(Statement(
        verb=Statement.create_verb('complete'),
        statement_obj=Statement.create_activity_obj(
            uri='http://www.skillsyouneed.com/ips/improving-communication.html',
            name='Developing Effective Communication | Skills You Need')))

    sample_plan.add_planned_item(Statement(
        verb='read',
        statement_obj=Statement.create_activity_obj(
            uri='http://www.artofliving.org/meditation/meditation-for-you/benefits-of-meditation',
            name='Benefits of Meditation | Meditation Benefits | The Art Of Living Global')))

    return _post(sample_plan.to_json())


def _post(payload_json):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    requestUrl = _create_full_url(Config.LRS_STATEMENTS_URL)
    headers = {
        'X-Experience-API-Version': '1.0.1',
        'Content-Type': 'text/json'
    }

    response = requests.post(requestUrl, headers=headers, data=json.dumps(payload_json), auth=(username, password), verify=False)
    return response.json()


def _query(aggregation_pipeline):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    query_url = Config.LRS_QUERY_URL % json.dumps(aggregation_pipeline)
    requestUrl = _create_full_url(query_url)

    response = requests.get(requestUrl, auth=(username, password), verify=False)
    return response.json()


def _create_full_url(route_url):
    return '{protocol}://{host}:{port}{route_url}'.format(
        protocol=('https' if Config.LRS_HTTPS_ENABLED else 'http'),
        host=Config.LRS_HOST,
        port=Config.LRS_PORT,
        route_url=route_url)


def _create_match_user_by(email):
    return {
        '$match': {
            '$or': [
                {'statement.actor.mbox': 'mailto:%s' % email},
                {'statement.actor.name': '%s' % email.split('@')[0]}
            ]
        }
    }

def _create_match_learning_plan_by_email(email):
   return {
        '$match': {
            'statement.actor.mbox': 'mailto:%s' % email,
            'statement.verb.id': 'http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan'
        }
    }

def _create_match_learning_plan_by_plan_id(plan_id):
   return {
        '$match': {
            '$or': [
                {'statement.id': '%s' % plan_id},
                {'statement.object.id': '%s' % plan_id},
                {'statement.object.id': 'http://www.tincanapi.co.uk/wiki/learning_plan:%s' % plan_id}
            ]
        }
    }

def _create_match_learning_plan_items_by(plan_id):
    return {
        '$match': {
            'statement.object.context.contextActivities.grouping': {
                '$elemMatch': {
                    '$or': [
                        {'id': '%s' % plan_id},
                        {'id': 'http://www.tincanapi.co.uk/wiki/learning_plan:%s' % plan_id}
                    ]
                }
            }
        }
    }

def _create_match_learning_plan_item_by(statement_id):
    return {
        '$match': {'statement.id': statement_id}
    }


def _create_match_learning_plan_item_learning_records(email, plan_item):
    return {
        '$match': {
            'statement.actor.mbox': 'mailto:%s' % email,
            'statement.object.id': '%s' % plan_item['object']['id'],
            'statement.object.definition.type': '%s' % plan_item['object']['definition']['type'],
            'statement.verb.id': '%s' % plan_item['verb']['id']
        }
    }


PROJECTIONS = {
    'learning_record': {
        '$project': {
          'statementId': '$statement.id',
          'actor': {
            'id': {'$ifNull': ['$statement.actor.account.name', '$statement.actor.mbox']},
            'name': '$statement.actor.name',
            'mbox': '$mailto'
          },
          'verb': {
            'id': '$statement.verb.id',
            'name': {'$ifNull': ['$statement.verb.display.en', '$statement.verb.display.en-US']}
          },
          'object': {
            'id': '$statement.object.id',
            'name': {'$ifNull': ['$statement.object.definition.name.en', '$statement.object.definition.name.en-US']}
          },
          'when': '$statement.timestamp',
          'result': {
            'score': '$statement.result.score',
            'duration': '$statement.result.duration'
          },
          'activities': {
            '$map': {
              'input': '$statement.context.contextActivities.grouping',
              'as': 'activity',
              'in': {
                'id': '$$activity.id',
                'name': '$$activity.definition.name.en'
              }
            }
          }
        }
    },

    'plan': {
        '$project': {
            '_id': 1,
            'statementId': '$statement.id',
            'actor': '$statement.actor',
            'verb': '$statement.verb',
            'object': '$statement.object'
        }
    },

    'plan_item': {
        '$project': {
            '_id': 1,
            'statementId': '$statement.id',
            'actor': '$statement.object.actor',
            'verb': '$statement.object.verb',
            'object': '$statement.object.object',
            'result': '$statement.object.result'
        }
    }

}


