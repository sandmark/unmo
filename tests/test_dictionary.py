"""
Dictionaryクラスのテストを行うモジュール
"""
import os
from pathlib import Path
import shutil
import re
from nose.tools import eq_, ok_, with_setup
from unmo.dictionary import Dictionary
from unmo.morph import analyze


HOME = str(Path.home())


def remove_dic():
    """辞書ファイルを削除する"""
    if os.path.isdir(Dictionary.DICT_DIR):
        shutil.rmtree(Dictionary.DICT_DIR)


@with_setup(setup=remove_dic)
def test_init():
    """Dictionary: 辞書ファイルが無くても読み込みできる"""
    Dictionary()


@with_setup(setup=remove_dic, teardown=remove_dic)
def test_dictionary_dir():
    """Dictionary#save: 辞書ファイルは~/.unmo/dics/に保存する"""
    sentense = 'こんにちは'
    parts = analyze(sentense)
    d = Dictionary()
    d.study(sentense, parts)
    d.save()
    dics_dir = os.path.join(HOME, '.unmo', 'dics')
    ok_(os.path.isdir(dics_dir))


@with_setup(setup=remove_dic, teardown=remove_dic)
def test_random_save_and_load():
    """Dictionary#random: 保存した辞書を読み込める"""
    sentense = 'Hello'
    d1 = Dictionary()
    d1.study_random(sentense)
    d1.save()
    d2 = Dictionary()
    ok_(sentense in d2.random)


@with_setup(setup=remove_dic, teardown=remove_dic)
def test_pattern_save_and_load():
    """Dictionary#pattern: 保存した辞書を読み込める"""
    word = '名詞'
    sentense = '名詞です'
    parts = analyze(sentense)
    d1 = Dictionary()
    d1.study_pattern(sentense, parts)
    d1.save()
    d2 = Dictionary()
    patterns = [ptn for ptn in d2.pattern if re.search(ptn['pattern'], sentense)]
    eq_(len(patterns), 1)
    ok_(patterns[0], {'pattern': word, 'phrases': [sentense]})


@with_setup(setup=remove_dic, teardown=remove_dic)
def test_template_save_and_load():
    """Dictionary#template: 保存した辞書を読み込める"""
    sentense = '私はプログラムの女の子です'
    result = '%noun%は%noun%の%noun%です'
    parts = analyze(sentense)
    d1 = Dictionary()
    d1.study_template(parts)
    d1.save()
    d2 = Dictionary()
    ok_(d2.template[3] == [result])


@with_setup(setup=remove_dic, teardown=remove_dic)
def test_markov_save_and_load():
    """Dictionary#markov: 保存した辞書を読み込める"""
    sentense = '私はプログラムの女の子です'
    parts = analyze(sentense)
    d1 = Dictionary()
    d1.study_markov(parts)
    d1.save()
    d2 = Dictionary()
    ok_(d2.markov.generate('私').startswith('私は'))


def test_pattern_to_line():
    """Dictionary.pattern2line: パターンハッシュを一行の文字列にする"""
    test_dict = {'pattern': 'Test', 'phrases': ['This', 'is', 'test', 'phrases']}
    test_result = 'Test\tThis|is|test|phrases'
    eq_(Dictionary.pattern2line(test_dict), test_result)


def test_line2pattern():
    """Dictionary.line2pattern: 一行の文字列からパターンハッシュを作る"""
    test_line = 'Test\tThis|is|test|phrases'
    test_result = {'pattern': 'Test', 'phrases': ['This', 'is', 'test', 'phrases']}
    eq_(Dictionary.line2pattern(test_line), test_result)


def test_dicfile():
    """Dictionary.dicfile: 辞書ファイルのフルパスを返す"""
    for key in ('random', 'pattern', 'template', 'markov'):
        ext = '.txt' if not key == 'markov' else '.dat'
        eq_(Dictionary.dicfile(key), os.path.join(Dictionary.DICT_DIR, key) + ext)


class TestDictionary:
    """Dictionaryオブジェクトのメソッドテスト"""

    def setup(self):
        self.dictionary = Dictionary()

    def teardown(self):
        remove_dic()

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

    def test_study_template(self):
        """Dictionary#study_template: テンプレートを学習する"""
        eq_(len(self.dictionary.template), 0)
        parts = analyze('テンプレートを学習する')
        self.dictionary.study_template(parts)
        eq_(len(self.dictionary.template), 1)
        eq_(self.dictionary.template[2], ['%noun%を%noun%する'])

    def test_study_template_with_same_template(self):
        """Dictionary#study_template: 同じテンプレートは学習しない"""
        parts1 = analyze('テンプレートを学習する')
        parts2 = analyze('プログラムを作成する')
        self.dictionary.study_template(parts1)
        self.dictionary.study_template(parts2)
        eq_(len(self.dictionary.template), 1)
        eq_(self.dictionary.template[2], ['%noun%を%noun%する'])

    def test_study_template_without_nouns(self):
        """Dictionary#study_template: 名詞がなければ学習しない"""
        parts = analyze('実はさっきから寒い')
        self.dictionary.study_template(parts)
        eq_(len(self.dictionary.template), 0)

    def test_study_pattern(self):
        """Dictionary#study_pattern: 名詞の数だけパターンを学習する"""
        sentense = '名詞の数だけパターンを学習する'
        parts = analyze(sentense)
        self.dictionary.study_pattern(sentense, parts)
        eq_(len(self.dictionary.pattern), 4)
        nouns = ['名詞', '数', 'パターン', '学習']
        for pattern in self.dictionary.pattern:
            ok_(pattern['pattern'] in nouns)
            eq_(pattern['phrases'], [sentense])

    def test_study_pattern_without_nouns(self):
        """Dictionary#study_pattern: 名詞がなければ学習しない"""
        sentense = '実はさっきから寒い'
        parts = analyze(sentense)
        self.dictionary.study_pattern(sentense, parts)
        eq_(len(self.dictionary.pattern), 0)

    def test_study_pattern_with_same_word(self):
        """Dictionary#study_pattern: 同じ単語があれば追加する"""
        sentenses = ['波が立つ', '波が引く']
        parts_per_sentense = [analyze(s) for s in sentenses]
        for sentense, parts in zip(sentenses, parts_per_sentense):
            self.dictionary.study_pattern(sentense, parts)
        eq_(len(self.dictionary.pattern), 1)
        eq_(self.dictionary.pattern[0]['pattern'], '波')
        for i, sentense in enumerate(sentenses):
            eq_(self.dictionary.pattern[0]['phrases'][i], sentense)

    def test_save(self):
        """Dictionary#save: 正常に保存できる"""
        self.dictionary.save()

    def test_study(self):
        """Dictionary#study: すべての辞書に学習させる"""
        sentense = '私はプログラムの女の子です'
        parts = analyze(sentense)
        self.dictionary.study(sentense, parts)
        eq_(len(self.dictionary.random), 2)          # デフォルト + 1
        eq_(len(self.dictionary.pattern), 3)         # 名詞の数
        eq_(len(self.dictionary.template), 1)        # template[3]
        eq_(len(self.dictionary.markov._starts), 1)  # _starts['私']
