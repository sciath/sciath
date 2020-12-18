printf "Max ranks $SCIATH_JOB_MAX_RANKS\n"

echo "this is stdout" 1>>$SCIATH_JOB_STDOUT
echo "this is stderr" 2>&1 1>>$SCIATH_JOB_STDERR

printf "This is for a job named $SCIATH_JOB_NAME\n" 1>>$SCIATH_JOB_STDOUT 2>>$SCIATH_JOB_STDERR

$CLEAN_MPICH -n $SCIATH_TASK_RANKS \
$SCIATH_TASK_COMMAND 1>>$SCIATH_JOB_STDOUT 2>>$SCIATH_JOB_STDERR && printf "$?\n" >> $SCIATH_JOB_EXITCODE

echo "Done"
