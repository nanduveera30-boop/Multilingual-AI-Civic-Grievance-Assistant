import importlib
import re

import streamlit as st


def load_translations(language_code: str) -> dict:
    try:
        module = importlib.import_module(f"translations.{language_code}")
        return getattr(module, "translations", {})
    except Exception:
        return {}


def get_text(key: str, default: str = None, **kwargs) -> str:
    translations = st.session_state.get("translations")
    if translations is None:
        language_code = st.session_state.get("language", "en")
        translations = load_translations(language_code)
        st.session_state["translations"] = translations
    text = translations.get(key, default if default is not None else key)
    if isinstance(text, str) and kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def translate_dynamic(prefix: str, value: str, default: str = None) -> str:
    if not value:
        return default or ""
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower())
    normalized = normalized.strip("_")
    return get_text(f"{prefix}_{normalized}", default or value)
