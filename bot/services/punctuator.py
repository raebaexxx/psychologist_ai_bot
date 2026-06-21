import re

COMMA_WORDS = [
    "а", "но", "и", "да", "или",
    "что", "чтобы", "потому", "поэтому", "так", "как", "который",
    "если", "хотя", "ведь", "причем", "притом",
    "and", "but", "or", "because", "so", "if",
    "although", "though", "which", "that",
    "when", "while", "since", "unless", "until",
]

COMMA_BEFORE = re.compile(
    r"\s+(" + "|".join(COMMA_WORDS) + r")\s", re.IGNORECASE
)

QUESTION_WORDS = re.compile(
    r"\b(как|что|почему|зачем|где|когда|куда|откуда|сколько|чей|кто|какой"
    r"|неужели|разве|how|what|why|where|when|which|who|does|did|is|are"
    r"|can|could|will|would|shall|should|may|might)\b",
    re.IGNORECASE,
)

SENTENCE_END = re.compile(r"(?<=[^.!?])\s+(?=[А-ЯA-Z])")


def restore_punctuation(text: str) -> str:
    text = text.strip()
    if not text:
        return text

    result = COMMA_BEFORE.sub(r", \1 ", text)
    result = SENTENCE_END.sub(". ", result)

    if QUESTION_WORDS.search(result):
        result = result.rstrip(".!?") + "?"

    result = re.sub(r",\s*,", ",", result)
    result = re.sub(r"\.\s*\.", ".", result)
    result = re.sub(r"\s+", " ", result).strip()
    result = result.strip(",")

    if not result.endswith((".", "!", "?")):
        result += "."

    return result
