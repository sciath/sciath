#!/usr/bin/env sh

test_dir=$1

sed "s%$test_dir%<<TEST DIR STRIPPED>>%g"
