from random import choice
from responder import WhatResponder, RandomResponder


class Unmo:
    """人工無脳コアクラス。

    プロパティ:
    name -- 人工無脳コアの名前
    responder_name -- 現在の応答クラスの名前
    """

    def __init__(self, name):
        """文字列を受け取り、コアインスタンスの名前に設定する。
        WhatResponder, RandomResponderインスタンスを作成し、保持する。
        """
        self._responders = {
            'what':   WhatResponder('What'),
            'random': RandomResponder('Random'),
        }
        self._name = name
        self._responder = self._responders['random']

    def dialogue(self, text):
        """ユーザーからの入力を受け取り、Responderに処理させた結果を返す。
        呼び出されるたびにランダムでResponderを切り替える。"""
        chosen_key = choice(list(self._responders.keys()))
        self._responder = self._responders[chosen_key]
        return self._responder.response(text)

    @property
    def name(self):
        """人工無脳インスタンスの名前"""
        return self._name

    @property
    def responder_name(self):
        """保持しているResponderの名前"""
        return self._responder.name
