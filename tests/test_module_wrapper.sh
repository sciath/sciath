#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
args=$2
test_conf="test_conf"
python=python

rm -rf $sandbox
mkdir $sandbox
cp $test_conf "$sandbox""/SciATHBatchQueuingSystem.conf"
cd $sandbox
$python -m sciath $args \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"
