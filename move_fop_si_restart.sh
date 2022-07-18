#!/bin/bash

read -p 'Enter atom: ' atom

for dir in "$atom"*; do
  for file in "$dir/init/restart"*; do
    mv "$file" "$dir/hole/"
  done
done
