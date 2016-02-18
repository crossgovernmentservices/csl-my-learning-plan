import json
import http.client
import uuid
import ssl
from application.config import Config
import requests
import application.modules.models as Statement


LEARNING_PLAN_DATA_FILEPATH = 'application/data/learning-plan.json'
LRS_LEARNING_PLAN_ACTIVITIES_TEMPLATE_FILEPATH = 'application/data/lrs-learning-plan-activities-template.json'
LRS_LEARNING_PLAN_ENROLLMENT_TEMPLATE_FILEPATH = 'application/data/lrs-learning-plan-enrollment-template.json'


def get_user_records(email):
    pipeline = [
        _create_match_user(email),
        PROJECTIONS['learning_record'],
        { "$sort": { "when": -1 } }
    ]

    return query(pipeline)['result']

def get_user_learning_plan(email):
    # all of them lines of code be here for now
    with open(LEARNING_PLAN_DATA_FILEPATH) as data_file:
      learning_plan=json.load(data_file)
    return learning_plan

def create_plan(learner_email):
    with open(LRS_LEARNING_PLAN_ENROLLMENT_TEMPLATE_FILEPATH) as enrollment_file:
        enrollment_json = json.load(enrollment_file)

    with open(LRS_LEARNING_PLAN_ACTIVITIES_TEMPLATE_FILEPATH) as activities_file:
        activities_json = json.load(activities_file)

    newid = uuid.uuid1()
    enrollment_json["object"]["id"] = enrollment_json["object"]["id"] + str(newid)
    enrollment_json["actor"]["mbox"] = "mailto:" + learner_email
    for activity in activities_json:
        activity["object"]["actor"]["mbox"] = "mailto:" + learner_email
        activity["context"]["contextActivities"]["grouping"][0]["id"] = activity["context"]["contextActivities"]["grouping"][0]["id"] + str(newid)

    activities_json.insert(0, enrollment_json)
    return activities_json


def post(payload_json):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    requestUrl = _create_full_url(Config.LRS_STATEMENTS_URL)
    headers = {
        'X-Experience-API-Version': '1.0.1',
        'Content-Type': 'text/json'
    }

    response = requests.post(requestUrl, headers=headers, data=json.dumps(payload_json), auth=(username, password), verify=False)
    return response.json()


def query(aggregation_pipeline):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    query_url = Config.LRS_QUERY_URL % json.dumps(aggregation_pipeline)
    requestUrl = _create_full_url(query_url)

    response = requests.get(requestUrl, auth=(username, password), verify=False)
    return response.json()

def _create_full_url(route_url):
    return "{protocol}://{host}:{port}{route_url}".format(
        protocol=('https' if Config.LRS_HTTPS_ENABLED else 'http'),
        host=Config.LRS_HOST,
        port=Config.LRS_PORT,
        route_url=route_url)


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












