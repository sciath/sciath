#!/usr/bin/env sh

test_name=verifier_update
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
test_conf="test_conf"
python=python

args1="-i input.yml"
args2="-i input.yml -u"

rm -rf $sandbox
mkdir $sandbox
cp $test_conf "$sandbox""/SciATHBatchQueuingSystem.conf"
cd $sandbox

# Generate expected file
echo bar > expected
cp ../test_data/verifier_update/input.yml .
printf '  expected: expected\n' >> input.yml

$python -m sciath $args1 \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"

$python -m sciath $args2 \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"

$python -m sciath $args1 \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"
