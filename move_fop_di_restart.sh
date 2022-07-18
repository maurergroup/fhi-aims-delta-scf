#!/bin/bash

read -p 'Enter atom: ' atom

for dir in "$atom"*; do
  for file in "$dir/init_1/restart"*; do
    mv "$file" "$dir/init_2/"
  done
  for file in "$dir/init_2/restart"*; do
    mv "$file" "$dir/hole/"
  done
done
