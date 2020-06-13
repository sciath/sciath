#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
args=$2
python=python

rm -rf $sandbox
mkdir $sandbox
cd $sandbox
$python -m sciath --configure-default
$python -m sciath $args \
  | sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"
