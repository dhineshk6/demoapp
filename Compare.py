def compare_schedules(log_files, output_file):
  """
  Compares scheduleIDs and their values from multiple log files.

  Args:
    log_files: A list of paths to the log files.
    output_file: The path to the output text file.
  """

  # Initialize empty dictionaries to store schedule data
  all_schedules = {}
  matching_schedules = {}
  mismatching_schedules = {}

  # Read each log file
  for log_file in log_files:
    with open(log_file, 'r') as f:
      for line in f:
        # Extract scheduleID and value from the line
        schedule_id, value = parse_log_line(line)
        if schedule_id not in all_schedules:
          all_schedules[schedule_id] = {}
        all_schedules[schedule_id][log_file] = value

  # Compare schedules
  for schedule_id, schedule_data in all_schedules.items():
    # Check if all values are the same
    if len(set(schedule_data.values())) == 1:
      matching_schedules[schedule_id] = schedule_data
    else:
      mismatching_schedules[schedule_id] = schedule_data

  # Write results to output file
  with open(output_file, 'w') as f:
    f.write("Matching Schedules:\n")
    if matching_schedules:
      for schedule_id, data in matching_schedules.items():
        f.write(f"\tScheduleID: {schedule_id}\n")
        for log_file, value in data.items():
          f.write(f"\t\tLog file: {log_file}, Value: {value}\n")
    else:
      f.write("\tNo matching schedules found.\n")

    f.write("Mismatching Schedules:\n")
    if mismatching_schedules:
      for schedule_id, data in mismatching_schedules.items():
        f.write(f"\tScheduleID: {schedule_id}\n")
        for log_file, value in data.items():
          f.write(f"\t\tLog file: {log_file}, Value: {value}\n")
    else:
      f.write("\tNo mismatching schedules found.\n")

# Function to parse a log line and extract scheduleID and value
def parse_log_line(line):
  # Extract scheduleID and value based on your format
  parts = line.strip().split(':', 1)
  return parts[0], parts[1].split(';')[0]

# Example usage (replace with your actual file paths)
# log_files = ["path/to/log_file1.txt", "path/to/log_file2.txt", "path/to/log_file3.txt"]
# output_file = "path/to/comparison_results.txt"
# compare_schedules(log_files, output_file)

# Print("Results written to", output_file)

# Uncomment the example usage section above and replace the file paths 
# to run the script with your specific log files and output file.
