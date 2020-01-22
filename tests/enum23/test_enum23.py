#!/usr/bin/env python

# Run e.g.
#  python -m pytest this_file.py

import pytest

from sciath._enum23 import Enum23, Enum23Value

def test_enum_value_equality():
    class MyEnum(Enum23):
        FOO = Enum23Value('foo')

    x = MyEnum.FOO
    assert(x == MyEnum.FOO)

def test_enum_value():
    class MyEnum(Enum23):
        FOO = Enum23Value('foo')
        BAR = Enum23Value('bar')

    x = MyEnum.FOO
    assert(x.value == 'foo')
    y = MyEnum.BAR
    assert(y.value == 'bar')
