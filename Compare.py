import regex as re

def extract_schedule_ids(file_path):
    schedule_ids = {}
    with open(file_path, 'r') as file:
        for line in file:
            print(f"Processing line: {line.strip()}")  # Debugging statement
            schedule_match = re.search(r'scheduleID:\s*(\w+);', line)
            value_match = re.search(r'value:\s*(\w+);', line)
            if schedule_match and value_match:
                schedule_id = schedule_match.group(1)
                schedule_value = value_match.group(1)
                print(f"Extracted: ScheduleID={schedule_id}, Value={schedule_value}")  # Debugging statement
                schedule_ids[schedule_id] = schedule_value
    return schedule_ids

def compare_schedule_ids(log_files):
    schedules = {}
    for file_path in log_files:
        schedules[file_path] = extract_schedule_ids(file_path)

    matching_values = {}
    mismatching_values = {}
    for schedule_id in schedules[log_files[0]]:
        values = [schedules[file_path].get(schedule_id) for file_path in log_files]
        if all(values):
            if len(set(values)) == 1:
                matching_values[schedule_id] = values[0]
            else:
                mismatching_values[schedule_id] = values

    return matching_values, mismatching_values

def write_output(matching_values, mismatching_values, output_file):
    with open(output_file, 'w') as file:
        print("Writing output to file...")  # Debugging statement
        file.write("Matching Values:\n")
        for schedule_id, value in matching_values.items():
            file.write(f"{schedule_id}: {value}\n")

        file.write("\nMismatching Values:\n")
        for schedule_id, values in mismatching_values.items():
            file.write(f"{schedule_id}: {values}\n")

if __name__ == "__main__":
    log_files = ["log1.txt", "log2.txt"]  # Update with your log file paths
    output_file = "output.txt"  # Update with your desired output file path

    matching_values, mismatching_values = compare_schedule_ids(log_files)
    print("Matching Values:", matching_values)  # Debugging statement
    print("Mismatching Values:", mismatching_values)  # Debugging statement
    write_output(matching_values, mismatching_values, output_file)
