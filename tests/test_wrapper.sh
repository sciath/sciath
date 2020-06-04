#!/usr/bin/env sh

test_name=$1
sandbox="$test_name""_sandbox"
script="$PWD""/""$2"
test_conf="test_conf"
python=python

rm -rf $sandbox
mkdir $sandbox
cp $test_conf "$sandbox""/SciATHBatchQueuingSystem.conf"
cd $sandbox
$python $script \
  | sed "s%from /.*_sandbox%from <<PATH STRIPPED>>%" \
  | sed "s%Expected file.*\.expected%Expected file <<PATH STRIPPED>>%" \
