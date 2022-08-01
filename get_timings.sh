#!/bin/bash

if [[ $1 == '' ]]; then
  echo "Directories argument not specified"
  echo
  echo "Script Usage:"
  echo "1st argument: Directories to search for timings"
  exit 1
fi

input_dirs=($1)

for i in $input_dirs; do (
  cd "$i"

  for j in *; do (
    if [ -d "$j" ]; then
      # If a directory, this is an excited state calculation
      atom="$i"
      run_type="$j"
      cd "$j"

      time=$(tail -n 100 aims.out | grep -q '| Total time   ' | awk '{ printf("$d", $5) }')
      echo "$atom $run_type: $time seconds"
    else
      # This must be a ground state calculation
      time=$(tail -n 100 aims.out | grep -q '| Total time   ' | awk '{ printf("$d", $5) }')
      echo "ground: $time seconds"
    fi
  ) done
) done
