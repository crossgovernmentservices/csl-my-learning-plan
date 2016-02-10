import sys
import os
import json

import unittest

sys.path.append(os.path.join('..','..'))
import application.modules.diagnostic_service as sut_service
from application.modules.diagnostic_service import *


class DiagnosticServiceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass


    def test_get_score_for_multichoice_question(self):
        sut_question = Question(
            title='title_test',
            tag='tag_test',
            description='description_test',
            guide='guide_test',
            multichoice=True,
            choices=['option_1_test', 'option_2_test', 'option_3_test']
        )

        sut_question.answer = {'tag_test-1': '1'}
        self.assertEqual(2, sut_question.get_score())

        sut_question.answer = {'tag_test-1': '1', 'tag_test-2': '2'}
        self.assertEqual(4, sut_question.get_score())

        sut_question.answer = {'tag_test-1': '1', 'tag_test-2': '2', 'tag_test-3': '3'}
        self.assertEqual(5, sut_question.get_score())


    def test_get_score_for_singlechoice_question_with_3_options(self):
        sut_question = Question(
            title='title_test',
            tag='tag_test',
            description='description_test',
            guide='guide_test',
            multichoice=False,
            choices=['option_1_test', 'option_2_test', 'option_3_test'],
        )

        sut_question.answer = {'tag_test': '0'}
        self.assertEqual(5, sut_question.get_score())

        sut_question.answer = {'tag_test': '1'}
        self.assertEqual(3, sut_question.get_score())

        sut_question.answer = {'tag_test': '2'}
        self.assertEqual(0, sut_question.get_score())

    def test_get_score_for_singlechoice_question_with_4_options(self):
        sut_question = Question(
            title='title_test',
            tag='tag_test',
            description='description_test',
            guide='guide_test',
            multichoice=False,
            choices=['option_1_test', 'option_2_test', 'option_3_test', 'option_4_test'],
        )

        sut_question.answer = {'tag_test': '0'}
        self.assertEqual(5, sut_question.get_score())

        sut_question.answer = {'tag_test': '1'}
        self.assertEqual(4, sut_question.get_score())

        sut_question.answer = {'tag_test': '2'}
        self.assertEqual(2, sut_question.get_score())

        sut_question.answer = {'tag_test': '3'}
        self.assertEqual(0, sut_question.get_score())


if __name__ == '__main__':
    unittest.main()