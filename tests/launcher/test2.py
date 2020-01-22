#!/usr/bin/env python
import os
import sys
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess # To be removed once Python 2 is fully abandoned
else:
    import subprocess

def example_1():
    ctx = subprocess.run(['echo','ccccaaaa'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print(ctx.returncode)

example_1()

