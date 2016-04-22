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

    # loaded_plans = load_learning_plans(email)
    # for plan in loaded_plans:
    #     learning_plan.insert(len(learning_plan)-1, _create_learning_plan_view_model(plan, email))

    return learning_plan

def load_learning_plans(email):
    # query_response = _query([
    #     _create_match_learning_plan_by_email(email),
    #     PROJECTIONS['plan']
    # ])
    return [] #_get_lrs_result_from(query_response)


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
    print(json.dumps(payload_json))
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


