""" SciATH Job class """
from __future__ import print_function

import sciath.task


class Job:
    """:class:`Job` describes a set of :class:`Task`s.

    It describes the Tasks themselves, not information about any
    particular "run" (handled within :class:`Harness`) or how one might
    interpret the results of such a run (handled by :class:`Test`).  A
    :class:`Launcher` object executes the :class:`Task`s described by a :class:`Job`.

    Data include

    * A name
    * An ordered list of :class:`Task`s

    It also defines how the name may be converted to various standard filenames.

    """

    _default_job_name = 'job'

    def __init__(self, task_or_tasks, name=None):
        if name is None:
            self.name = Job._default_job_name
            self.named_by_default = True
        else:
            self.name = name.replace(' ', '_')
            self.named_by_default = False

        if isinstance(task_or_tasks, sciath.task.Task):
            self.tasks = [task_or_tasks]
        elif isinstance(task_or_tasks, list):
            for task in task_or_tasks:
                if not isinstance(task, sciath.task.Task):
                    raise Exception('A Task or list of Tasks was expected')
                self.tasks = task_or_tasks
        else:
            raise Exception('A Task or list of Tasks was expected')

    def create_execute_command(self):
        """
        Returns a list containing the command, resource tuple for a job.
        """
        return [task.create_execute_command() for task in self.tasks]

    @property
    def complete_filename(self):
        """ Returns a filename for a sentinel signifying completion """
        return '.%s.complete' % self.name

    @property
    def exitcode_filename(self):
        """ Returns a filename to use for exit codes """
        return self.name + '.exitcode'

    @property
    def launched_filename(self):
        """ Returns a filename for a sentinel signifying launching """
        return '.%s.launched' % self.name

    @property
    def stdout_filename(self):
        """ Returns a filename to use for stdout """
        return self.name + '.stdout'

    @property
    def stderr_filename(self):
        """ Returns a filename to use for stderr """
        return self.name + '.stderr'

    def get_max_resources(self):
        """ Returns a dict() defining the maximum required counts / values """

        # Use the first Task to determine which resources to consider
        max_resources = dict()
        for key, value in self.tasks[0].resources.items():
            max_resources[key] = value

        for task in self.tasks[1:]:
            for key, value in task.resources.items():
                if value > max_resources[key]:
                    max_resources[key] = value
        return max_resources

    def number_tasks(self):
        """ Returns the number of tasks within the Job """
        return len(self.tasks)

    def total_wall_time(self):
        """ Returns the total wall time required for all Tasks """
        total_wall_time = 0
        for task in self.tasks:
            total_wall_time += task.wall_time
        return total_wall_time
