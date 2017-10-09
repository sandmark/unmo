from random import choice, randrange
from responder import WhatResponder, RandomResponder, PatternResponder
from dictionary import Dictionary


class Unmo:
    """人工無脳コアクラス。

    プロパティ:
    name -- 人工無脳コアの名前
    responder_name -- 現在の応答クラスの名前
    """

    def __init__(self, name):
        """文字列を受け取り、コアインスタンスの名前に設定する。
        Responder(What, Random, Pattern)インスタンスを作成し、保持する。
        Dictionaryインスタンスを作成し、保持する。
        """
        self._dictionary = Dictionary()

        self._responders = {
            'what':   WhatResponder('What', self._dictionary),
            'random': RandomResponder('Random', self._dictionary),
            'pattern': PatternResponder('Pattern', self._dictionary),
        }
        self._name = name
        self._responder = self._responders['pattern']

    def dialogue(self, text):
        """ユーザーからの入力を受け取り、Responderに処理させた結果を返す。
        呼び出されるたびにランダムでResponderを切り替える。
        入力をDictionaryに学習させる。"""
        chance = randrange(0, 100)
        if chance in range(0, 59):
            self._responder = self._responders['pattern']
        elif chance in range(60, 89):
            self._responder = self._responders['random']
        else:
            self._responder = self._responders['what']

        response = self._responder.response(text)
        self._dictionary.study(text)
        return response

    @property
    def name(self):
        """人工無脳インスタンスの名前"""
        return self._name

    @property
    def responder_name(self):
        """保持しているResponderの名前"""
        return self._responder.name
