#!/usr/bin/env python

# Note: this is not so error-prone for now, since we use a version with the old package name.
# Later, we need to make extremely sure we import the correct (older) version of SciATH,
# printing out enough to make this very clear if we make a mistake
import sys
import os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'sciath','lib')) # old location
import pyTestHarness as stablePackage
from pyTestHarness.version import getVersion as getStableVersion # old way to get version (later, just use sciath.__version__)
from pyTestHarness.harness import Harness
from pyTestHarness.test    import Test


# Make a path relative to this file absolute
def abs_path(path) :
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir,path)

def JobTest():
    t = Test('JobTest',1,'python ' + abs_path('./job/test_job.py'),abs_path('job/test_job.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

def JobSequenceTest():
    t = Test('JobSequenceTest',1,'python ' + abs_path('./job/test_jobsequence.py'),abs_path('job/test_jobsequence.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

def JobDAGTest():
    t = Test('JobDAGTest',1,'python ' + abs_path('./job/test_jobdag.py'),abs_path('job/test_jobdag.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

def main():
    print('SciATH Self-tests')
    print('Testing with version',getStableVersion(),'from',stablePackage.__file__)
    harness = Harness([JobTest(),JobSequenceTest(),JobDAGTest()])
    harness.execute()
    harness.verify()

if __name__ == "__main__":
    main()
