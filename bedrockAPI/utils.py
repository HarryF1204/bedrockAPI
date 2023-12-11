import re


def to_pascal_case(text):
    text = re.split('[_-]+', text)
    text = ''.join([x[0].upper() + x[1:] for x in text])
    return text



def to_camel_case(text):
    text = re.sub(r"([_-])+", " ", text).title().replace(" ", "")
    return ''.join([text[0].lower(), text[1:]])


def to_snake_case(text):
    return re.sub(r"[\s\-]+", "_", text.lower())

