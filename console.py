import codecs
import os


def text_create(name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "mylog")
    os.makedirs(log_dir, exist_ok=True)
    full_path = os.path.join(log_dir, f"{name}.txt")
    return full_path


def convert_encoding(message):
    try:
        # 假設輸入是 cp950 編碼
        return message.encode('cp950').decode('utf-8')
    except UnicodeEncodeError:
        # 如果無法用 cp950 編碼，可能已經是 utf-8，直接返回
        return message


def log_message(message):
    filename = 'log'
    log_path = text_create(filename)

    # 轉換編碼
    utf8_message = convert_encoding(message)

    with codecs.open(log_path, 'w', encoding='utf-8') as outputfile:
        print(utf8_message, file=outputfile)

    return utf8_message
