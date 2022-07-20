#!/bin/bash

read -p 'Enter atom: ' atom

for dir in "$atom"*; do
  if [[ "$1" == 1 ]]; then
    for file in "$dir/init_1/restart"*; do
      mv "$file" "$dir/init_2/"
    done

  elif [[ "$1" == 2 ]]; then
    for file in "$dir/init_2/restart"*; do
      mv "$file" "$dir/hole/"
    done
  fi
done
