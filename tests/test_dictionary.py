from nose.tools import eq_, ok_
from unmo.dictionary import Dictionary
from unmo.morph import analyze, is_keyword


class TestDictionary:
    TEST_PATTERN = {'pattern':
                    {'pattern': 'Test', 'phrases': ['This', 'is', 'test', 'phrases']},
                    'line': 'Test\tThis|is|test|phrases',
                    }

    def setup(self):
        self.dictionary = Dictionary()

    def test_study_template_replace_nouns(self):
        """Dictionary#study_template: 形態素のリストを受け取り、名詞のみ%noun%に変換する"""
        parts = analyze('私はプログラムの女の子です')
        self.dictionary.study_template(parts)
        eq_(self.dictionary.template[3], ['%noun%は%noun%の%noun%です'])

    def test_study_template_count(self):
        """Dictionary#study_template: 名詞の数を辞書のインデックスにする"""
        parts = analyze('私はプログラムの女の子です')
        ok_(3 not in self.dictionary.template)
        self.dictionary.study_template(parts)
        ok_(3 in self.dictionary.template)

    def test_pattern_to_line(self):
        test_dict = TestDictionary.TEST_PATTERN['pattern']
        test_result = TestDictionary.TEST_PATTERN['line']
        eq_(Dictionary.pattern_to_line(test_dict), test_result)

    def test_make_pattern(self):
        test_line = TestDictionary.TEST_PATTERN['line']
        test_result = TestDictionary.TEST_PATTERN['pattern']
        eq_(Dictionary.make_pattern(test_line), test_result)

    def test_random(self):
        """Dictionary#random: デフォルトで['こんにちは']というリスト"""
        eq_(self.dictionary.random, ['こんにちは'])

    def test_study_random(self):
        """Dictionary#study_random: 発言を学習する"""
        sentense = 'Hello, World!'
        eq_(len(self.dictionary.random), 1)
        self.dictionary.study_random(sentense)
        eq_(len(self.dictionary.random), 2)

    def test_study_random_if_doubled(self):
        """Dictionary#study_random: 重複発言は学習しない"""
        sentense = 'Hello, World!'
        self.dictionary.study_random(sentense)
        eq_(len(self.dictionary.random), 2)
        self.dictionary.study_random(sentense)
        eq_(len(self.dictionary.random), 2)
