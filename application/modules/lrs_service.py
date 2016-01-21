import json
import http.client
import uuid
import ssl
from base64 import b64encode
from application.config import Config
import urllib
import requests


def get_user_records(email):
    pipeline = [
        _create_match_user(email),
        PROJECTIONS['learning_record'],
        { "$sort": { "when": -1 } }
    ]

    return query(pipeline)['result']


def query(aggregation_pipeline):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    requestUrl = "{protocol}://{host}:{port}/{query_url}".format(
        protocol=('https' if Config.LRS_HTTPS_ENABLED else 'http'),
        host=Config.LRS_HOST,
        port=Config.LRS_PORT,
        query_url=Config.LRS_QUERY_URL % json.dumps(aggregation_pipeline))

    response=requests.get(requestUrl, auth=(username, password), verify=False)#params=payload)
    return response.json()


def _create_match_user(email):
    return {
        "$match": {
            "$or": [
                { "statement.actor.mbox": "mailto:%s" % email},
                { "statement.actor.name": "%s" % email.split('@')[0] }
            ]
        }
    }

PROJECTIONS = {
    'learning_record': {
        "$project": {
          "statementId": "$statement.id",
          "actor": {
            "id": { "$ifNull": [ "$statement.actor.account.name", "$statement.actor.mbox" ] },
            "name": "$statement.actor.name",
            "mbox": "$mailto"
          },
          "verb": {
            "id": "$statement.verb.id",
            "name": { "$ifNull": [ "$statement.verb.display.en", "$statement.verb.display.en-US" ] }
          },
          "object": {
            "id": "$statement.object.id",
            "name": { "$ifNull": [ "$statement.object.definition.name.en", "$statement.object.definition.name.en-US" ] }
          },
          "when": "$statement.timestamp",
          "result": {
            "score": "$statement.result.score",
            "duration": "$statement.result.duration"
          },
          "activities": { 
            "$map": { 
              "input": "$statement.context.contextActivities.grouping",
              "as": "activity",
              "in": { 
                "id": "$$activity.id",
                "name": "$$activity.definition.name.en"
              }
            }
          }
        }
    }
}

#     TO INVESTIGATE THIS DAMN THING
    # headers = dict({
    #     # 'X-Experience-API-Version': '1.0.1',
    #     # 'Content-Type': 'application/json'
    # })
#     headers = _create_basic_auth_header()

#     # url_query = Config.LRS_QUERY_URL %  json.dumps(aggregation_pipeline)

#     url_query = '/api/v1/statements/aggregate?pipeline=%s' % json.dumps(aggregation_pipeline)
#     print(url_query)

#     server = _create_http_server()
#     server.connect()

#     server.request('GET', url_query, headers=headers)
#     response = server.getresponse()
#     response_data = response.read().decode(response.headers.get_content_charset('utf-8'))
#     return (response_data)


# def _create_basic_auth_header():
#     user_and_pass = Config.LRS_USER + ':' + Config.LRS_PASS
#     user_and_pass = b64encode(bytes(user_and_pass, "ascii")).decode("ascii")
#     return {'Authorization': 'Basic %s' % user_and_pass}


# def _create_http_server():
#     if Config.LRS_HTTPS_ENABLED:
#         httpServer = http.client.HTTPSConnection(
#             host=Config.LRS_HOST,
#             port=Config.LRS_PORT,
#             context=ssl._create_unverified_context())
#     else:
#         httpServer = http.client.HTTPConnection(Config.LRS_HOST)

#     return httpServer
