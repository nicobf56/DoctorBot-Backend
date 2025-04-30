from deep_translator import GoogleTranslator
from langdetect import detect

def detect_language(text):
    """Detecta el idioma del texto utilizando langdetect."""
    return detect(text)  # Ahora usa langdetect en lugar de deep-translator

def translate_text(text, target_lang):
    """Traduce un texto al idioma especificado usando Google Translator."""
    return GoogleTranslator(source='auto', target=target_lang).translate(text)
