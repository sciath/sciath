#!/usr/bin/env sh

original=$1
replacement=${2:-<<TEST DIR STRIPPED>>}

sed "s%$original%$replacement%g"
