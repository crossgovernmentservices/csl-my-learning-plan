

def __constructtargetnode(item):
    return 'basicproblemsolving:'+str(min(int(item.targetnode.split(':')[1])+1, 5))

def __matchitem(item, matchingitems):
    for matchitem in matchingitems:
        if (matchitem.educationalFramework == item['educationalFramework'] 
            and __constructtargetnode(matchitem) == item['targetUrl']
            and matchitem.audience == item['audience']):
            return True
    return False

def run(matchingitems, candidate_data_generator):
    """ Rule basically just looks for the next incremental item in the targetUrl """
    matcheditems = []
    for item in candidate_data_generator:
        if __matchitem(item, matchingitems):
            matcheditems.append(item)
    return matcheditems
    


