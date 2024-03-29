#!/usr/bin/env python
from __future__ import print_function

import sciath.job
import sciath.task

resources_to_print = ['mpiranks', 'threads']

taskA = sciath.task.Task('echo \"task 1\"')
taskA.set_resources(ranks=4, threads=11)

taskB = sciath.task.Task('echo \"task 2\"')
taskB.set_resources(ranks=140)

taskC = sciath.task.Task('echo \"task 3\"')

taskD = sciath.task.Task('echo \"task 4\"')
taskD.set_resources(threads=27, ranks=40)

job = sciath.job.Job([taskA, taskB, taskC, taskD], name='Four-task job')

er = job.create_execute_command()
print('Execute command + resources for job')
for i in er:
    print('  cmd =', i[0])
    for r in resources_to_print:
        print(' ', r, ':', i[1][r])

print('Max. resources required for job')
for r in resources_to_print:
    print(r, ':', job.resource_max(r))
