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
  atom_counter+=1
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
      echo "$atom $run_type: $time_hr minutes"
      echo

      # Add time to array depending on run type
      if [[ "$run_type" == "hole" ]]; then
        hole_times_sec+=("$time_round")
        hole_times_min+=("$time_hr")
      elif [[ "$run_type" == "init_1" ]]; then
        init1_times_sec+=("$time_round")
        init1_times_min+=("$time_hr")
      elif [[ "$run_type" == "init_2" ]]; then
        init2_times_sec+=("$time_round")
        init2_times_min+=("$time_hr")
      fi

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
  )
  done
)
done

# Sum counters
hole_sec_tot=0
hole_min_tot=0
init1_sec_tot=0
init1_min_tot=0
init2_sec_tot=0
init2_min_tot=0

# Calculate the sum of each array
for i in "${hole_times_sec[@]}"; do
  hole_sec_tot+=$i
done
for i in "${hole_times_min[@]}"; do
  hole_min_tot+=$i
done
for i in "${init1_times_sec[@]}"; do
  init1_sec_tot+=$i
done
for i in "${init1_times_min[@]}"; do
  init1_min_tot+=$i
done
for i in "${init2_times_sec[@]}"; do
  init2_sec_tot+=$i
done
for i in "${init2_times_min[@]}"; do
  init2_min_tot+=$i
done

# Calculate average times and round
avg_hole_time_sec=$(echo "hole_sec_tot" / "${#hole_times_sec[@]}" | bc -l)
round_hole_time_sec=$(printf "%.0f\n" "$avg_hole_time_sec")
avg_hole_time_min=$(echo "hole_min_tot" / "${#hole_times_min[@]}" | bc -l)
round_hole_time_min=$(printf "%.0f\n" "$avg_hole_time_min")
avg_init1_time_sec=$(echo "init1_sec_tot" / "${#init1_times_sec[@]}" | bc -l)
round_init1_time_sec=$(printf "%.0f\n" "$avg_init1_time_sec")
avg_init1_time_min=$(echo "init1_min_tot" / "${#init1_times_min[@]}" | bc -l)
round_init1_time_min=$(printf "%.0f\n" "$avg_init1_time_min")
avg_init2_time_sec=$(echo "init2_sec_tot" / "${#init2_times_sec[@]}" | bc -l)
round_init2_time_sec=$(printf "%.0f\n" "$avg_init2_time_sec")
avg_init2_time_min=$(echo "init2_min_tot" / "${#init2_times_min[@]}" | bc -l)
round_init2_time_min=$(printf "%.0f\n" "$avg_init2_time_min")

# Print the average rounded times
echo "Average hole time: $round_hole_time_sec seconds"
echo "Average hole time: $round_hole_time_min minutes"
echo "Average init_1 time: $round_init1_time_sec seconds"
echo "Average init_1 time: $round_init1_time_min minutes"
echo "Average init_2 time: $round_init2_time_sec seconds"
echo "Average init_2 time: $round_init2_time_min minutes"
