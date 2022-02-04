""" Generate default templates for Launcher batch systems """

import os

CONTENTS_LOCAL = r"""#!/usr/bin/env sh

$SCIATH_TASK_MPI_RUN \
$SCIATH_TASK_COMMAND 1>>$SCIATH_JOB_STDOUT 2>>$SCIATH_JOB_STDERR; printf "$?\n" >> $SCIATH_JOB_EXITCODE

touch $SCIATH_JOB_COMPLETE
"""

CONTENTS_LSF = r"""#!/bin/sh

#BSUB -J $SCIATH_JOB_NAME
#BSUB -o $SCIATH_JOB_STDOUT
#BSUB -e $SCIATH_JOB_STDERR
#BSUB -n $SCIATH_JOB_MAX_RANKS_OR_REMOVE_LINE
#BSUB -W $SCIATH_JOB_WALLTIME_HM_OR_REMOVE_LINE
#BSUB -q $SCIATH_QUEUE_OR_REMOVE_LINE

$SCIATH_TASK_MPI_RUN \
$SCIATH_TASK_COMMAND; printf "$?\n" >> $SCIATH_JOB_EXITCODE

touch $SCIATH_JOB_COMPLETE
"""

CONTENTS_SLURM = r"""#!/bin/bash -l

#SBATCH --job-name=$SCIATH_JOB_NAME
#SBATCH --output=$SCIATH_JOB_STDOUT
#SBATCH --error=$SCIATH_JOB_STDERR
#SBATCH --ntasks=$SCIATH_JOB_MAX_RANKS_OR_REMOVE_LINE
#SBATCH --time=$SCIATH_JOB_WALLTIME_HMS_OR_REMOVE_LINE
#SBATCH --account=$SCIATH_ACCOUNT_OR_REMOVE_LINE
#SBATCH --partition=$SCIATH_QUEUE_OR_REMOVE_LINE

$SCIATH_TASK_MPI_RUN \
$SCIATH_TASK_COMMAND; printf "$?\n" >> $SCIATH_JOB_EXITCODE

touch $SCIATH_JOB_COMPLETE
"""


def _generate_default_template(system_type, output_path=".", filename=None):
    if system_type == "local":
        contents = CONTENTS_LOCAL
        if filename is None:
            filename = "SciATH_template_local.sh"
    elif system_type == "lsf":
        contents = CONTENTS_LSF
        if filename is None:
            filename = "SciATH_template_lsf.lsf"
    elif system_type == "slurm":
        contents = CONTENTS_SLURM
        if filename is None:
            filename = "SciATH_template_slurm.sbatch"
    else:
        raise Exception("Unrecognized batch system type %s" % system_type)

    with open(os.path.join(output_path, filename), "w") as file:
        file.write(contents)
    return filename
