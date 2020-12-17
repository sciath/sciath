#!/usr/bin/env sh

# this doesn't have a timeout (seems risky, as you might have zombie processes)

rm -f stderr stdout

echo "this is stdout" 1>>stdout
echo "this is stderr" 2>&1 1>>stderr

printf "This is for a job named $SCIATH_JOB_NAME" 1>>stdout

SCIATH_TASK_COMMAND="grep foo bar"
SCIATH_TASK_RANKS=2

$CLEAN_MPICH -n $SCIATH_TASK_RANKS \
$SCIATH_TASK_COMMAND 1>>stdout 2>>stderr # &
