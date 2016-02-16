import json
import http.client
import uuid
import ssl
from base64 import b64encode
from application.config import Config
import urllib
import requests

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


def create_plan_from_user_json():
    activity_verb_mappings = { "article" : "read" };
    with open(LRS_LEARNING_PLAN_ACTIVITIES_TEMPLATE_FILEPATH) as template_activities_file:
        template_activities = json.load(template_activities_file)

    # newid = uuid.uuid1()
    # enrolstatement = template_activities['enrollment'].copy()
    # ## customise for user
    # # swap out the plan id with a unique identifier
    # enrolstatement["object"]["id"] = enrolstatement["object"]["id"] + str(newid)
    # #assign title
    # enrolstatement['object']['definition']['name']['en'] = user_json['title']
    # # assign the learners id to the enroll
    # enrolstatement["actor"]["mbox"] = 'mailto:'+user_id
    # statements = []
    # for activitylink in user_json['planitems'].keys():
    #     verb = activity_verb_mappings[user_json['planitems'][activitylink]['type']]
    #     statement = template_activities[verb].copy()
    #     statement['object']['actor']['mbox']='mailto:'+user_id
    #     statement['object']['object']['id']=activitylink
    #     statement['object']['object']['definition']['name']['en']=user_json['planitems'][activitylink]['name']
    #     # context for plan
    #     statement["context"]["contextActivities"]["grouping"][0]["id"] = statement["context"]["contextActivities"]["grouping"][0]["id"] + str(newid) 
    #     statements.append(statement)
    # body = '['
    # body = body + json.dumps(enrolstatement)
    # for statement in statements:
    #     body = body + ", " + json.dumps(statement)
    # body = body + ']'
    return template_activities

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


def post(payload):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    requestUrl = _create_url(Config.LRS_STATEMENTS_URL)
    headers = {
        'X-Experience-API-Version': '1.0.1',
        'Content-Type': 'text/json'
    }

    print(json.dumps(payload))

    response = requests.post(requestUrl, headers=headers, data=json.dumps(payload), auth=(username, password), verify=False)
    return response.json()


def query(aggregation_pipeline):
    username = Config.LRS_USER
    password = Config.LRS_PASS

    query_url = Config.LRS_QUERY_URL % json.dumps(aggregation_pipeline)
    requestUrl = _create_url(query_url)

    response = requests.get(requestUrl, auth=(username, password), verify=False)
    return response.json()

# no creativity for names today :/
def _create_url(detail_url):
    return "{protocol}://{host}:{port}{detail_url}".format(
        protocol=('https' if Config.LRS_HTTPS_ENABLED else 'http'),
        host=Config.LRS_HOST,
        port=Config.LRS_PORT,
        detail_url=detail_url)


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
