#!/usr/bin/env sh

export DEFINED_VAR="defined var"
export DEFINED_VAR_LONGER="defined var longer"
export EMPTY_VAR=

sh test_wrapper.sh "$@"
