""" SciATH Task class """


class Task:
    """ A class which encapsulates a command and a set of required resources

       A "command", here, is a list of strings, the first of which names an executable
       and the rest of which provide arguments. For example ``['printf','Hello, World!']``
       corresponds to a local command like ``printf 'Hello, World!'``. This
       corresponds to the recommended way to pass commands to Python's
       :any:`python:subprocess.run` (click link for information).

       Note that relative paths (not recommended) in the command will be interpreted
       relative to wherever it is actually executed from, which is determined
       when a :class:`Launcher` is requested to execute a :class:`Job`.

       A "resource" here is a specification of a computational resource required,
       for example the number of (MPI) ranks or (OpenMP) threads, or an amount of
       time to allocate.
    """

    def __init__(self, command, **kwargs):
        self.command = command
        self.resources = {}
        for key, value in kwargs.items():
            self.resources[key] = value

        self.set_resources(**kwargs)  # looking in kwargs for any resources
        if 'mpiranks' not in self.resources:
            self.resources['mpiranks'] = 1
        if 'threads' not in self.resources:
            self.resources['threads'] = 1

        self.wall_time = None  # minutes

        for key, value in kwargs.items():
            if key == 'exitCode':
                self.exit_code_success = int(value)
            if key == 'wall_time':
                try:
                    self.wall_time = float(value)
                except ValueError:
                    #pylint: disable=bad-option-value,raise-missing-from
                    message = '[SciATH error]: Cannot convert wall_time \"' + str(
                        value) + '\" to float.'
                    raise RuntimeError(message)

    def create_execute_command(self):
        """
        Returns a  command, resource tuple.
        """
        return self.command, self.resources

    def get_resource(self, key):
        """ Returns the value for a given resource, specified by a string

            Returns None if resource not defined.
        """
        if key in self.resources:
            return self.resources[key]
        return None

    def set_resources(self, **kwargs):
        """
        Define task resources (e.g. number of mpi ranks)

        via "resource_name"=number keyword=value pairs.
        The keywords used to identify the number mpi ranks iare
        ['ranks', 'Ranks', 'mpiranks', 'MPIRanks'].

        The keywords used to identify the number of threads are
        ['threads', 'ompthreads'].

        Unrecognized resource types will produce an error.
        """

        # Valid names to identify number of MPI ranks
        ranks_k = ['ranks', 'Ranks', 'mpiranks', 'MPIRanks']
        ranks_set = 0

        # Valid names to identify number of threads
        threads_k = ['threads', 'ompthreads']
        threads_set = 0

        # Others resources go here

        # Perform error checking on non-empty dictionary. This is done to enable
        # this method silently be called during job.__init__()
        # Join all valid name list and check that the provided keyword is a
        # valid resource name / identifier
        if len(self.resources) != 0:
            all_valid_resource_names = ranks_k + threads_k
            for key, value in kwargs.items():
                if key not in all_valid_resource_names:
                    message = '[SciATH error]: Unknown resource type \"' + str(
                        key) + '\" was requested.\n'
                    message += '                Choose from the following: ' + " ".join(
                        all_valid_resource_names)
                    raise RuntimeError(message)

        for key, value in kwargs.items():
            if key in ranks_k:  # look mpi rank keyword identifiers
                self.resources.update({"mpiranks": int(value)})
                ranks_set += 1

            if key in threads_k:  # look for thread keyword identifiers
                self.resources.update({"threads": int(value)})
                threads_set += 1

        # Sanity check that only one instance of a valid keyword
        # for a given resource type (e.g. mpi ranks) was provided
        if ranks_set > 1:
            message = ('[SciATH error]: More than one instance of a valid MPI '
                       'ranks keyword was provided to set_resources().\n')
            message += '                To set the #mpi ranks, choose one of: ' + " ".join(
                ranks_k)
            raise RuntimeError(message)

        if threads_set > 1:
            message = (
                '[SciATH error]: More than one instance of a valid threads'
                'keyword was provided to set_resources().\n')
            message += '                To set the #threads, choose one of: ' + " ".join(
                threads_k)
            raise RuntimeError(message)
