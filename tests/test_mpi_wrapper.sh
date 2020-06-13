#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
args=$2
configuration_file=SciATHBatchQueuingSystem.conf
python=python

if [ ! -f "$configuration_file" ]; then
  printf 'Expected configuration file %s not found\n' "$configuration_file"
  exit 1
fi

rm -rf $sandbox
mkdir $sandbox
cp $configuration_file $sandbox
cd $sandbox
$python -m sciath $args \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"
