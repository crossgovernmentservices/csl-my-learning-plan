import json
import logging
from application.config import Config

DATA_FILEPATH='application/data/courses-for-search.json'
LEARNING_REGISTRY_SANDBOX='http://sandbox.learningregistry.org/slice?any_tags=civil%20service%20learning'

logger = logging.getLogger()

def get_all_courses_from_learning_registry():
    import urllib.request
    response = urllib.request.urlopen(LEARNING_REGISTRY_SANDBOX)
    items = json.loads(response.read().decode('utf-8'))
    logger.debug('got items')
    def convert_item(item):
        def map_type(resource_data):
            type_switcher = {
                'WebSite': 'web',
                'Web': 'web',
                'Video': 'video',
                'Book': 'book',
                'Workshop': 'workshop',
                'CreativeWork' : resource_data.get("learningResourceType", "eLearning").lower()
            }
            logger.debug('learningResourceType ' + resource_data.get("learningResourceType", "undefined"))
            logger.debug('Type is ' + resource_data['@type'])
            return type_switcher.get(resource_data.get("@type","undefined"),"undefined")

        return { 'title' : item['resource_data_description']['resource_data']['name'],
                 'type' :  map_type(item['resource_data_description']['resource_data']),
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
    if filterDict is None:    
        return all_courses
    mainFilter = filterDict["filter"].get("main-search", '').lower()
    typeFilter = filterDict["filter"].get("type-filter", '').lower()
    return [each for each in all_courses
                if (typeFilter is '' or typeFilter in each.get('type', ''))
                and (mainFilter in each.get('title','').lower()
                        or mainFilter in each.get('desc','').lower()
                        or [eachTopic for eachTopic in each.get('topics', []) if mainFilter in eachTopic.lower()])
            ]
