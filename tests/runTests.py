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

def Example1Test():
    t = Test('Example1Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example1','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example1','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example1Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))
        test.compareLiteral(re.escape(' [ex2]'))
        test.compareLiteral(re.escape(' [ex3]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example1Test_2():
    # Note: this test is a bit dangerous, as it modifies files in the examples directory
    t = Test('Example1Test_2',1,
            [
            'rm -f '   + abs_path(os.path.join('..','examples','example1','ex1.expected.bak')),
            'python '  + abs_path(os.path.join('..','examples','example1','example.py')) + ' -d',
            'python '  + abs_path(os.path.join('..','examples','example1','example.py')) + ' --no-colors -t ex1',
            'cp '      + abs_path(os.path.join('example_tests_resources','Example1Test_2_ex1.expected.wrong ')) + abs_path(os.path.join('..','examples','example1','ex1.expected')),
            'python '  + abs_path(os.path.join('..','examples','example1','example.py')) + ' --no-colors -t ex1',
            'python '  + abs_path(os.path.join('..','examples','example1','example.py')) + ' --no-colors -t ex1 -r',
            'python '  + abs_path(os.path.join('..','examples','example1','example.py')) + ' --no-colors -t ex1',
            'rm '      + abs_path(os.path.join('..','examples','example1','ex1.expected.bak')),
            ],
            abs_path('example_tests_expected/Example1Test_2.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape('[ex1]   *'))
        test.compareLiteral(re.escape('[ex1]   p'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example2Test():
    t = Test('Example2Test',1,
            [
            'mkdir -p t1 t2',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example2Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [test1]'))
        test.compareLiteral(re.escape(' [test2]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example2Test_2():
    t = Test('Example2Test_2',1,
            [
            'mkdir -p t1 t2',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' --no-colors -t test1'
            ],
            abs_path('example_tests_expected/Example2Test_2.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [test1]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example2Test_3():
    t = Test('Example2Test_3',1,
            [
            'mkdir -p t1 t2',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example2','example.py')) + ' --no-colors -t test1,test2'
            ],
            abs_path('example_tests_expected/Example2Test_3.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [test1]'))
        test.compareLiteral(re.escape(' [test2]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example4Test():
    t = Test('Example4Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example4','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example4','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example4Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))
        test.compareLiteral(re.escape(' [ex2]'))
        test.compareLiteral(re.escape(' [ex3]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example5Test():
    t = Test('Example5Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example5','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example5','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example5Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))
        test.compareLiteral(re.escape(' [ex2]'))
        test.compareLiteral(re.escape(' [ex3]'))
        test.compareLiteral(re.escape(' [ex4]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example5Test_2():
    t = Test('Example5Test_2',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example5','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example5','example.py')) + ' --no-colors -s'
            ],
            abs_path('example_tests_expected/Example5Test_2.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))
        test.compareLiteral(re.escape(' [ex2]'))
        test.compareLiteral(re.escape(' [ex3]'))
        test.compareLiteral(re.escape(' [ex4]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example6Test():
    t = Test('Example6Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example6','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example6','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example6Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))
        test.compareLiteral(re.escape(' [ex2]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example7Test():
    t = Test('Example7Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example7','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example7','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example7Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [ex1]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example8Test():
    t = Test('Example8Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example8','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example8','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example8Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [test1]'))
        test.compareLiteral(re.escape(' [test1_clone]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example8Test_2():
    t = Test('Example8Test_2',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example8','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example8','example.py')) + ' --no-colors -t test1_clone'
            ],
            abs_path('example_tests_expected/Example8Test_2.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape(' [test1]'))
        test.compareLiteral(re.escape(' [test1_clone]'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def Example9Test():
    t = Test('Example9Test',1,
            [
            'python ' + abs_path(os.path.join('..','examples','example9','example.py')) + ' -d',
            'python ' + abs_path(os.path.join('..','examples','example9','example.py')) + ' --no-colors'
            ],
            abs_path('example_tests_expected/Example9Test.expected'))

    def comparefunc(test):
        test.compareLiteral(re.escape('[testAbs]   *'))
        test.compareLiteral(re.escape('[testRel]   *'))
        test.compareLiteral(re.escape('[testRelEpsilon]   p'))

    t.setVerifyMethod(comparefunc)
    t.setUseSandbox()
    return t

def main():
    print('SciATH Self-tests')
    print('Testing with version',getStableVersion(),'from',stablePackage.__file__)
    harness = Harness([
        JobTest(),
        JobSequenceTest(),
        JobDAGTest(),
        Example1Test(),
        Example1Test_2(),
        Example2Test(),
        Example2Test_2(),
        Example2Test_3(),
        Example4Test(),
        Example5Test(),
        Example5Test_2(),
        Example6Test(),
        Example7Test(),
        Example8Test(),
        Example8Test_2(),
        Example9Test(),
        ])
    harness.execute()
    harness.verify()

if __name__ == "__main__":
    main()
