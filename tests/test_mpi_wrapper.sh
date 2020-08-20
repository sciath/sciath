#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox/"
prereq_test_name=${3:-}
prereq_sandbox="$prereq_test_name""_sandbox/"
args=$2
configuration_file=SciATHBatchQueuingSystem.conf
python=python

if [ ! -f "$configuration_file" ]; then
  printf 'Expected configuration file %s not found\n' "$configuration_file"
  exit 1
fi

if [ -z "$prereq_test_name" ]; then
  rm -rf $sandbox
  mkdir $sandbox
else
  cp -R $prereq_sandbox/. $sandbox
fi
cp $configuration_file $sandbox
cd $sandbox
$python -m sciath $args \
  | $test_dir/filter.sh $test_dir
