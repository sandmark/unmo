from collections import defaultdict
import morph
from markov import Markov
from util import format_error
import functools


class Dictionary:
    """思考エンジンの辞書クラス。

    クラス変数:
    DICT_RANDOM -- ランダム辞書のファイル名
    DICT_PATTERN -- パターン辞書のファイル名

    スタティックメソッド:
    make_pattern(str) -- パターン辞書読み込み用のヘルパー
    pattern_to_line(pattern) -- パターンハッシュをパターン辞書形式に変換する

    load_random(file) -- fileからランダム辞書の読み込みを行う
    load_pattern(file) -- fileからパターン辞書の読み込みを行う
    load_template(file) -- fileからテンプレート辞書の読み込みを行う
    load_markov(file) -- fileからマルコフ辞書の読み込みを行う

    プロパティ:
    random -- ランダム辞書
    pattern -- パターン辞書
    template -- テンプレート辞書
    """

    DICT = {'random': 'dics/random.txt',
            'pattern': 'dics/pattern.txt',
            'template': 'dics/template.txt',
            'markov': 'dics/markov.dat',
            }

    def __init__(self):
        """ファイルから辞書の読み込みを行う。"""
        self._random = Dictionary.load_random(Dictionary.DICT['random'])
        self._pattern = Dictionary.load_pattern(Dictionary.DICT['pattern'])
        self._template = Dictionary.load_template(Dictionary.DICT['template'])
        self._markov = Dictionary.load_markov(Dictionary.DICT['markov'])

    def study(self, text, parts):
        """ランダム辞書、パターン辞書、テンプレート辞書をメモリに保存する。"""
        self.study_random(text)
        self.study_pattern(text, parts)
        self.study_template(parts)
        self.study_markov(parts)

    def study_markov(self, parts):
        """形態素のリストpartsを受け取り、マルコフ辞書に学習させる。"""
        self._markov.add_sentence(parts)

    def study_template(self, parts):
        """形態素のリストpartsを受け取り、
        名詞のみ'%noun%'に変更した文字列templateをself._templateに追加する。
        名詞が存在しなかった場合、または同じtemplateが存在する場合は何もしない。

        >>> parts = morph.analyze('私はプログラムの女の子です')
        >>> d = Dictionary()
        >>> 3 not in d.template
        True
        >>> d.study_template(parts)
        >>> 3 in d.template
        True
        >>> d.template[3]
        ['%noun%は%noun%の%noun%です']
        """
        template = ''
        count = 0
        for word, part in parts:
            if morph.is_keyword(part):
                word = '%noun%'
                count += 1
            template += word

        if count > 0 and template not in self._template[count]:
            self._template[count].append(template)

    def study_random(self, text):
        """ユーザーの発言textをランダム辞書に保存する。
        すでに同じ発言があった場合は何もしない。"""
        if text not in self._random:
            self._random.append(text)

    def study_pattern(self, text, parts):
        """ユーザーの発言textを、形態素partsに基づいてパターン辞書に保存する。"""
        for word, part in parts:
            if not morph.is_keyword(part):  # 品詞が名詞でなければ学習しない
                continue

            # 単語の重複チェック
            # 同じ単語で登録されていれば、パターンを追加する
            # 無ければ新しいパターンを作成する
            duplicated = self._find_duplicated_pattern(word)
            if duplicated and text not in duplicated['phrases']:
                duplicated['phrases'].append(text)
            else:
                self._pattern.append({'pattern': word, 'phrases': [text]})

    def save(self):
        """メモリ上の辞書をファイルに保存する。"""
        self._save_random()
        self._save_pattern()
        self._save_template()
        self._markov.save(Dictionary.DICT['markov'])

    def save_dictionary(dict_key):
        """
        辞書を保存するためのファイルを開くデコレータ。
        dict_key - Dictionary.DICTのキー。
        """
        def _save_dictionary(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                with open(Dictionary.DICT[dict_key], 'w', encoding='utf-8') as f:
                    result = func(self, *args, **kwargs)
                    f.write(result)
                return result
            return wrapper
        return _save_dictionary

    @save_dictionary('template')
    def _save_template(self):
        """テンプレート辞書を保存する。"""
        lines = []
        for count, templates in self._template.items():
            for template in templates:
                lines.append('{}\t{}'.format(count, template))
        return '\n'.join(lines)

    @save_dictionary('pattern')
    def _save_pattern(self):
        """パターン辞書を保存する。"""
        lines = [Dictionary.pattern_to_line(p) for p in self._pattern]
        return '\n'.join(lines)

    @save_dictionary('random')
    def _save_random(self):
        """ランダム辞書を保存する。"""
        return '\n'.join(self.random)

    def _find_duplicated_pattern(self, word):
        """パターン辞書に名詞wordがあればパターンハッシュを、無ければNoneを返す。"""
        return next((p for p in self._pattern if p['pattern'] == word), None)

    @staticmethod
    def load_random(filename):
        """filenameをランダム辞書として読み込み、リストを返す。
        filenameのデフォルト値はDictionary.DICT['random']
        戻り値のリストが空である場合、['こんにちは']という一文を追加する。"""
        filename = filename if filename else Dictionary.DICT['random']
        lines = Dictionary.__load_file_as_lines(filename)
        return lines if lines else ['こんにちは']

    @staticmethod
    def load_pattern(filename=None):
        """filenameをパターン辞書として読み込み、リストを返す。
        filenameのデフォルト値はDictionary.DICT['pattern']"""
        filename = filename if filename else Dictionary.DICT['pattern']
        lines = Dictionary.__load_file_as_lines(filename)
        return [Dictionary.make_pattern(l) for l in lines]

    @staticmethod
    def load_template(filename=None):
        """filenameをテンプレート辞書として読み込み、ハッシュを返す。
        filenameのデフォルト値はDictionary.DICT['template']"""
        filename = filename if filename else Dictionary.DICT['template']
        templates = defaultdict(lambda: [])
        for line in Dictionary.__load_file_as_lines(filename):
            count, template = line.split('\t')
            if count and template:
                count = int(count)
                templates[count].append(template)
        return templates

    @staticmethod
    def __load_file_as_lines(filename):
        """filenameをutf-8で読み込み、改行で区切った文字列のリストを返す。
        例外IOErrorが発生した場合、詳細を標準出力へprintする。"""
        lines = []
        try:
            with open(filename, encoding='utf-8') as f:
                lines = f.read().splitlines()
        except IOError as e:
            print(format_error(e))
        finally:
            return lines

    @staticmethod
    def load_markov(filename):
        """Markovオブジェクトを生成し、filenameから読み込みを行う。"""
        markov = Markov()
        try:
            markov.load(filename)
        except IOError as e:
            print(format_error(e))
        return markov

    @staticmethod
    def pattern_to_line(pattern):
        """
        パターンのハッシュを文字列に変換する。

        >>> pattern = {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        >>> Dictionary.pattern_to_line(pattern)
        'Pattern\\tphrases|list'
        """
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))

    @staticmethod
    def make_pattern(line):
        """
        文字列lineを\tで分割し、{'pattern': [0], 'phrases': [1]}の形式で返す。
        [1]はさらに`|`で分割し、文字列のリストとする。

        >>> line = 'Pattern\\tphrases|list'
        >>> Dictionary.make_pattern(line)
        {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        """
        pattern, phrases = line.split('\t')
        if pattern and phrases:
            return {'pattern': pattern, 'phrases': phrases.split('|')}

    @property
    def random(self):
        """ランダム辞書"""
        return self._random

    @property
    def pattern(self):
        """パターン辞書"""
        return self._pattern

    @property
    def template(self):
        """テンプレート辞書"""
        return self._template

    @property
    def markov(self):
        """マルコフ辞書"""
        return self._markov
