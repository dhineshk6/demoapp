import re

def extract_schedule_ids(file_path):
    schedule_ids = set()
    with open(file_path, 'r') as file:
        for line in file:
            schedule_match = re.search(r'scheduleID:\s*(\w+);', line)
            if schedule_match:
                schedule_id = schedule_match.group(1)
                schedule_ids.add(schedule_id)
    return schedule_ids

def compare_schedule_ids(log_files):
    schedules = {file_path: extract_schedule_ids(file_path) for file_path in log_files}

    matching_values = {}
    mismatching_values = {}
    for file_path, schedule_ids in schedules.items():
        other_files = [f for f in log_files if f != file_path]
        other_schedule_ids = set.union(*[schedules[f] for f in other_files])
        common_schedule_ids = schedule_ids.intersection(other_schedule_ids)

        for schedule_id in common_schedule_ids:
            if all(schedule_id in schedules[file_path] for file_path in log_files):
                matching_values[schedule_id] = list(schedule_ids)
            else:
                mismatching_values[schedule_id] = {file_path: list(schedule_ids)}

    return matching_values, mismatching_values

def write_output(matching_values, mismatching_values, output_file):
    with open(output_file, 'w') as file:
        file.write("Matching Schedule IDs:\n")
        for schedule_id, values in matching_values.items():
            file.write(f"{schedule_id}: {values}\n")

        file.write("\nMismatching Schedule IDs:\n")
        for schedule_id, values in mismatching_values.items():
            file.write(f"{schedule_id}: {values}\n")

if __name__ == "__main__":
    log_files = ["path/to/log1.log", "path/to/log2.log"]  # Update with your log file paths
    output_file = "output.txt"  # Update with your desired output file path

    matching_values, mismatching_values = compare_schedule_ids(log_files)
    write_output(matching_values, mismatching_values, output_file)

    print("Matching Schedule IDs:", matching_values)
    print("Mismatching Schedule IDs:", mismatching_values)
