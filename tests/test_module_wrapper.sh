#!/usr/bin/env sh

test_name=$1
sandbox="$test_name""_sandbox"
args=$2
test_conf="test_conf"
python=python

rm -rf $sandbox
mkdir $sandbox
cp $test_conf "$sandbox""/SciATHBatchQueuingSystem.conf"
cd $sandbox
$python -m sciath $args \
  | sed "s%from /.*/sandbox%from <<PATH STRIPPED>>%" \
  | sed "s%Expected file.*\.expected%Expected file <<PATH STRIPPED>>%"
