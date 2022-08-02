#!/bin/bash

if [[ $1 == '' ]]; then
  echo "Directories argument not specified"
  echo
  echo "Script Usage:"
  echo "1st argument: Directories to search for timings"
  exit 1
fi

for i in "$@"; do
  input_dirs+=("$i")
done

echo "Specified directories: ${input_dirs[@]}"
echo

for i in "${input_dirs[@]}"; do (
  cd "$i"
  for j in *; do (
    if [ -d "$j" ]; then
      # If a directory, this is an excited state calculation
      atom="$i"
      run_type="$j"
      cd "$j"
      # Find time taken in aims.out
      time=$(tail -n 100 aims.out | grep '| Total time   ' | awk '{ print $5 }')
      time_round=$(printf "%.0f\n" "$time")
      time_h=$(echo "$time_round" / 60 | bc -l)
      time_hr=$(printf "%.2f\n" "$time_h")
      echo "$atom $run_type: $time_round seconds"
      echo "$atom $run_type: $time_hr seconds"
      echo

    elif [[ "$j" == "aims.out" ]]; then
      # This must be a ground state calculation
      # Find time taken in aims.out
      time=$(tail -n 100 "$j" | grep '| Total time   ' | awk '{ print $5 }')
      time_round=$(printf "%.0f\n" "$time")
      time_h=$(echo "$time_round" / 60 | bc -l)
      time_hr=$(printf "%.2f\n" "$time_h")
      echo "ground: $time_round seconds"
      echo "ground: $time_hr minutes"
      echo

    fi
  ) done
) done
