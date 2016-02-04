

def __constructtargetnode(item):
    print(item.targetnode)
    return str(min(int(item.targetnode)+1, 5))

def __matchitem(item, matchingitems):
    for matchitem in matchingitems:
        if (matchitem.educationalFramework == item['educationalFramework'] 
            and __constructtargetnode(matchitem) == item['target']
            and matchitem.audience == item['audience']):
            return True
    return False

def run(matchingitems, candidate_data_generator):
    """ Rule basically just looks for the next incremental item in the targetUrl """
    matcheditems = { f.educationalFramework : [] for f in matchingitems }
    print(matcheditems)
    for item in candidate_data_generator:
        if __matchitem(item, matchingitems):
            matcheditems[item['educationalFramework']].append(item)
    return [{'educationalFramework': f, 'recommendations': matcheditems[f]} for f in matcheditems.keys()]
    


