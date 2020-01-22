# Defines a class which behaves like an Enum (Python 3.4+)
# But also supports some operations with earlier versions of Python
# It is used just like Enum, except that values must be assigned
# Using Enum23Value(), not directly, for example
#
# class MyEnum(Enum23):
#    FOO = Enum23Value('foo')
#
# If Python <3.4 support is dropped, Enum23 can be directly replaced
# with Enum, and Enum23Value() can be removed

import sys

if sys.version_info[0] >= 3 and sys.version_info[1] >= 4:
    from enum import Enum

    def Enum23Value(x):
        return x

    Enum23 = Enum
else:
    class Enum23Value:
        """ A wrapper class which allows one to access a value field """
        def __init__(self, value): self.__dict__.update(value=value)

    Enum23 = object
