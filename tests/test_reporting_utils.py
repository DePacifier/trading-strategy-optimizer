import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytz
from reporting.utils import convert_to_eat, ffloat, fpos

def test_convert_to_eat_valid():
    result = convert_to_eat("2023-01-11 00:00:00")
    assert result == "23/01/11 03:00"

def test_convert_to_eat_none():
    assert convert_to_eat(None) == ""

def test_ffloat_valid():
    assert ffloat(1.23456) == 1.2346

def test_ffloat_invalid():
    assert ffloat("abc") is None

def test_fpos():
    assert fpos(1) == "LONG \u2206"
    assert fpos(-1) == "SHORT \u2207"
