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
            area["recommendations"].append( {'title' : item['name'], 'url' : item['url'], 'duration' : item['duration'] if 'duration' in item else '', 'type' : __maptype(item)} )
    return [ frameworks[f] for f in frameworks.keys() ] 

   
    


