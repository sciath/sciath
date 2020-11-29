#!/usr/bin/env sh

test_name=$1
test_dir=$(pwd)
sandbox="$test_name""_sandbox"
reference_location="/Users/patrick/scratch/"
docs_tutorial_dir="../../docs/_static/tutorial/"
args=$2
python=python

rm -rf $sandbox
mkdir $sandbox
cd $sandbox
$python -m sciath --configure-default
$python -m sciath $args \
  | $test_dir/filter.sh "$test_dir/$sandbox/" "$reference_location" \
  | sed "s%$docs_tutorial_dir%%g"

 
