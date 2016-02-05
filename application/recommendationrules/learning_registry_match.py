

def __hasTargetedItem(matchitem, educationalAlignments): 
    for ea in educationalAlignments:
        print(ea['targetUrl'] == matchitem.targetnode)
        print(ea['alignmentType'] == 'teaches')
        print(ea['educationalFramework'] == matchitem.educationalFramework)
        if (ea['alignmentType'] == 'teaches'
                and ea['educationalFramework'] == matchitem.educationalFramework
                and ea['targetUrl'] == matchitem.targetnode):
            print('Found!!')
            return True
    return False

def __matchitem(item, matchingitems):
    for matchitem in matchingitems:
        if ('educationalAlignment' in item
                and __hasTargetedItem(matchitem, item['educationalAlignment'])):
            return matchitem
    return None

def run(matchingitems, candidate_data_generator):
    """ Rule basically just looks for the next incremental item in the targetUrl """
    matcheditems = { f.educationalFramework : [] for f in matchingitems }
    print(matcheditems)
    for item in candidate_data_generator:
        matchedrule = __matchitem(item, matchingitems)
        if matchedrule is not None:
            print('Addning')
            print(item)
            matcheditems[matchedrule.educationalFramework].append(item)
    return [{'educationalFramework': f, 'recommendations': matcheditems[f]} for f in matcheditems.keys()]
    


