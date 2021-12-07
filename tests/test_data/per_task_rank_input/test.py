#!/usr/bin/env python

from __future__ import print_function

import os

import sciath.test_file

TEST_YML_CONTENTS = r"""
tests:
  - name: test1
    command: echo foo
    type: exit_code

  - name: test1a
    commands: echo foo
    type: exit_code

  - name: test1b
    task: echo foo
    type: exit_code

  - name: test1c
    tasks: echo foo
    type: exit_code

  - name: test2
    ranks: 2
    commands: echo foo
    type: exit_code

  - name: test3
    ranks: 2
    commands:
      - command: echo foo
    type: exit_code

  - name: test4
    commands:
      - command: echo foo
        ranks: 2
    type: exit_code

  - name: test4b
    tasks:
      - command: echo foo
        ranks: 3
    type: exit_code

  - name: test4c
    task:
      - command: echo foo
        ranks: 3
    type: exit_code

  - name: test5
    ranks: 2
    tasks:
      - command: echo foo
        ranks: 3
      - command: echo foo
    type: exit_code

  - name: test6
    ranks: 2
    tasks:
      - command: echo foo
        ranks: 3
      - command: echo foo
        ranks: 0
    type: exit_code

  - name: test6b
    ranks: 2
    tasks:
      - command: echo foo
      - command: echo foo
    type: exit_code

  - name: test7
    tasks:
      - command: echo foo
      - command: echo foo
    type: exit_code

  - name: test8
    tasks:
      - echo foo
      - command: echo foo
    type: exit_code

  - name: test9
    tasks:
      - echo foo
      - echo foo
    type: exit_code

"""


def run():

    if os.path.exists("test.yml"):
        raise Exception("Refusing to overwrite test.yml")

    with open("test.yml", "w") as file:
        file.write(TEST_YML_CONTENTS)

    tests = sciath.test_file.create_tests_from_file("test.yml")

    for test in tests:
        print(test.job.name)
        for task in test.job.tasks:
            print(task.get_resource("mpiranks"))
        print()


if __name__ == "__main__":
    run()
