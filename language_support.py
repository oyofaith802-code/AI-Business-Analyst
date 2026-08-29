# ============================================================
# MULTILINGUAL LANGUAGE SUPPORT
# ============================================================

import re

try:
    from langdetect import detect
except ImportError:
    detect = None


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "de": "German",
    "it": "Italian",
    "nl": "Dutch",
    "ru": "Russian",
    "uk": "Ukrainian",
    "ar": "Arabic",
    "tr": "Turkish",
    "pl": "Polish",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi",
    "sw": "Swahili",
}


# ============================================================
# LANGUAGE NAME
# ============================================================

def get_language_name(language_code):

    if not language_code:
        return "English"

    language_code = language_code.lower()

    return SUPPORTED_LANGUAGES.get(
        language_code,
        "English"
    )


# ============================================================
# DETECT LANGUAGE
# ============================================================

def detect_language(text):

    if not text or not text.strip():
        return "en"

    text = text.strip()

    # --------------------------------------------------------
    # Use langdetect when available
    # --------------------------------------------------------

    if detect is not None:

        try:

            language = detect(text)

            if language in SUPPORTED_LANGUAGES:
                return language

        except Exception:
            pass

    # --------------------------------------------------------
    # Basic fallback detection
    # --------------------------------------------------------

    lower_text = text.lower()

    # Arabic characters
    if re.search(r"[\u0600-\u06ff]", text):
        return "ar"

    # Chinese characters
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh-cn"

    # Japanese characters
    if re.search(r"[\u3040-\u30ff]", text):
        return "ja"

    # Korean characters
    if re.search(r"[\uac00-\ud7af]", text):
        return "ko"

    # Russian / Ukrainian
    if re.search(r"[\u0400-\u04ff]", text):

        ukrainian_words = [
            "що",
            "який",
            "яка",
            "дохід",
            "продажі",
            "місяць"
        ]

        if any(
            word in lower_text
            for word in ukrainian_words
        ):
            return "uk"

        return "ru"

    # French
    french_words = [
        "quel",
        "quelle",
        "quels",
        "quelles",
        "revenu",
        "revenus",
        "chiffre",
        "affaires",
        "ventes",
        "mois"
    ]

    if any(
        word in lower_text
        for word in french_words
    ):
        return "fr"

    # Spanish
    spanish_words = [
        "qué",
        "cuál",
        "cuáles",
        "ingresos",
        "ventas",
        "mes",
        "categoría"
    ]

    if any(
        word in lower_text
        for word in spanish_words
    ):
        return "es"

    # Portuguese
    portuguese_words = [
        "qual",
        "quais",
        "receita",
        "vendas",
        "mês",
        "categoria"
    ]

    if any(
        word in lower_text
        for word in portuguese_words
    ):
        return "pt"

    # German
    german_words = [
        "welche",
        "unser",
        "umsatz",
        "verkauf",
        "monat",
        "kategorie"
    ]

    if any(
        word in lower_text
        for word in german_words
    ):
        return "de"

    # Italian
    italian_words = [
        "quale",
        "quali",
        "ricavi",
        "vendite",
        "mese",
        "categoria"
    ]

    if any(
        word in lower_text
        for word in italian_words
    ):
        return "it"

    return "en"


# ============================================================
# GET LANGUAGE INSTRUCTION
# ============================================================

def get_language_instruction(language_code):

    language_name = get_language_name(
        language_code
    )

    return f"""
The user's preferred response language is {language_name}.

Important rules:

- Understand the user's question in their language.
- Translate the business intent internally when necessary.
- Use the actual database schema.
- Never invent database columns.
- Never translate database table names or column names when generating SQL.
- SQL must use the exact database table and column names.
- Return the business explanation in {language_name}.
- Preserve product names, category names, and other database values.
- Preserve numbers accurately.
- Do not invent facts.
- Keep the answer professional and concise.
"""


# ============================================================
# BUILD MULTILINGUAL AI PROMPT
# ============================================================

def build_multilingual_prompt(
    question,
    result_text,
    language_code
):

    language_name = get_language_name(
        language_code
    )

    instruction = get_language_instruction(
        language_code
    )

    prompt = f"""
You are a professional AI Business Analyst.

{instruction}

User question:
{question}

Database result:
{result_text}

Your task:

1. Understand the user's business question.
2. Answer using ONLY the database result.
3. Do not invent numbers.
4. Do not invent facts.
5. Preserve database values exactly.
6. Explain the result in {language_name}.
7. Give one useful business insight.

Format:

Answer:

[direct answer]

Business insight:

[useful business insight]
"""

    return prompt


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MULTILINGUAL LANGUAGE SUPPORT TEST")
    print("=" * 60)

    test_questions = [

        "What is our revenue by category?",

        "Quel est notre chiffre d'affaires par catégorie ?",

        "¿Cuáles son nuestros ingresos por categoría?",

        "Qual é a nossa receita por categoria?",

        "Wie hoch ist unser Umsatz nach Kategorie?",

        "ما هي إيراداتنا حسب الفئة؟",

        "Какая у нас выручка по категориям?",

        "Quali sono i nostri ricavi per categoria?"

    ]

    for question in test_questions:

        language = detect_language(
            question
        )

        language_name = get_language_name(
            language
        )

        print()
        print(
            f"Question: {question}"
        )

        print(
            f"Detected language: "
            f"{language} "
            f"({language_name})"
        )