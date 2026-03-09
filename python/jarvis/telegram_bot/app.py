# -*- coding: utf-8 -*-
"""Botni ishga tushirish: python app.py"""
import os
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)
os.chdir(_BASE)

if __name__ == "__main__":
    from main import main
    main()
