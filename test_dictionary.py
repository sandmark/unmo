from nose.tools import eq_
from dictionary import Dictionary


class TestDictionary():
    TEST_PATTERN = {'pattern':
                    {'pattern': 'Test', 'phrases': ['This', 'is', 'test', 'phrases']},
                    'line': 'Test\tThis|is|test|phrases',
                    }

    def test_pattern_to_line(self):
        test_dict = TestDictionary.TEST_PATTERN['pattern']
        test_result = TestDictionary.TEST_PATTERN['line']
        eq_(Dictionary.pattern_to_line(test_dict), test_result)

    def test_make_pattern(self):
        test_line = TestDictionary.TEST_PATTERN['line']
        test_result = TestDictionary.TEST_PATTERN['pattern']
        eq_(Dictionary.make_pattern(test_line), test_result)
