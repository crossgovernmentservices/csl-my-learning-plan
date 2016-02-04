
class BasisItem(object):
	""" """
	def __init__(self, audience, educationalFramework, targetnode):
		self._audience = audience
		self._educationalFramework = educationalFramework
		self._targetnode = targetnode

	@property
	def activity(self):
	    return self._activity

	@property
	def audience(self):
	    return self._audience

	@property
	def educationalFramework(self):
	    return self._educationalFramework

	@property
	def targetnode(self):
	    return self._targetnode

class RecommendationBasis(object):
	""" """
	def __init__(self, rule, items):
		self._rule = rule
		self._items = items

	@property
	def rule(self):
	    return self._rule

	@property
	def items(self):
	    return self._items


def recommend_resources(base_info, candidate_data_generator):
	rulemodule = __import__('application.recommendationrules.' + base_info.rule, globals(), locals(), ['run'])
	return rulemodule.run(base_info.items, candidate_data_generator)
	
