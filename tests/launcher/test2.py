#!/usr/bin/python
import sciath._subprocess as subp

def example_1():
    ecode = subp.run(['echo','ccccaaaa'],None,None)
    print(ecode)

example_1()

