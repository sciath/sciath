from __future__ import print_function

import sys

import sciath.task


class Job:
    """:class:`Job` describes a set of commands to be run with a given set of resources.

    It describes the commands themselves, not information about any
    particular "run" (handled within :class:`Harness`) or how one might
    interpret the results of such a run (handled by :class:`Test`).  A
    :class:`Launcher` object executes tasks described by a :class:`Job`.

    Data include

    * An ordered list of :class:`Task` objects describing one or more commands to be run, and required resources for each.
    * A name

    """

    _default_job_name = 'job'

    def __init__(self, task_or_tasks, name=None):
        if name is None:
            self.name = Job._default_job_name
            self.named_by_default = True
        else:
            self.name = name.replace(' ','_')
            self.named_by_default = False

        if isinstance(task_or_tasks, sciath.task.Task):
            self.tasks = [task_or_tasks]
        elif isinstance(task_or_tasks, list):
            for task in task_or_tasks:
                if not isinstance(task, sciath.task.Task):
                    raise Exception('A Task, or list of Task objects was expected')
                self.tasks = task_or_tasks
        else:
            raise Exception('A Task or list of Tasks was expected')

    def createExecuteCommand(self):
        """
        Returns a list containing the command, resource tuple for a job.
        """
        return [task.createExecuteCommand() for task in self.tasks]

    def exit_codes_success(self):
        return [task.exit_code_success for task in self.tasks]

    def get_output_filenames(self):
        """ Returns name lists for error-code file (one per job), stdout, stderr """
        errorCodeName = "sciath.job-" +  self.name + ".errorcode"
        stdoutName = []
        stderrName = []

        for count in range(len(self.tasks)):
            jprefix = "sciath.job-%d-%s" % (count, self.name)
            stdoutName.append( jprefix + ".stdout" )
            stderrName.append( jprefix + ".stderr" )

        return errorCodeName, stdoutName, stderrName

    def getMaxResources(self):
        """
        Returns a dict() defining the maximum required counts / values
        """

        # Use the first Task to determine which resources to consider
        max_resources = dict()
        for key, value in self.tasks[0].resources.items():
            max_resources[key] = value

        for task in self.tasks[1:]:
            for key, value in task.resources.items():
                if value > max_resources[key]:
                    max_resources[key] = value
        return max_resources

    def total_wall_time(self):
        """
        Returns the total wall time required for all Tasks
        """
        total_wall_time = 0
        for task in self.tasks:
            total_wall_time += task.wall_time
        return total_wall_time
