from .unmo import Unmo


def _build_prompt(unmo):
    """AIインスタンスを取り、AIとResponderの名前を整形して返す"""
    return '{name}:{responder}> '.format(name=unmo.name,
                                         responder=unmo.responder_name)


def main():
    print('Unmo System prototype : proto')
    proto = Unmo('proto')
    while True:
        text = input('> ')
        if not text:
            break

        response = proto.dialogue(text)
        print('{prompt}{response}'.format(prompt=_build_prompt(proto),
                                          response=response))
    proto.save()
