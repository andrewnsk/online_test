from __future__ import unicode_literals
import unittest
import os
import shutil
import tempfile

from yaksh import code_evaluator
from yaksh.code_evaluator import CodeEvaluator
from yaksh.scilab_code_evaluator import ScilabCodeEvaluator
from yaksh.settings import SERVER_TIMEOUT

class ScilabEvaluationTestCases(unittest.TestCase):
    def setUp(self):
        tmp_in_dir_path = tempfile.mkdtemp()
        self.test_case_data = [{"test_case": "scilab_files/test_add.sce",
                                "test_case_type": "standardtestcase",
                                "weight": 0.0
                                }]
        self.in_dir = tmp_in_dir_path
        self.timeout_msg = ("Code took more than {0} seconds to run. "
                            "You probably have an infinite loop" 
                            " in your code.").format(SERVER_TIMEOUT)
        code_evaluator.SERVER_TIMEOUT = 9
        self.file_paths = None

    def tearDown(self):
        code_evaluator.SERVER_TIMEOUT = 4
        shutil.rmtree(self.in_dir)

    def test_correct_answer(self):
        user_answer = ("funcprot(0)\nfunction[c]=add(a,b)"
                        "\n\tc=a+b;\nendfunction")
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'scilab'
                    },
                    'test_case_data': self.test_case_data,
                  }

        evaluator = CodeEvaluator(self.in_dir)
        result = evaluator.evaluate(kwargs)

        self.assertEqual(result.get('error'), "Correct answer\n")
        self.assertTrue(result.get('success'))

    def test_error(self):
        user_answer = ("funcprot(0)\nfunction[c]=add(a,b)"
                        "\n\tc=a+b;\ndis(\tendfunction")
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'scilab'
                    },
                    'test_case_data': self.test_case_data,
                  }

        evaluator = CodeEvaluator(self.in_dir)
        result = evaluator.evaluate(kwargs)

        self.assertFalse(result.get("success"))
        self.assertTrue('error' in result.get("error"))


    def test_incorrect_answer(self):
        user_answer = ("funcprot(0)\nfunction[c]=add(a,b)"
                        "\n\tc=a-b;\nendfunction")
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'scilab'
                    },
                    'test_case_data': self.test_case_data,
                  }

        evaluator = CodeEvaluator(self.in_dir)
        result = evaluator.evaluate(kwargs)

        lines_of_error = len(result.get('error').splitlines())
        self.assertFalse(result.get('success'))
        self.assertIn("Message", result.get('error'))
        self.assertTrue(lines_of_error > 1)

    def test_infinite_loop(self):
        code_evaluator.SERVER_TIMEOUT = 4
        user_answer = ("funcprot(0)\nfunction[c]=add(a,b)"
                        "\n\tc=a;\nwhile(1==1)\nend\nendfunction")
        kwargs = {
                  'metadata': {
                    'user_answer': user_answer,
                    'file_paths': self.file_paths,
                    'partial_grading': False,
                    'language': 'scilab'
                    },
                    'test_case_data': self.test_case_data,
                  }

        evaluator = CodeEvaluator(self.in_dir)
        result = evaluator.evaluate(kwargs)

        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("error"), self.timeout_msg)

if __name__ == '__main__':
    unittest.main()
