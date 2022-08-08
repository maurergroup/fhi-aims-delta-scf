#!/bin/bash

# Exit if an error occurs
set -e

script_usage () {
  echo "Script Usage:"
  echo "1st argument: Time to parse from aims.out (options: scf or total)"
  echo "2nd argument: Directories to search for timings"
  exit 1
}

# Argument checker
if [[ $1 != "total" && $1 != "scf" ]]; then
  echo "Incorrect timing type argument specified"
  echo
  script_usage
elif [[ $2 == "" ]]; then
  echo "Directories argument not specified"
  echo
  script_usage
fi

scf_timings () {
  # Read scf timings from aims.out and add to array
  scf_times=()
  scf_times+=($(cat aims.out | grep '| Time for this iteration' | awk '{ print $7 }'))

  # Initialise counters and penultimate index of scf_times
  iter_count_1=0
  iter_count_2=0
  scf_times_len_short=$(("${#scf_times[@]}" - 1))

  # Difference between kth value and k+1 value
  for k in "${scf_times[@]::$scf_times_len_short}"; do
    iter_count_1=$((iter_count_1 + 1))
    current_iter=$(echo "${scf_times[$iter_count_2]}")
    next_iter=$(echo "${scf_times[$iter_count_1]}")
    iter_diff=$(echo "$current_iter - $next_iter" | bc -l)

    # Use values after first value where difference between scf values is
    # less than 1
    if (( $(echo "$iter_diff < 1" | bc -l) )); then
      stab_times_index="$iter_count_2"
      break
    fi

    iter_count_2=$((iter_count_2 + 1))
  done

  # New array of stablised scf times
  stab_scf_times=()
  stab_scf_times+=("${scf_times[@]:$stab_times_index}")

  # Sum all scf times
  stab_scf_times_tot=0
  for k in "${stab_scf_times[@]}"; do
    stab_scf_times_tot=$(echo "$stab_scf_times_tot + $k" | bc -l)
  done

  # Average and round time per scf step
  avg_stab_scf_time=$(echo "$stab_scf_times_tot" / "${#stab_scf_times[@]}" | bc -l)
  round_stab_scf_time=$(printf "%.2f\n" "$avg_stab_scf_time")

  echo "$i $j"
  echo "Number of SCF iterations averaged: ${#stab_scf_times[@]}"
  echo "Average time per SCF step: $round_stab_scf_time sec"
  echo
}

# Add all user specified directories to an array
for i in "${@:2}"; do
  input_dirs+=("$i")
done

echo "Specified directories:" "${input_dirs[@]}"
echo

# Go into directories and files to read timings
for i in "${input_dirs[@]}"; do
  cd "$i"
  for j in *; do
    run_type="$j"
    if [ -d "$j" ]; then
      if [[ $1 == "total" ]]; then
        # If a directory, this is an excited state calculation
        atom="$i"
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

      elif [[ $1 == "scf" ]]; then
        cd "$j"
        scf_timings
      fi

    elif [[ "$j" == "aims.out" ]]; then
      if [[ "$1" == "total" ]]; then
        # This must be a ground state calculation
        # Find time taken in aims.out
        ground_state="true"
        time=$(tail -n 100 "$j" | grep '| Total time   ' | awk '{ print $5 }')
        time_round=$(printf "%.0f\n" "$time")
        time_h=$(echo "$time_round" / 60 | bc -l)
        time_hr=$(printf "%.2f\n" "$time_h")
        echo "ground: $time_round seconds"
        echo "ground: $time_hr minutes"
        echo
      elif [[ "$1" == "scf" ]]; then
        scf_timings
      fi
    fi

    cd ../
  done

  cd ../
done

if [[ "$1" == "total" && "$ground_state" != "true" ]]; then
  # Sum counters
  hole_sec_tot=0
  init1_sec_tot=0
  init2_sec_tot=0

  # Calculate the sum of each array
  for i in "${hole_times_sec[@]}"; do
    ((hole_sec_tot+=i))
  done
  for i in "${init1_times_sec[@]}"; do
    ((init1_sec_tot+=i))
  done
  for i in "${init2_times_sec[@]}"; do
    ((init2_sec_tot+=i))
  done

  # Calculate average times and round
  avg_hole_time_sec=$(echo "$hole_sec_tot" / "${#hole_times_sec[@]}" | bc -l)
  round_hole_time_sec=$(printf "%.0f\n" "$avg_hole_time_sec")
  avg_init1_time_sec=$(echo "$init1_sec_tot" / "${#init1_times_sec[@]}" | bc -l)
  round_init1_time_sec=$(printf "%.0f\n" "$avg_init1_time_sec")
  avg_init2_time_sec=$(echo "$init2_sec_tot" / "${#init2_times_sec[@]}" | bc -l)
  round_init2_time_sec=$(printf "%.0f\n" "$avg_init2_time_sec")

  round_hole_time_min=$(printf "%.2f\n" "$(echo "$round_hole_time_sec" / 60 | bc -l)")
  round_init1_time_min=$(printf "%.2f\n" "$(echo "$round_init1_time_sec" / 60 | bc -l)")
  round_init2_time_min=$(printf "%.2f\n" "$(echo "$round_init2_time_sec" / 60 | bc -l)")

  # Print the average rounded times
  echo "Average hole time: $round_hole_time_sec seconds"
  echo "Average hole time: $round_hole_time_min minutes"
  echo "Average init_1 time: $round_init1_time_sec seconds"
  echo "Average init_1 time: $round_init1_time_min minutes"
  echo "Average init_2 time: $round_init2_time_sec seconds"
  echo "Average init_2 time: $round_init2_time_min minutes"
fi

