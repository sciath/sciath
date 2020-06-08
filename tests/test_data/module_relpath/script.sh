#!/usr/bin/env sh

data_file=${1:-/dev/null}
printf "Script running.\n"
printf "data file contents: "
cat $data_file
touch script_residue.junk
