import json
import logging
from application.config import Config

DATA_FILEPATH = 'application/data/courses-for-search.json'
RESOURCE_TINCAN_DATA = 'application/data/learning-resource-tincanstatements.json'
RESOURCE_DATA_FILEPATH = 'application/data/learning-resources.json'

LEARNING_REGISTRY_URL = Config.LR_URL + Config.LR_QUERY_URL

logger = logging.getLogger()

def get_resource(resource_id):

    with open(RESOURCE_DATA_FILEPATH) as data_file:
        course_data = json.load(data_file).get(resource_id, {})

    lr_data = get_courses({"filter": {"id": resource_id}})
    lr_data = lr_data[0] if lr_data else {}

    return {**course_data, **lr_data}

    

def get_resources_with_tincanstatements():
    with open(RESOURCE_TINCAN_DATA) as data_file:
        tc = json.load(data_file)

    def addtc(item):
        if item['url'] in tc:
            item['tincanstatement'] = tc[item['url']]
        return item

    return [addtc(r) for r in get_resources()]

def get_resources():
    import urllib.request
    logger.debug('Ger resources query url: '+LEARNING_REGISTRY_URL)
    response = urllib.request.urlopen(LEARNING_REGISTRY_URL)
    items = json.loads(response.read().decode('utf-8'))
    return [{**i['resource_data_description']['resource_data'], '_id': i['resource_data_description']['_id']} for i in items['documents']]

def get_all_courses_from_learning_registry():
    def convert_item(item):
        def map_type(resource_data):
            type_switcher = {
                'WebSite': 'website',
                'Article': 'article',
                'Video': 'video',
                'Book': 'book',
                'Workshop': 'workshop',
                'CreativeWork': resource_data.get("learningResourceType", "eLearning").lower().replace(' ','')
            }
            logger.debug('learningResourceType ' + resource_data.get("learningResourceType", "undefined"))
            logger.debug('Type is ' + resource_data['@type'])
            return type_switcher.get(resource_data.get("@type","undefined"),"undefined")

        converted = {
            'id': item['_id'],
            'title': item['name'],
            'audience': item['audience'],
            'type': map_type(item),
            'desc': item['description'],
            'url': item['url'],
            'price': item['offers']['price'] + item['offers']['priceCurrency'] if 'offers' in item else 'Free Resource',
            'topics': item['keywords']
        }

        if 'timeRequired' in item:
            converted['duration'] = item['timeRequired']
        return converted

    return [convert_item(i) for i in get_resources()]

def get_all_courses():
    with open(DATA_FILEPATH) as data_file:
        courses = json.load(data_file)
    return courses

def get_courses(filterDict):
    all_courses = get_all_courses_from_learning_registry()
    if filterDict is None:
        return all_courses
    idFilter = filterDict["filter"].get("id", '')
    mainFilter = filterDict["filter"].get("main-search", '').lower()
    typeFilter = filterDict["filter"].get("type-filter", '').lower()
    professionFilter = filterDict["filter"].get("profession-filter", '').lower()
    freeResourcesOnly = filterDict["filter"].get("free-resources-only", 'False')
    logger.debug('freeResourcesOnly ' + freeResourcesOnly)
    return [each for each in all_courses
                if (typeFilter is '' or typeFilter in each.get('type', ''))
                and (idFilter is '' or idFilter == each.get('id', ''))
                and (freeResourcesOnly == 'False' or 'Free' in each.get('price', 'Free'))
                and (professionFilter is '' or professionFilter in each.get('audience', '').lower())
                and (mainFilter in each.get('title','').lower()
                        or mainFilter in each.get('desc','').lower()
                        or [eachTopic for eachTopic in each.get('topics', []) if mainFilter in eachTopic.lower()])
            ]
