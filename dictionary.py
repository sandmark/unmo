from collections import defaultdict
import morph
from markov import Markov
from util import format_error


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
            if morph.is_keyword(part):  # 品詞が名詞であれば学習
                # 単語の重複チェック
                # 同じ単語で登録されていれば、パターンを追加する
                # 無ければ新しいパターンを作成する
                duplicated = next((p for p in self._pattern if p['pattern'] == word), None)
                if duplicated:
                    if text not in duplicated['phrases']:
                        duplicated['phrases'].append(text)
                else:
                    self._pattern.append({'pattern': word, 'phrases': [text]})

    def save(self):
        """メモリ上の辞書をファイルに保存する。"""
        with open(Dictionary.DICT['random'], mode='w', encoding='utf-8') as f:
            f.write('\n'.join(self.random))

        with open(Dictionary.DICT['pattern'], mode='w', encoding='utf-8') as f:
            f.write('\n'.join([Dictionary.pattern_to_line(p) for p in self._pattern]))

        with open(Dictionary.DICT['template'], mode='w', encoding='utf-8') as f:
            for count, templates in self._template.items():
                for template in templates:
                    f.write('{}\t{}\n'.format(count, template))

        self._markov.save(Dictionary.DICT['markov'])

    @staticmethod
    def load_random(filename):
        """filenameをランダム辞書として読み込み、リストを返す"""
        try:
            with open(filename, encoding='utf-8') as f:
                return [l for l in f.read().splitlines() if l]
        except IOError as e:
            print(format_error(e))
            return ['こんにちは']

    @staticmethod
    def load_pattern(filename):
        """filenameをパターン辞書として読み込み、リストを返す"""
        try:
            with open(filename, encoding='utf-8') as f:
                return [Dictionary.make_pattern(l) for l
                        in f.read().splitlines() if l]
        except IOError as e:
            print(format_error(e))
            return []

    @staticmethod
    def load_template(filename):
        """filenameをテンプレート辞書として読み込み、ハッシュを返す"""
        templates = defaultdict(lambda: [])
        try:
            with open(filename, encoding='utf-8') as f:
                for line in f:
                    count, template = line.strip().split('\t')
                    if count and template:
                        count = int(count)
                        templates[count].append(template)
            return templates
        except IOError as e:
            print(format_error(e))
            return templates

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
        """パターンのハッシュを文字列に変換する。"""
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))

    @staticmethod
    def make_pattern(line):
        """文字列lineを\tで分割し、{'pattern': [0], 'phrases': [1]}の形式で返す。
        [1]はさらに`|`で分割し、文字列のリストとする。"""
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
