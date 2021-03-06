#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
script="$test_dir""/""$2"
python=python

rm -rf $sandbox
mkdir $sandbox
cd $sandbox
$python -m sciath --configure-default
$python $script \
  | $test_dir/filter.sh $test_dir
