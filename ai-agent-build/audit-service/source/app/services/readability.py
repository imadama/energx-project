"""
Flesch-Douma score voor Nederlandse teksten.

Formule (Douma 1960, NL aanpassing van Flesch Reading Ease):
    score = 206.84 - (0.77 × ASW) - (0.93 × ASL)

waarin:
    ASW = aantal lettergrepen per 100 woorden
    ASL = gemiddelde zinslengte (woorden per zin)

Interpretatie:
    70+   zeer makkelijk leesbaar (lager onderwijs)
    60-70 makkelijk (mavo/havo)
    50-60 redelijk (havo/vwo)
    <50   complex (hoger onderwijs)
"""

import re


# Klinker-clusters voor lettergreep-schatting in NL
_VOWELS_NL = "aeiouyäëïöüáéíóúàèìòùâêîôû"
_SYLLABLE_PATTERN = re.compile(rf"[{_VOWELS_NL}]+", flags=re.IGNORECASE)


def count_syllables(word: str) -> int:
    """
    Schat het aantal lettergrepen in een Nederlands woord.

    Heuristiek: tel groepen aaneengesloten klinkers.
    Niet perfect voor leenwoorden, maar consistent genoeg voor Flesch-Douma.
    """
    if not word:
        return 0
    matches = _SYLLABLE_PATTERN.findall(word)
    return max(len(matches), 1)


def count_sentences(text: str) -> int:
    """Tel zinnen op basis van leestekens. Minimaal 1 (anders deelfout)."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    return max(len(sentences), 1)


def count_words(text: str) -> int:
    """Tel woorden — sequenties van alfabetische tekens."""
    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)


def flesch_douma(text: str) -> tuple[float | None, str]:
    """
    Bereken Flesch-Douma score voor een Nederlandse tekst.

    Returns (score, grade-omschrijving). Score None bij te weinig data.
    """
    if not text or len(text.strip()) < 50:
        return None, "Onvoldoende tekst voor analyse"

    word_count = count_words(text)
    sentence_count = count_sentences(text)

    if word_count < 10 or sentence_count < 1:
        return None, "Onvoldoende tekst voor analyse"

    # Lettergrepen tellen per woord
    words = re.findall(r"\b[\w'-]+\b", text)
    total_syllables = sum(count_syllables(w) for w in words)

    asw = (total_syllables / word_count) * 100  # lettergrepen per 100 woorden
    asl = word_count / sentence_count

    score = 206.84 - (0.77 * asw) - (0.93 * asl)
    score = round(score, 1)

    if score >= 70:
        grade = "Zeer makkelijk leesbaar (lager onderwijs)"
    elif score >= 60:
        grade = "Makkelijk leesbaar (mavo/havo) — doel voor Energx"
    elif score >= 50:
        grade = "Redelijk leesbaar (havo/vwo)"
    else:
        grade = "Complex (hoger onderwijs, vakliteratuur)"

    return score, grade
