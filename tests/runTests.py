#!/usr/bin/env python

# Note that these are NOT well-done. These are put quickly in place
# to help us refactor, and should later be replaced using a newer version of SciATH!

# Note: At the time of this writing, there are no parallel tests here

# Note: this is not so error-prone for now, since we use a version with the old package name.
# Later, we need to make extremely sure we import the correct (older) version of SciATH,
# printing out enough to make this very clear if we make a mistake
import sys
import os
import re
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

def JobCompositeTest():
    t = Test('JobCompositeTest',1,'python ' + abs_path('./job/test_jobcomposite.py'),abs_path('job/test_jobcomposite.expected'))
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

def LauncherTest1():
    t = Test('LauncherTest1',1, [ 'cp '  + abs_path('./launcher/test_conf') + ' ' + 'SciATHBatchQueuingSystem.conf', 'python ' + abs_path('./launcher/test1.py') ], abs_path('launcher/test1.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

def LauncherTest2():
    t = Test('LauncherTest2',1,'python ' + abs_path('./launcher/test2.py'),abs_path('launcher/test2.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

def TestTest1():
    t = Test('TestTest1',1, [ 'cp -r ' + abs_path('./test/expected/') + ' expected','cp '  + abs_path('./test/test_conf') + ' ' + 'SciATHBatchQueuingSystem.conf', 'python ' + abs_path('./test/unittest_ex1.py') ], abs_path('test/unittest_ex1.expected'))
    t.setVerifyMethod(lambda t: t.compareUnixDiff())
    t.setUseSandbox()
    return t

# Missing: test/unittest_ex2.py testing

def main():
    print('SciATH Self-tests')
    print('Testing with version',getStableVersion(),'from',stablePackage.__file__)
    harness = Harness([
        JobTest(),
        JobSequenceTest(),
        JobDAGTest(),
        JobCompositeTest(),
        LauncherTest1(),
        LauncherTest2(),
        TestTest1(),
        ])
    harness.execute()
    harness.verify()

if __name__ == "__main__":
    main()
