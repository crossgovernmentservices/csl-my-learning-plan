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
                 'name': 'staff forums', 'type': 'article', 'duration': 'PT15M', 'resourceUrl': 'http://test.com/item'}] 
        for i in data:
            yield i


    def test_basic_single_recommendation_test(self):
        """ Pick a single recommended resource from a list of three """
        # Base the recommendations on a simple 1-5 scoring where we score 3 and want something of 4
        # to come back as a result
        
        # one single item to base on
        items = [BasisItem('all', '1to5', '1to5:3')]
        basis = RecommendationBasis("1to5", items)
        recommended = recommend_resources(basis, self.get_basic_candidatedata())
        self.assertEqual(1, len(recommended))
        self.assertEqual(recommended[0]['targetUrl'], '1to5:4')
        self.assertEqual(recommended[0]['resourceUrl'], 'http://1-5/4')


    def test_basic_two_recommendation_test(self):
        """ Pick a single recommended resource from a list of three """
        # Base the recommendations on a simple 1-5 scoring where we score 3 and want something of 4
        # to come back as a result
        
        # one single item to base on
        items = [BasisItem('all', '1to5', '1to5:3'), BasisItem('all', '1to5', '1to5:4')]
        basis = RecommendationBasis("1to5", items)
        recommended = recommend_resources(basis, self.get_basic_candidatedata())
        self.assertEqual(2, len(recommended))
        self.assertEqual(recommended[1]['targetUrl'], '1to5:5')
        self.assertEqual(recommended[1]['resourceUrl'], 'http://1-5/5')

    def test_first_dummy_page(self):
        items = [BasisItem('all', 'basicproblemsolving', '4')]
        basis = RecommendationBasis("dummypage", items)
        recommendations = recommend_resources(basis, self.get_dummypage_data())
        self.assertEqual(1, len(recommendations))
        self.assertEqual(recommendations[0]['educationalFramework'], 'basicproblemsolving')
        self.assertEqual(1, len(recommendations[0]['recommendations']))
        
        
        

if __name__ == '__main__':
    unittest.main()
