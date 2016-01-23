import json
from application.config import Config

DATA_FILEPATH='application/data/courses-for-search.json'

def get_all_courses():
    with open(DATA_FILEPATH) as data_file:
        courses = json.load(data_file)
    return courses

def get_courses(filterDict):
    all_courses = get_all_courses()
    filterStr = ('' if filterDict is None else filterDict.get('filter', '')).lower()
    
    if filterStr:
        return [each for each in all_courses
                if filterStr in each.get('title','').lower()
                or filterStr in each.get('desc','').lower()
                or [eachTopic for eachTopic in each.get('topics', []) if filterStr in eachTopic.lower()]
            ]
    else:
        return all_courses
