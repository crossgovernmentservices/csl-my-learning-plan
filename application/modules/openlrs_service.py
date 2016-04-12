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
                statement_obj=Statement.create_void_obj(record['statementId'])).to_json()
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
                            'query': {'match': {'actor.mbox': 'mailto:%s' % email}}
                        }
                    },
                    {
                        'nested': {
                            'path': 'verb',
                            'query': {'match': {'verb.id': verb['id']}}
                        }
                    },
                    {
                        'nested': {
                            'path': 'object',
                            'query': {'match': {'object.id': course_uri}}
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


def _get_lrs_result_from(query_response, take_first=False):
    result = query_response.get('hits').get('hits')
    result = [_create_view_model_learning_record(item.get('_source')) for item in result]

    if result and take_first:
        result = next(result, None)

    return result


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
                        {'match': {'actor.mbox': 'mailto:%s' % email}},
                        {'match': {'actor.name':  email.split('@')[0]}}
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
        'name': res_object.get('definition', {}).get('name', {}).get('en') or record.get('id')
    }

    result['when'] = record.get('timestamp')
    result['result'] = record.get('result')

    # 'object': {
    #   'id': '$statement.object.id',
    #   'name': {'$ifNull': ['$statement.object.definition.name.en', '$statement.object.definition.name.en-US']}
    # },
    # 'when': '$statement.timestamp',
    # 'result': {
    #   'score': '$statement.result.score',
    #   # 'max_score': '$statement.result.score',
    #   'duration': '$statement.result.duration'
    # },
    return result


# 'sort' : [
    # { 'post_date' : {'order' : 'asc'}},
    # 'user',
    # {
