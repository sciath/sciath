# SciATH Self-tests

Important: these are tests for SciATH to test itself, NOT intended as examples for users! 
See the SciATH documentation for information on using SciATH.

We use a previous stable version of SciATH itself to test, via a git submodule.

If that makes you nervous, maybe you will be partially reassured to know that
when possible, these tests use pytest's exit codes or plain diffs, not SciATH's 
own logic for determining successful execution based on an output file.

To run the tests:

    git submodule init && git submodule update
    ./runTests.py
    ./runTests.py -v  # if on batch system, after waiting
    ./runTests.py -p  # clean up
