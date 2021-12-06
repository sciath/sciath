""" SciATH Job class """
from __future__ import print_function

import sciath.task


class Job:
    r""":class:`Job` describes a ordered list of :class:`Task`\s.

    It describes the :class:`Task`\s themselves, not information about any
    particular "run" (handled within :class:`Harness`) or how one might
    interpret the results of such a run (handled by :class:`Test`).  A
    :class:`Launcher` object executes the :class:`Task`\s described by a :class:`Job`.

    Data include

    * A name
    * An ordered list of :class:`Task`\s
    * A minimum wall time required (can be None)

    It also defines how the name may be converted to various standard filenames.

    If a minimum wall time is specified, the wall time allocated is the maximum
    of this value and the sum of values of wall times for all included :class:`Task`\s that
    defined them. If no minimum wall time is specified, the :class:`Job`'s wall time
    is only defined if all included :class:`Task`\s specify a wall time, in which case the
    sum is used.

    """

    _default_job_name = 'job'

    def __init__(self, task_or_tasks, name=None, minimum_wall_time=None):
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

        self.wall_time = self._compute_wall_time(minimum_wall_time)

    def create_execute_command(self):
        """
        Returns a list containing (command, resource) tuples for the Job.
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

    # This can be removed once the transition to using templates is complete
    def get_max_resources(self):
        """ Returns a dict() defining the maximum required counts / values """

        # Use the first Task to determine which resources to consider
        max_resources = {}
        for key, value in self.tasks[0].resources.items():
            max_resources[key] = value

        for task in self.tasks[1:]:
            for key, value in task.resources.items():
                if value > max_resources[key]:
                    max_resources[key] = value
        return max_resources

    def resource_max(self, key):
        """ Returns the maximum value of a resource over all Tasks

            Returns None if no Tasks define that resource.
        """
        maximum = None
        for task in self.tasks:
            if key in task.resources:
                current = task.resources[key]
                if maximum is None:
                    maximum = current
                else:
                    maximum = max(maximum, current)
        return maximum

    def number_tasks(self):
        """ Returns the number of tasks within the Job """
        return len(self.tasks)

    def _compute_wall_time(self, minimum_wall_time):
        task_wall_time_total, task_wall_time_defined = self._tasks_wall_time()
        if minimum_wall_time is None:
            return task_wall_time_total
        if task_wall_time_total is None:
            return minimum_wall_time
        return max(minimum_wall_time, task_wall_time_defined)

    def _tasks_wall_time(self):
        """ Returns (total walltime, total defined wall time) for a job's Tasks.

            Returns None in the first slot if any Task doesn't have a defined
            wall time. The second slot holds the sum of the defined task
            wall times, or 0 if none are defined.
        """
        defined = 0
        total = 0
        for task in self.tasks:
            if task.wall_time is None:
                total = None
            else:
                defined += task.wall_time
                if total is not None:
                    total += task.wall_time
        return total, defined
