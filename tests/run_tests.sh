#!/usr/bin/env sh
# Additional arguments (e.g. --update) are passed through

minisciath=minisciath/minisciath.py

if [ ! -f "$minisciath" ]; then
  printf "MiniSciATH is required. Update submodules, e.g.\n" 
  printf "  cd .. && git submodule init && git submodule update && cd -\n"
  exit 1
fi

if [ ! -f "SciATHBatchQueuingSystem.conf" ]; then
  python -m sciath  # prompt to generate configuration file
fi

./minisciath/minisciath.py --exclude-group mpi_verify tests.yml $@

printf "You should run additional tests to verify MPI tests. Wait until any queued jobs are completed, and then run\n"
printf "  ./minisciath/minisciath.py --only-group mpi_verify tests.yml\n"
