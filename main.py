class Responder:
    """AIの応答を制御するクラス。

    プロパティ:
    name -- Responderオブジェクトの名前
    """

    def __init__(self, name):
        """文字列を受け取り、自身のnameに設定する。"""
        self._name = name

    def response(self, text):
        """ユーザーからの入力(text)を受け取り、AIの応答を生成して返す。"""
        return '{}ってなに？'.format(text)

    @property
    def name(self):
        """応答オブジェクトの名前"""
        return self._name


class Unmo:
    """人工無脳コアクラス。

    プロパティ:
    name -- 人工無脳コアの名前
    responder_name -- 現在の応答クラスの名前
    """

    def __init__(self, name):
        """文字列を受け取り、コアインスタンスの名前に設定する。
        ’What' Responderインスタンスを作成し、保持する。
        """
        self._name = name
        self._responder = Responder('What')

    def dialogue(self, text):
        """ユーザーからの入力を受け取り、Responderに処理させた結果を返す。"""
        return self._responder.response(text)

    @property
    def name(self):
        """人工無脳インスタンスの名前"""
        return self._name

    @property
    def responder_name(self):
        """保持しているResponderの名前"""
        return self._responder.name


def build_prompt(unmo):
    """AIインスタンスを取り、AIとResponderの名前を整形して返す"""
    return '{name}:{responder}> '.format(name=unmo.name,
                                         responder=unmo.responder_name)


if __name__ == '__main__':
    print('Unmo System prototype : proto')
    proto = Unmo('proto')
    while True:
        text = input('> ')
        if not text:
            break

        response = proto.dialogue(text)
        print('{prompt}{response}'.format(prompt=build_prompt(proto),
                                          response=response))
