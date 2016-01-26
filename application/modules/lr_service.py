import json
import logging
from application.config import Config

DATA_FILEPATH='application/data/courses-for-search.json'
LEARNING_REGISTRY_SANDBOX='http://sandbox.learningregistry.org/slice?any_tags=civil%20service%20learning'

logger = logging.getLogger("flogger")

def get_all_courses_from_learning_registry():
    import urllib.request
    response = urllib.request.urlopen(LEARNING_REGISTRY_SANDBOX)
    items = json.loads(response.read().decode('utf-8'))
    logger.debug('got items')
    def convert_item(item):
        return { 'title' : item['resource_data_description']['resource_data']['name'],
                 'type' :  item['resource_data_description']['resource_data']['learningResourceType'].lower(),
                 'desc' :  item['resource_data_description']['resource_data']['description'],
                 'duration' :  item['resource_data_description']['resource_data']['timeRequired'],
                 'url' :  item['resource_data_description']['resource_data']['url'], 
                 'topics' : item['resource_data_description']['resource_data']['keywords']}
    return [convert_item(i) for i in items['documents']]

def get_all_courses():
    with open(DATA_FILEPATH) as data_file:
        courses = json.load(data_file)
    return courses

def get_courses(filterDict):
    logger.info("get_courses")
    all_courses = get_all_courses_from_learning_registry()
    filterStr = ('' if filterDict is None else filterDict.get('filter', '')).lower()
    if filterStr:
        return [each for each in all_courses
                if filterStr in each.get('title','').lower()
                or filterStr in each.get('desc','').lower()
                or [eachTopic for eachTopic in each.get('topics', []) if filterStr in eachTopic.lower()]
            ]
    else:
        return all_courses
