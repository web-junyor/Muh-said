# services.py
# -*- coding: utf-8 -*-

import re

# ======================
# 1. DICTIONARYLAR
# (SEN YUBORGAN KODNI BU YERGA O'ZGARTIRMAY QO'YASAN)
# ======================

LATIN_TO_CYRILLIC = {
    'a': 'а', 'A': 'А',
    'b': 'б', 'B': 'Б',
    'd': 'д', 'D': 'Д',
    'e': 'е', 'E': 'Е',
    'f': 'ф', 'F': 'Ф',
    'g': 'г', 'G': 'Г',
    'h': 'ҳ', 'H': 'Ҳ',
    'i': 'и', 'I': 'И',
    'j': 'ж', 'J': 'Ж',
    'k': 'к', 'K': 'К',
    'l': 'л', 'L': 'Л',
    'm': 'м', 'M': 'М',
    'n': 'н', 'N': 'Н',
    'o': 'о', 'O': 'О',
    'p': 'п', 'P': 'П',
    'q': 'қ', 'Q': 'Қ',
    'r': 'р', 'R': 'Р',
    's': 'с', 'S': 'С',
    't': 'т', 'T': 'Т',
    'u': 'у', 'U': 'У',
    'v': 'в', 'V': 'В',
    'x': 'х', 'X': 'Х',
    'y': 'й', 'Y': 'Й',
    'z': 'з', 'Z': 'З',
    'ʼ': 'ъ',
}

# (QOLGAN ULKAN DICTIONARYLARINGNI SHU YERGA QO‘YASAN – O‘ZGARTIRMA)

# ======================
# 2. ASOSIY FUNKSIYA
# ======================

def latin_to_cyrillic(text: str) -> str:
    """
    Lotin → Kirill
    Oddiy, tez, xatosiz
    """
    if not text:
        return ""

    result = []

    for char in text:
        result.append(LATIN_TO_CYRILLIC.get(char, char))

    return "".join(result)


def cyrillic_to_latin(text: str) -> str:
    """
    Kirill → Lotin (oddiy revers)
    """
    if not text:
        return ""

    reverse_map = {v: k for k, v in LATIN_TO_CYRILLIC.items()}
    result = []

    for char in text:
        result.append(reverse_map.get(char, char))

    return "".join(result)
