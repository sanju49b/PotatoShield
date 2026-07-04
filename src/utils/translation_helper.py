from langchain_openai import ChatOpenAI
from functools import lru_cache

LANGUAGE_NAMES = {
    "hindi": "Hindi (हिंदी)",
    "telugu": "Telugu (తెలుగు)",
    "tamil": "Tamil (தமிழ்)"
}


@lru_cache(maxsize=1)
def get_translation_llm():
    """Return a cached translation LLM instance."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def translate_text(text: str, language_code: str) -> str:
    """
    Translate English text into the specified target language.
    Returns translated text or None if translation not needed/available.
    """
    if not text or not language_code or language_code.lower() == "english":
        return None
    language_code = language_code.lower()
    if language_code not in LANGUAGE_NAMES:
        return None

    target_language = LANGUAGE_NAMES[language_code]
    prompt = f"""You are a professional agricultural translator.

Translate the following English text into {target_language}.

Guidelines:
1. Preserve the tone and intent.
2. Keep technical agricultural terms accurate.
3. Maintain formatting (line breaks, bullet points).
4. Do NOT add extra commentary—return only the translated text.

English text:
{text}

Provide only the translated text in {target_language}."""

    llm = get_translation_llm()
    response = llm.invoke(prompt)
    return response.content.strip()
