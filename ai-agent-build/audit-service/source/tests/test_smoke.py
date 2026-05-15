"""Smoke tests — draait via `pytest tests/`. Test alleen pure functies, geen externe calls."""

import pytest

from app.services.readability import (
    count_sentences,
    count_syllables,
    count_words,
    flesch_douma,
)


def test_count_words():
    assert count_words("Een thuisbatterij is handig.") == 4
    assert count_words("") == 0


def test_count_sentences():
    assert count_sentences("Eerste zin. Tweede zin! Derde?") == 3
    assert count_sentences("Geen leesteken") == 1
    assert count_sentences("") == 1  # safety: nooit deelfout


def test_count_syllables():
    assert count_syllables("thuisbatterij") >= 3  # thuis-bat-te-rij (4)
    assert count_syllables("aan") == 1  # 'aa' = 1 klinker-cluster
    assert count_syllables("") == 0


def test_flesch_douma_too_short():
    score, grade = flesch_douma("Te kort.")
    assert score is None
    assert "Onvoldoende" in grade


def test_flesch_douma_easy_text():
    text = (
        "Dit is een makkelijke tekst. De zinnen zijn kort. "
        "De woorden zijn klein. Iedereen kan dit lezen. "
        "Het is heel duidelijk. Geen moeilijke woorden. "
        "Lezen is leuk. Schrijven ook. Maak het simpel. "
        "Korte zinnen helpen je lezer. Dan snapt iedereen het."
    )
    score, grade = flesch_douma(text)
    assert score is not None
    assert score > 60, f"Eenvoudige tekst zou hoog moeten scoren, kreeg {score}"


def test_flesch_douma_complex_text():
    text = (
        "De implementatie van de salderingsregeling kent vele juridische en fiscale "
        "complicaties die voortvloeien uit de wisselwerking tussen verschillende "
        "Europese richtlijnen en nationale wetgevingskaders. De interpretatie "
        "van de hierboven beschreven complicaties vereist gedegen expertise."
    )
    score, _ = flesch_douma(text)
    assert score is not None
    assert score < 60, f"Complexe tekst zou laag moeten scoren, kreeg {score}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
