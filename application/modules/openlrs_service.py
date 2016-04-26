import json
import http.client
import uuid
import ssl
import os
import logging
import requests

from application.config import Config
from application.modules.models import Statement
import application.modules.dates as mls_dates

LEARNING_PLAN_DATA_FILEPATH = 'application/data/learning-plan.json'


def save_statement(statement_json):
    return _post(statement_json)


def clean_learning_record(email):
    result = []

    records = load_user_records(email)
    if records:
        records_to_clean = [
            Statement(
                actor=email,
                verb='void',
                statement_obj=Statement.create_reference_obj(record['statementId'])).to_json()
            for record in records]

        result = _post(records_to_clean)

    return json.dumps(result)


def load_course_learning_records(email, course_uri):
    verb = Statement.create_verb('complete')
    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'nested': {
                            'path': 'actor',
                            'query': {'match_phrase': {'actor.mbox': 'mailto:%s' % email}}
                        }
                    },
                    {
                        'nested': {
                            'path': 'verb',
                            'query': {'match_phrase': {'verb.id': verb['id']}}
                        }
                    },
                    {
                        'nested': {
                            'path': 'object',
                            'query': {'match_phrase': {'object.id': course_uri}}
                        }
                    }
                ]
            }
        }
    }

    return _get_lrs_result_from(_execute_query(query))


def load_user_records(email):
    query = {
        'size': 9999,
        'query': _create_match_learning_records_by(email),
        'sort': {'stored': {'order': 'desc'}}
    }

    return _get_lrs_result_from(_execute_query(query))

def load_user_learning_plans(email):
    # all of them lines of code be here for now
    with open(LEARNING_PLAN_DATA_FILEPATH) as data_file:
        learning_plan = json.load(data_file)

    loaded_plans = load_learning_plans(email)
    for plan in loaded_plans:
        learning_plan.insert(len(learning_plan)-1, plan)

    return learning_plan

def load_learning_plans(email):
    query = {
        'size': 9999,
        'query': _create_match_learning_records_by(email),
        'sort': {'stored': {'order': 'desc'}}
    }

    result = _execute_query(query).get('hits', {}).get('hits')
    enroll_verb = Statement.VERBS['enroll']
    plan_verb = Statement.VERBS['plan']

    if result:
        statements_to_hide = []
        for raw_statement in result:
            statement = raw_statement.get('_source')
            if statement.get('verb').get('id') == Statement.VERBS['void']['id']:
                statements_to_hide.append(raw_statement.get('_id'))
                statements_to_hide.append(statement.get('object').get('id'))

        plans = []
        plan_items = {}

        for raw_statement in result:
            if raw_statement.get('_id') not in statements_to_hide:
                statement = raw_statement.get('_source')

                if statement.get('verb').get('id') == enroll_verb['id']:
                    plans.append(statement)
                else:
                    plan_group = statement.get('context', {}).get('contextActivities', {}).get('grouping')
                    if plan_group:
                        plan_id = plan_group[0]['id']

                        if not plan_items.get(plan_id):
                            plan_items[plan_id] = []
                        plan_items[plan_id].append(statement)

    return [_create_learning_plan_view_model(plan, plan_items[plan['object']['id']]) for plan in plans]


def _get_lrs_result_from(query_response, take_first=False):

    def __should_be_hidden(statement):
        return statement.get('verb').get('id') in [Statement.VERBS['void']['id'], Statement.VERBS['plan']['id']]

    result = query_response.get('hits', {}).get('hits')

    if result:
        statements_to_hide = []
        for raw_statement in result:
            statement = raw_statement.get('_source')
            if __should_be_hidden(statement):
                statements_to_hide.append(raw_statement.get('_id'))
                statements_to_hide.append(statement.get('object').get('id'))


        result = [_create_view_model_learning_record(item.get('_source'))
            for item in result
            if item.get('_id') not in statements_to_hide]

        if result and take_first:
            result = next(result, None)

    return result or []


def _execute_query(payload_json):
    query_url = _create_full_url(Config.OPEN_LRS_QUERY_URL, Config.OPEN_LRS_QUERY_PORT)
    return _post(payload_json, query_url)


def _post(payload_json, target_url=None):
    username = Config.OPEN_LRS_USER
    password = Config.OPEN_LRS_PASS
    requestUrl = target_url or _create_full_url(Config.OPEN_LRS_COMMAND_URL, Config.OPEN_LRS_COMMAND_PORT)

    headers = {
        'X-Experience-API-Version': '1.0.1',
        'Content-Type': 'application/json'
    }

    response = requests.post(requestUrl, headers=headers, data=json.dumps(
        payload_json), auth=(username, password), verify=False)
    return response.json()


def _create_full_url(route_url, port):
    return '{protocol}://{host}:{port}{route_url}'.format(
        protocol=('https' if Config.OPEN_LRS_HTTPS_ENABLED else 'http'),
        host=Config.OPEN_LRS_HOST,
        port=port,
        route_url=route_url)


def _create_match_learning_records_by(email):
    return {
        'nested': {
            'path': 'actor',
            'query': {
                'bool': {
                    'should': [
                        {'match_phrase': {'actor.mbox': 'mailto:%s' % email}},
                        {'match_phrase': {'actor.name':  email.split('@')[0]}}
                    ]
                }
            }
        }
    }


def _create_view_model_learning_record(record):
    result = {}
    result['statementId'] = record.get('id')

    actor_mbox = record.get('actor').get('mbox')
    actor_name = record.get('actor').get('account', {}).get('name')
    result['actor'] = {
        'id': actor_mbox or actor_name,
        'name': actor_name,
        'mbox': actor_mbox
    }

    verb_name = record.get('verb').get('display')
    result['verb'] = {
        'id': record.get('verb').get('id'),
        'name': verb_name.get('en', verb_name.get('en-US'))
    }

    res_object = record.get('object')
    result['object'] = {
        'id': res_object.get('id'),
        'name': res_object.get('definition', {}).get('name', {}).get('en') or record.get('object')
    }

    result['when'] = record.get('timestamp')
    result['result'] = record.get('result')

    return result


def _create_learning_plan_view_model(plan_statement, item_statements):
    return {
        'statementId': plan_statement['id'],
        'title': plan_statement['object']['definition']['name']['en'],
        'addedBy': 'diagnostic',
        'descriptionLines': [],
        'sections': [],
        'items': [ _create_learning_plan_item_view_model(item) for item in item_statements]
    }


def _create_learning_plan_item_view_model(item_statement, learning_records=[]):
    verb_name = item_statement['verb']['display']['en']
    
    info_lines = []
    resource_type = Statement.get_resource_type(item_statement.get('object').get('definition').get('type'))
    if resource_type:
        resource_type = resource_type.get('name', '')
        info_lines.append(resource_type)
    
    duration = item_statement.get('result', {}).get('duration')
    if duration:
        duration = 'Average time: ' + mls_dates.convert_duration(duration)
        info_lines.append(duration)

    actions = [{
        'title': verb_name.capitalize() + (' again' if learning_records else ' now'),
        'url': item_statement['object']['id']
    }]

    # taking the last one to display, done like this as who knows what they are going to come up with
    # all learning_records may be required later
    if learning_records:
        learning_records = [learning_records[-1]]

    planned_item = {
        'statementId': item_statement['id'],
        'records': learning_records,
        'title': '%s %s' % (verb_name.capitalize(), item_statement['object']['definition']['name']['en']),
        'required': item_statement.get('result', {}).get('completion', False),
        'descriptionLines': [],
        'infoLines': info_lines,
        'actions': actions
    }

    return planned_item
