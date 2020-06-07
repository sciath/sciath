import sys
if sys.version_info[0] < 3: # Remove when Python 2 support is dropped
    from itertools import izip as zip

from sciath._io import dictView

class Job:
    """:class:`Job` describes a set of commands to be run with a given set of resources.

    It describes the commands themselves, not information about any
    particular "run" (handled within :class:`Harness`) or how one might
    interpret the results of such a run (handled by :class:`Test`).  A
    :class:`Launcher` object executes tasks described by a :class:`Job`.

    Data include

    * A command to be run: a string containing an executable and arguments. Relative paths (not recommended) will be interpreted relative to where the command is run.
    * A set of "resources" required. These are system-agnostic details like the number of (MPI) ranks or (OpenMP) threads.
    * A name, set to a default value if not provided
    * An amount of time required to run (optional)
    * A user-provided method to clean up after the command, relative to a provided path (optional)

    """

    # This information should be integrated into docstring or tutorial:
    #Args:
    #  cmd          (string): The command used to execute your application.
    #  **kwargs (name=value): A keyword argument list.
    #                         The Job constructor will recognize the following names:
    #                           name        (string): textual name you want to assign to the job.
    #                           exitCode       (int): the exit code which should be used to infer success.
    #Examples:
    #  job = Job('echo \\"hi\\"') -> a new job which will simply execute $echo 'hi'

    #  job = Job('echo \\"hi\\"',**kwargs,) -> a new job which will simply execute $echo "hi"
    #                                     and with variables initialized with the name=value pairs
    #  job = Job('echo \\"hi\\"', name='job-1', exitCode=0)


    _default_job_name = 'job'

    def __init__(self, cmd, name=None, **kwargs):
        self.cmd = cmd # command which will be executed via a system call to run this job
        if name is None:
            self.name = Job._default_job_name
            self.named_by_default = True
        else:
            self.name = name.replace(' ','_')
            self.named_by_default = False

        # Design note: we use a dict to enable developers to easily add support for different resource requests
        self.resources = dict()
        self.setResources(**kwargs) # looking in kwargs for any resources
        if len(self.resources) == 0: # set defaults
            self.resources.update({"mpiranks":1}) # mpi parallel resource data
            self.resources.update({"threads":1}) # thread parallel (e.g. OMP) resource data
            self.resources.update({"idlempirankspernode":0}) # idle ranks-per-compute-node resource data

        # optional info not needing a setter (e.g. they are not special enough)
        self.exit_code_success = 0
        self.wall_time         = 10.0/60.0 # 10 secs (in minutes)

        for key, value in kwargs.items():
            if key == 'exitCode':
                self.exit_code_success = int(value)
            if key == 'wall_time':
                try:
                    self.wall_time = float(value)
                except ValueError:
                    message = '[SciATH error]: Cannot convert wall_time \"' + str(value) + '\" to float.'
                    raise RuntimeError(message)


    def clean(self):
        """
        Responsible for deleting any data Job creates.
        User should over-ride this method with their own deletion rules.
        Care will have to be taken with paths as the Job may get executed from a
        different directory to where the executable lives.
        """
        pass

    def createJobOrdering(self):
        """
        Returns a list of job names in the order they will be executed.
        """
        return [self.name]

    def get_output_filenames(self):
        """ Returns name lists for error-code file (one per job), stdout, stderr """
        jobnames = self.createJobOrdering()

        errorCodeName = "sciath.job-" +  self.name + ".errorcode"
        stdoutName = []
        stderrName = []

        lc_count = len(jobnames)
        for jobname in jobnames:
            jprefix = "".join(["sciath.depjob-",str(lc_count),'-',jobname])
            if lc_count == 1: # we do something special for the last job in a sequence list
                jprefix = "sciath.job-" + self.name

            stdoutName.append( jprefix + ".stdout" )
            stderrName.append( jprefix + ".stderr" )

            lc_count -= 1

        return errorCodeName, stdoutName, stderrName

    def getMaxResources(self):
        """
        Returns a dict() defining the maximum required counts / values.
        for each valid resource associated with a job.
        This functionality is required for batch queue systems.
        """

        # Iterate through keys in self.resource, set initial values in max_resources
        # We are certain no new keys will be added as setResources() will
        # error if unrecognized resources were requested
        max_resources = dict()
        for key in self.resources:
            value = self.resources[key]
            max_resources.update({key:value})
        return max_resources

    def getResources(self):
        """
        Returns a dict() defining the compute resources required for this job.
        """

        return self.resources

    def getMaxWallTime(self):
        """
        Returns a floating point number which is the sum of all wall_time values.
        """
        return self.wall_time

    def createExecuteCommand(self):
        """
        Returns a list containing the command, resource tuple for a job.
        """

        ex = []
        ex.append( (self.cmd,self.resources) )
        return ex

    def setResources(self,**kwargs):
        """
        Define job resources (e.g. number of mpi ranks) via "resource_name"=number keyword=value pairs.
        The keywords used to identify the number mpi ranks is ['ranks', 'Ranks', 'mpiranks', 'MPIRanks'].
        The keywords used to identify the number of threads is ['threads', 'ompthreads'].
        Unrecognized resource types will produce an error.
        """

        # Valid names to identify number of MPI ranks
        ranks_k = [ 'ranks', 'Ranks', 'mpiranks', 'MPIRanks' ]
        ranks_set = 0

        # Valid names to identify number of threads
        threads_k = [ 'threads', 'ompthreads' ]
        threads_set = 0

        idlempirankspernode_k = [ 'idle-ranks-per-node', 'idle-mpiranks-per-node', 'idle-ranks_per_node', 'idle_mpiranks_per_node','idlerankspernode', 'idlempirankspernode' ]
        idlempirankspernode_set = 0

        # Others resources go here

        # Perform error checking on non-empty dictionary. This is done to enable this method
        # silently be called during job.__init__()
        # Join all valid name list and check that the provided keyword is a valid resource name / identifier
        if len(self.resources) != 0:
            allValidResourceNames = ranks_k + threads_k
            allValidResourceNames += idlempirankspernode_k
            for key,value in kwargs.items():
                if key not in allValidResourceNames:
                    message  = '[SciATH error]: Unknown resource type \"' + str(key) + '\" was requested.\n'
                    message += '                Choose from the following: ' + " ".join(allValidResourceNames)
                    raise RuntimeError(message)

        for key, value in kwargs.items():
            if key in ranks_k: # look mpi rank keyword identifiers
                self.resources.update({"mpiranks":int(value)})
                ranks_set += 1

            if key in threads_k: # look for thread keyword identifiers
                self.resources.update({"threads":int(value)})
                threads_set += 1

            if key in idlempirankspernode_k: # look for idlempirankspernode keyword identifiers
                self.resources.update({"idlempirankspernode":int(value)})
                idlempirankspernode_set += 1


        # Sanity check that only one instance of a valid keyword
        # for a given resource type (e.g. mpi ranks) was provided
        if ranks_set > 1:
            message  = '[SciATH error]: More than one instance of a valid MPI ranks keyword was provided to setResources().\n'
            message += '                To set the #mpi ranks, choose one of: ' + " ".join(ranks_k)
            raise RuntimeError(message)

        if threads_set > 1:
            message   = '[SciATH error]: More than one instance of a valid threads keyword was provided to setResources().\n'
            message += '                To set the #threads, choose one of: ' + " ".join(threads_k)
            raise RuntimeError(message)

        if idlempirankspernode_set > 1:
            message = '[SciATH error]: More than one instance of a valid idlempirankspernode keyword was provided to setResources().\n'
            message += '                To set the #idle-ranks-per-node, choose one of: ' + " ".join(idlempirankspernode_k)
            raise RuntimeError(message)


    def view(self):
        """
        Display the contents of an Job instance to stdout.
        The parent->child relationship will be reported.
        Uninitialized non-essential members will not be reported.
        This includes: self.child.
        """

        print('Job: Job name:',self.name)
        print('Command:',self.cmd)
        print('Exit code success:',self.exit_code_success)
        #print('MPI ranks:',self.resources["mpiranks"],', Threads:',self.resources["threads"])
        print('Resources:',dictView(self.resources))
        maxR = self.getMaxResources()
        print('Max. resources (incl. dependencies):', dictView(maxR))



class JobSequence(Job):
    """ A SciATH linear job sequence (inherits from :class:`Job`)
    """

    #A linear job sequence defines a parent job (job_0) and N depdendent jobs: job_1, job_2, ..., job_N.
    #A dependency graph is assumed from the order above; specifically we assume that
    #job_{i} depends on the result of job_{i+1}, hence job_{i+1} will be executed before job_{i}.
    #An arbitrary number of dependent jobs (N) may be defined.

    #Args:
    #  cmd          (string): The command used to execute your application.
    #  **kwargs (name=value): A keyword argument list.
    #                         The Job constructor will recognize the following names:
    #                           name        (string): textual name you want to assign to the job.
    #                           exitCode       (int): the exit code which should be used to infer success.

    def __init__(self,cmd,name='job_sequence',**kwargs):
        Job.__init__(self,cmd,name,**kwargs)
        self.sequence = []


    def append(self,job):
        """
        Append a job into the sequence. The parent job is always first in the list.
        Dependent jobs appear after the parent.
        """
        self.sequence.append(job)


    # overload
    def createExecuteCommand(self):
        """
        Returns a list of command, resource tuples for a job sequence.
        The reverse order of the parent->child relationship is captured in the tuple returned.
        The commands should thus be executed in order from first to last.
        """

        execute = []
        resources = []

        # collect the user defined job list and reverse it (leave self.sequence untouched)
        sr = []
        for j in self.sequence:
            sr.append(j)
        sr.reverse()

        # for each instance of an inherited job, collect commands,resources pairs
        for j in sr:
            er = j.createExecuteCommand()
            for k in er:
                execute.append(k[0])
                resources.append(k[1])

        execute.append(self.cmd)
        resources.append(self.resources)

        return [x for x in zip(execute,resources)]

    # overload
    def getMaxResources(self):
        """
        Returns the max. resources required for a job sequence.
        The max is taken over all jobs registered via JobSequence.append() and the parent job.
        """

        max_resources = dict()
        for key in self.resources:
            value = self.resources[key]
            max_resources.update({key:value})

        for j in self.sequence:
            max_resources_j = j.getMaxResources()
            # iterate through keys in max_resources_j, update values in max_resources
            for key in max_resources_j:
                value = max_resources_j[key]
                if value > max_resources[key]:
                    max_resources.update({key:value})

        return max_resources

    # overload
    def getMaxWallTime(self):
        """
        Returns a floating point number which is the sum of all wall_time values associated with JobSequence
        """
        sum_wt = self.wall_time
        for j in self.sequence:
            sum_wt += j.getMaxWallTime()

        return sum_wt


    # overload
    def view(self):
        """
        Display the contents of an job sequence to stdout.
        The parent will be reported first followed by its dependencies.
        Uninitialized non-essential members will not be reported.
        This includes: self.child.
        """

        Job.view(self)
        # view dependencies
        print('JobSequence:')
        print('Dependencies: found',len(self.sequence))
        cnt = 0
        for j in self.sequence:
            print('[Child job index',cnt,']')
            j.view()
            cnt += 1
        print('[Execution order]')
        cr = self.createExecuteCommand()
        cnt = 0
        for i in cr:
            print('  order',cnt,':',i[0])
            cnt += 1


    def createJobOrdering(self):
        """
        Returns a list of job names in the order they will be executed.
        """
        # collect the user defined job list and reverse it (leave self.sequence untouched)
        jname = []
        jname.append(self.name)
        for j in self.sequence:
            jname.append(j.name)
        jname.reverse()
        return jname

    def getJobList(self):
        jobs = []
        jobs.append(self)
        for j in self.sequence:
            jobs.append(j)
        jobs.reverse()
        return jobs
