import json
import http.client
import uuid
import ssl
import os
from application.config import Config
import requests
from application.modules.models import Statement

LEARNING_PLAN_DATA_FILEPATH = 'application/data/learning-plan.json'

LEARNING_PLAN_USER_DATA_FILEPATH = 'application/data/user-data.json'

def get_user_records(email):
    pipeline = [
        _create_match_user(email),
        PROJECTIONS['learning_record'],
        {"$sort": {"when": -1}}
    ]

    return query(pipeline)['result']

def get_user_learning_plan(email):
    # all of them lines of code be here for now
    with open(LEARNING_PLAN_DATA_FILEPATH) as data_file:
        learning_plan = json.load(data_file)

    if os.path.isfile(LEARNING_PLAN_USER_DATA_FILEPATH):
        with open(LEARNING_PLAN_USER_DATA_FILEPATH) as user_data_file:
            diagnostic_learning_plan = json.load(user_data_file)
            
            planned_items = [ {
                        "title": item['title'],
                        "required": item.get('required', False),
                        "descriptionLines": [],
                        "infoLines": [
                          item['type'],
                          ("Average time: " + item['duration'] if item['duration'] else item.get('duration'))
                        ],
                        "actions": [{
                            "title": "Start now",
                            "url": item['url']
                        }]
                    }
                for item in diagnostic_learning_plan]

            dgn_learning_plan = {
                "title": "Actions from diagnostic",
                "addedBy": "diagnostic",
                "descriptionLines": [
                  "Imported automatically from your diagnostic test."
                ],
                "sections": [],
                "items": planned_items
            }

            learning_plan.insert(len(learning_plan)-1, dgn_learning_plan)


    return learning_plan




def create_sample_plan(learner_email):
    sample_plan = Statement.create_plan(
        plan_name='Sample learning plan',
        planner_actor='planner@gmail.com')

    # maybe here assignee_actor then add_planneditem can take it if it's there - do it later
    sample_plan.add_planned_item(Statement(
        actor=learner_email,
        verb=Statement.create_verb('complete'),
        statement_obj=Statement.create_activity_obj(
            uri='http://www.skillsyouneed.com/ips/improving-communication.html',
            name='Developing Effective Communication | Skills You Need')))

    sample_plan.add_planned_item(Statement(
        actor=learner_email,
        verb='read',
        statement_obj=Statement.create_activity_obj(
            uri='http://www.artofliving.org/meditation/meditation-for-you/benefits-of-meditation',
            name='Benefits of Meditation | Meditation Benefits | The Art Of Living Global')))

    return sample_plan.to_json()


def save_to_json(learner_email, json_data):
    with open(LEARNING_PLAN_USER_DATA_FILEPATH, 'w+') as f:
        json.dump(json_data, f, indent=4)

def remove_json():
    if os.path.isfile(LEARNING_PLAN_USER_DATA_FILEPATH):
        os.remove(LEARNING_PLAN_USER_DATA_FILEPATH)
        return 'removed :)'
    else:
        return 'already done - there was no file to remove'
    


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












