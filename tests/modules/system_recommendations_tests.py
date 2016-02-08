import sys
import os
import json

import unittest

sys.path.append(os.path.join('..','..'))
from application.modules.system_recommendations import BasisItem, RecommendationBasis, recommend_resources

class SystemRecommendationsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def get_basic_candidatedata(self):
        data = [{   'audience': 'all',
            'alignmentType' : 'teaches', 
            'educationalFramework' : '1to5', 
            'targetUrl' : '1to5:4',
            'resourceUrl': 'http://1-5/4'
        }, {   'audience': 'all',
            'alignmentType' : 'teaches', 
            'educationalFramework' : '1to5', 
            'targetUrl' : '1to5:5',
            'resourceUrl': 'http://1-5/5'
        }]
        for i in data:
            yield i

    def get_dummypage_data(self):
        data = [ {'educationalFramework': 'basicproblemsolving', 'target':'5',
                'audience': 'all',
                 'name': 'staff forums', 'type': 'article', 'duration': 'PT15M', 'resourceUrl': 'http://test.com/item'},
                 {'educationalFramework': 'digitalskills', 'target':'4',
                'audience': 'all',
                 'name': 'word for dummies', 'type': 'course', 'duration': 'PT5M', 'resourceUrl': 'http://test.com/item2'},
                 {'educationalFramework': 'cooking', 'target':'3',
                'audience': 'all',
                 'name': 'thermomix scandal', 'type': 'course', 'duration': 'PT5M', 'resourceUrl': 'http://test.com/thermo'},
                 {'educationalFramework': 'cooking', 'target':'3',
                'audience': 'all',
                 'name': 'onions', 'type': 'course', 'duration': 'PT5M', 'resourceUrl': 'http://test.com/onions'}] 
        for i in data:
            yield i

    def get_learningregistry_items(self):
        from application.modules.lr_service import get_resources
        for i in get_resources():
            yield i


    def test_basic_single_recommendation_test(self):
        ''' Pick a single recommended resource from a list of three '''
        # Base the recommendations on a simple 1-5 scoring where we score 3 and want something of 4
        # to come back as a result
        
        # one single item to base on
        items = [BasisItem('all', '1to5', '1to5:3')]
        basis = RecommendationBasis('1to5', items)
        recommended = recommend_resources(basis, self.get_basic_candidatedata())
        self.assertEqual(1, len(recommended))
        self.assertEqual(recommended[0]['targetUrl'], '1to5:4')
        self.assertEqual(recommended[0]['resourceUrl'], 'http://1-5/4')


    def test_basic_two_recommendation_test(self):
        ''' Pick a single recommended resource from a list of three '''
        # Base the recommendations on a simple 1-5 scoring where we score 3 and want something of 4
        # to come back as a result
        
        # one single item to base on
        items = [BasisItem('all', '1to5', '1to5:3'), BasisItem('all', '1to5', '1to5:4')]
        basis = RecommendationBasis('1to5', items)
        recommended = recommend_resources(basis, self.get_basic_candidatedata())
        self.assertEqual(2, len(recommended))
        self.assertEqual(recommended[1]['targetUrl'], '1to5:5')
        self.assertEqual(recommended[1]['resourceUrl'], 'http://1-5/5')

    def test_first_dummy_page(self):
        items = [BasisItem('all', 'basicproblemsolving', '4')]
        basis = RecommendationBasis('dummypage', items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        self.assertEqual(1, len(recommendations))
        self.assertEqual(recommendations[0]['educationalFramework'], 'basicproblemsolving')
        self.assertEqual(1, len(recommendations[0]['recommendations']))
        # digital skills
        items = [BasisItem('all', 'digitalskills', '3')]
        basis = RecommendationBasis('dummypage', items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        self.assertEqual(1, len(recommendations))
        self.assertEqual(recommendations[0]['educationalFramework'], 'digitalskills')
        self.assertEqual(1, len(recommendations[0]['recommendations']))
        self.assertEqual('word for dummies', recommendations[0]['recommendations'][0]['name'])
        #cooking
        items = [BasisItem('all', 'cooking', '2')]
        basis = RecommendationBasis('dummypage', items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        self.assertEqual(1, len(recommendations))
        self.assertEqual(2, len(recommendations[0]['recommendations']))
        #cooking & digital
        items = [BasisItem('all', 'cooking', '2'), BasisItem('all', 'digitalskills', '3')]
        basis = RecommendationBasis('dummypage', items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        digitalrecs = [x['recommendations'] for x in recommendations if x['educationalFramework']=='digitalskills']
        self.assertEqual(1, len(digitalrecs[0]))
        cooking = [x['recommendations'] for x in recommendations if x['educationalFramework']=='cooking']
        self.assertEqual(2, len(cooking[0]))
        #dodo
        items = [BasisItem('all', 'dodo', '2'), BasisItem('all', 'klein', '3')]
        basis = RecommendationBasis('dummypage', items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        self.assertEqual(2, len(recommendations))
        self.assertEqual(0, len(recommendations[0]['recommendations']))
        self.assertEqual(0, len(recommendations[1]['recommendations']))


        
    def test_learning_registry_lookup_one_recommendation(self):
        items = [BasisItem('all', 'Civil Service Skills and Knowledge Framework', 'https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf#ProblemSolving#0')]
        basis = RecommendationBasis('learning_registry_match', items)
        recommendations = recommend_resources(basis, self.get_learningregistry_items())
        print(recommendations)
        self.assertEqual(1, len(recommendations))
        self.assertEqual('Civil Service Skills and Knowledge Framework', recommendations[0]['title'])
        self.assertEqual(1, len(recommendations[0]['areas']))
        self.assertEqual('ProblemSolving', recommendations[0]['areas'][0]['name'])
        self.assertEqual(1, recommendations[0]['areas'][0]['level'])
        self.assertEqual(1, len(recommendations[0]['areas'][0]['recommendations']))
        self.assertEqual('https://www.mindtools.com/pages/article/newCT_10.htm', recommendations[0]['areas'][0]['recommendations'][0]['url'])
    
    def test_learning_registry_lookup_two_recommendations_over_two_frameworks(self):
        items = [BasisItem('all', 'Civil Service Skills and Knowledge Framework', 'https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf#ProblemSolving#0'),
                BasisItem('all', 'Civil Service Skills and Knowledge Framework', 'https://civilservicelearning.civilservice.gov.uk/sites/default/files/policy_profession_skills_and_knowledge_framework_jan2013web.pdf#Communications#4')]
        basis = RecommendationBasis('learning_registry_match', items)
        recommendations = recommend_resources(basis, self.get_learningregistry_items())
        self.assertEqual(1, len(recommendations))
        self.assertEqual('Civil Service Skills and Knowledge Framework', recommendations[0]['title'])
        self.assertEqual(2, len(recommendations[0]['areas']))

        # Problem solving level 1
        ps = [r for r in recommendations[0]['areas'] if r['name'] == 'ProblemSolving']
        self.assertEqual(1, len(ps))
        ps = ps[0]
        self.assertEqual(1, ps['level'])
        self.assertEqual(1, len(ps['recommendations']))

        # Problem solving level 5
        c = [r for r in recommendations[0]['areas'] if r['name'] == 'Communications']
        self.assertEqual(1, len(c))
        c = c[0]
        self.assertEqual(5, c['level'])
        self.assertEqual(1, len(c['recommendations']))
    
    



if __name__ == '__main__':
    unittest.main()
