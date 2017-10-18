def format_error(error):
    """例外errorを受け取り、'名前: メッセージ'の形式で返す"""
    return '{}: {}'.format(type(error).__name__, str(error))
