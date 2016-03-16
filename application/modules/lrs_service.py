import json
import http.client
import uuid
import ssl
import os
import logging
import requests
import urllib.parse as url_parse

from application.config import Config
from application.modules.models import Statement
import application.modules.dates as mls_dates

LEARNING_PLAN_DATA_FILEPATH = 'application/data/learning-plan.json'


def load_course_learning_records(email, course_uri):
    verb = Statement.create_verb('complete')
    query_response = _query([
        {'$match': {
            'statement.actor.mbox': 'mailto:%s' % email,
            'statement.object.id': '%s' % url_parse.quote(course_uri),
            'statement.verb.id': '%s' % verb['id'],
            'voided': False
        }},
        PROJECTIONS['learning_record'],
        {'$sort': {'when': -1}}
    ])
    return _get_lrs_result_from(query_response)

def save_statement(statement_json):
    return _post(statement_json)



def load_user_records(email):
    pipeline = [
        _create_match_learning_records_by(email),
        PROJECTIONS['learning_record'],
        {'$sort': {'when': -1}}
    ]
    return _get_lrs_result_from(_query(pipeline))

def load_user_learning_plans(email):
    # all of them lines of code be here for now
    with open(LEARNING_PLAN_DATA_FILEPATH) as data_file:
        learning_plan = json.load(data_file)

    loaded_plans = load_learning_plans(email)
    for plan in loaded_plans:
        learning_plan.insert(len(learning_plan)-1, _create_learning_plan_view_model(plan, email))

    return learning_plan

def load_learning_plans(email):
    query_response = _query([
        _create_match_learning_plan_by_email(email),
        PROJECTIONS['plan']
    ])
    return _get_lrs_result_from(query_response)

def load_learning_plan(plan_id):
    query_response = _query([
        _create_match_learning_plan_by_plan_id(plan_id),
        PROJECTIONS['plan']
    ])
    return _get_lrs_result_from(query_response, take_first=True)

def load_learning_plan_items(plan_id):
    query_response = _query([
        _create_match_learning_plan_items_by(plan_id),
        PROJECTIONS['plan_item']
    ])
    return _get_lrs_result_from(query_response)

def load_learning_plan_item(statement_id):
    query_response = _query([
        _create_match_learning_plan_item_by(statement_id),
        PROJECTIONS['plan_item']
    ])
    return _get_lrs_result_from(query_response, take_first=True)

def load_learning_plan_item_learning_records(email, plan_item_id):
    plan_item = load_learning_plan_item(plan_item_id)
    query_response = _query([
        _create_match_learning_plan_item_learning_records(email, plan_item),
        PROJECTIONS['learning_record']
    ])
    return _get_lrs_result_from(query_response)

def save_learning_plan(learning_plan):
    return _post(learning_plan.to_json())

def clean_learning_plans(email):
    logger = logging.getLogger()

    username = Config.LRS_USER
    password = Config.LRS_PASS
    matcher = {'$or': [
        {'statement.actor.mbox': 'mailto:%s' % email},
        {'statement.object.actor.mbox': 'mailto:%s' % email}
    ]}

    requestUrl = '%s/void?match=%s' % (_create_full_url(Config.LRS_COMMAND_API_URL), json.dumps(matcher))
    logger.debug(requestUrl)

    response = requests.get(requestUrl, auth=(username, password), verify=False)
    return response.json()

def _get_lrs_result_from(query_response, take_first=False):
    result = query_response.get('result')
    if result and take_first:
        result = next(iter(result), None)
    return result

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


def _create_match_learning_records_by(email):
    return {
        '$match': {
            '$or': [
                {'statement.actor.mbox': 'mailto:%s' % email},
                {'statement.actor.name': '%s' % email.split('@')[0]}
            ],
            'voided': False
        }
    }

def _create_match_learning_plan_by_email(email):
   return {
        '$match': {
            'statement.actor.mbox': 'mailto:%s' % email,
            'statement.verb.id': 'http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan',
            'voided': False
        }
    }

def _create_match_learning_plan_by_plan_id(plan_id):
   return {
        '$match': {
            '$or': [
                {'statement.id': '%s' % plan_id},
                {'statement.object.id': '%s' % plan_id},
                {'statement.object.id': 'http://www.tincanapi.co.uk/wiki/learning_plan:%s' % plan_id}
            ],
            'voided': False
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
            },
            'voided': False
        }
    }

def _create_match_learning_plan_item_by(statement_id):
    return {
        '$match': {
            'statement.id': statement_id,
            'voided': False
        }
    }

def _create_match_learning_plan_item_learning_records(email, plan_item):
    return {
        '$match': {
            'statement.actor.mbox': 'mailto:%s' % email,
            'statement.object.id': '%s' % url_parse.quote(plan_item['object']['id']),
            'statement.verb.id': '%s' % plan_item['verb']['id'],
            'voided': False
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
            # 'max_score': '$statement.result.score',
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

def _create_learning_plan_view_model(plan, email):
    planned_items = []
    
    for item in load_learning_plan_items(plan['object']['id']):
        records = load_learning_plan_item_learning_records(email, item['statementId'])

        verb_name = item['verb']['display']['en']
        
        info_lines = []
        resource_type = Statement.get_resource_type(item.get('object').get('definition').get('type'))
        if resource_type:
            resource_type = resource_type.get('name', '')
            info_lines.append(resource_type)
        
        duration = item.get('result', {}).get('duration')
        if duration:
            duration = 'Average time: ' + mls_dates.convert_duration(duration)
            info_lines.append(duration)

        actions = [{
            'title': verb_name.capitalize() + (' again' if records else ' now'),
            'url': item['object']['id']
        }]

        # taking the last one to display, done like this as who knows what they are going to come up with
        # all records may be required later
        if records:
            records = [records[-1]]

        planned_item = {
            'statementId': item['statementId'],
            'records': records,
            'title': '%s %s' % (verb_name.capitalize(), item['object']['definition']['name']['en']),
            'required': item.get('result', {}).get('completion', False),
            'descriptionLines': [],
            'infoLines': info_lines,
            'actions': actions
        }
        planned_items.append(planned_item)

    return {
        'statementId': plan['statementId'],
        'title': plan['object']['definition']['name']['en'],
        'addedBy': 'diagnostic',
        'descriptionLines': [],
        'sections': [],
        'items': planned_items
    }
