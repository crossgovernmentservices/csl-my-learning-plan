import sys
import os
import json

import unittest

sys.path.append(os.path.join('..','..'))
import application.modules.lr_service as sut_service

class LRServiceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sut_service.DATA_FILEPATH = '../data/courses-for-search.json'

    def test_get_all_courses__when_called__should_return_all_courses(self):
        self.assertEqual(3, len(sut_service.get_all_courses()))


    def test_get_courses__when_filter_is_None__should_return_all_courses(self):
        self.assertEqual(3, len(sut_service.get_courses(None)))

    def test_get_courses__when_filter_has_no_keys__should_return_all_courses(self):
        self.assertEqual(3, len(sut_service.get_courses({})))

    def test_get_courses__when_filter_has_empty_value__should_return_all_courses(self):
        self.assertEqual(3, len(sut_service.get_courses({'filter': ''})))


    def test_get_courses__when_filter_contained_in_title__should_return_those_courses(self):
        actual_courses = sut_service.get_courses({'filter': 'with customers'})
        self.assertEqual(1, len(actual_courses))
        self.assertEqual("Communicating with customers", actual_courses[0]['title'])

    def test_get_courses__when_filter_contained_in_desc__should_return_those_courses(self):
        actual_courses = sut_service.get_courses({'filter': 'purpose of this'})
        self.assertEqual(1, len(actual_courses))
        self.assertEqual("The purpose of this e-learning", actual_courses[0]['desc'])

    def test_get_courses__when_filter_contained_in_topics__should_return_those_courses(self):
        actual_courses = sut_service.get_courses({'filter': 'rship & Man'})
        self.assertEqual(1, len(actual_courses))
        self.assertEqual("Change leaders for senior management", actual_courses[0]['title'])


    def test_get_courses__when_filtering__should_ignore_casing(self):
        actual_courses = sut_service.get_courses({'filter': 'IgiTal aWareNeS'})
        self.assertEqual(1, len(actual_courses))
        self.assertEqual("Digital awareness", actual_courses[0]['title'])


if __name__ == '__main__':
    unittest.main()
