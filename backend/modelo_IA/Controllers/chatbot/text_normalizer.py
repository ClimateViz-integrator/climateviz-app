import unicodedata

class TextNormalizer:
    @staticmethod
    def normalize_text(text):
        """Normaliza el texto quitando acentos y pasando a minúsculas"""
        text = text.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')
