from utils.helpers import load_translations


def detect_language(text: str) -> str:
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "hi"
    if any("\u0C00" <= ch <= "\u0C7F" for ch in text):
        return "te"
    return "en"


def translate(text: str, target_language: str) -> str:
    if target_language == "en":
        return text
    translations = load_translations(target_language)
    for key, value in translations.items():
        text = text.replace(key, value)
    return text
