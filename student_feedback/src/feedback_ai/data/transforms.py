import unicodedata
def unaccent(text):
    if not isinstance(text, str):
        raise TypeError('text must be str')
    decomposed = unicodedata.normalize('NFD', unicodedata.normalize('NFC', text))
    return unicodedata.normalize('NFC', ''.join(c for c in decomposed if not unicodedata.combining(c)).translate(str.maketrans({'đ': 'd', 'Đ': 'D'})))
