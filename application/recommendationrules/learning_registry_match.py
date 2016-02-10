import re

class TargetUrlElements:
    def __init__(self, framework, area, level):
        self._framework = framework
        self._area = area
        self._level = level

    @property
    def framework(self):
        return self._framework

    @property
    def area(self):
        return self._area

    @property
    def level(self):
        return self._level


def __getTargetUrlElements(framework, targetUrl):
    targetUrlElements = targetUrl.split('#')
    if (len(targetUrlElements)!=3):
        return None
    return TargetUrlElements(framework, targetUrlElements[1], targetUrlElements[2])


def __matchCandidateNodes(framework, matchUrl, candidateUrl):
    # https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf#ProblemSolving#1
    candidateElement = __getTargetUrlElements(framework, candidateUrl)
    matchElement = __getTargetUrlElements(framework, matchUrl)
    
    if (candidateElement is None or matchElement is None):
        return None
    try:
        return candidateElement.area == matchElement.area and int(candidateElement.level) == int(matchElement.level) + 1
    except ValueError:
        return None

def __hasTargetedItem(matchitem, educationalAlignments): 
    for ea in educationalAlignments:
        if (    ea['alignmentType'] == 'teaches' 
                and ea['educationalFramework'] == matchitem.educationalFramework
                and __matchCandidateNodes(ea['educationalFramework'], matchitem.targetnode, ea['targetUrl'])):
            return True
    return False

def __maptype(item):
    if 'learningResourceType' in item:
        return item['learningResourceType'].lower()
    elif '@type' in item:
        return item['@type'].lower()
    else:
        return 'not defined'

def __matchitem(item, matchingitems):
    for matchitem in matchingitems:
        if ('educationalAlignment' in item
                and __hasTargetedItem(matchitem, item['educationalAlignment'])):
            return matchitem
    return None

def __formatdurationunit(item, unitlabel):
    item = int(item)
    if item == 0:
        return ''
    if item > 1:
        unitlabel = unitlabel + 's'
    return str(item) + ' ' + unitlabel + ' ' 

def __convertduration(duration):
    match = re.search('(-)?P(?:([\.,\d]+)Y)?(?:([\.,\d]+)M)?(?:([\.,\d]+)W)?(?:([\.,\d]+)D)?(?:T)?(?:([\.,\d]+)H)?(?:([\.,\d]+)M)?(?:([\.,\d]+)S)?', duration)
    return (match.group(2) + ' Years'    if match.group(2) is not None else '') + \
                (__formatdurationunit(match.group(3), 'Month') if match.group(3) is not None else  '')  + \
                (__formatdurationunit(match.group(4), 'Week') if match.group(4) is not None else  '') + \
                (__formatdurationunit(match.group(5), 'Day') if match.group(5) is not None else  '') + \
                (__formatdurationunit(match.group(6), 'Hour') if match.group(6) is not None else  '') + \
                (__formatdurationunit(match.group(7), 'Minute') if match.group(7) is not None else  '') + \
                (__formatdurationunit(match.group(8), 'Second') if match.group(8) is not None else  '')


def run(matchingitems, candidate_data_generator):
    """ Rule basically just looks for the next incremental item in the targetUrl """
    frameworks = {}
    for item in candidate_data_generator:
        matchedrule = __matchitem(item, matchingitems)
        if matchedrule is not None:
            tue = __getTargetUrlElements(matchedrule.educationalFramework, matchedrule.targetnode)
            level = int(tue.level)+1
            if matchedrule.educationalFramework not in frameworks:
                frameworks[matchedrule.educationalFramework] = { 'title' : matchedrule.educationalFramework, 'areas' : []}    
            area = [a for a in frameworks[matchedrule.educationalFramework]['areas'] if a["name"] == tue.area and a["level"] == level]
            if len(area) == 0:
                area = { 'name' : tue.area, 'level' : level, 'recommendations' : [] }
                frameworks[matchedrule.educationalFramework]['areas'].append(area)
            else:
                area = area[0]
            area["recommendations"].append( {'title' : item['name'], 'url' : item['url'], 'duration' : __convertduration(item['timeRequired']) if 'timeRequired' in item else '', 'type' : __maptype(item)} )
    return [ frameworks[f] for f in frameworks.keys() ] 

   
    


