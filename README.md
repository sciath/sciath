# PythonTestHarness: The idea #

Testing code should be easy. The functionality required to launch, parse and perform the verification should be light-weight and simple to migrate into existing projects.

### Key concepts ###

We provide

* An object to define a single unit test
* A set of tools to parse / filter and query text files for verification purposes
* An object to manage executing a unit test within a batch queuing system

### How do I use this crap? ###

* For an example defining a test and performing the verification, execute 
  ```
  #!bash
  python3.4 zpth2.py
  ```
* For an example of the batch queuing system support, execute  
  ```
  #!bash
  python3.4 zpth_conf.py
  ```