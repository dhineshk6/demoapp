import re

def extract_schedule_ids(file_path):
    schedule_ids = {}
    with open(file_path, 'r') as file:
        for line in file:
            schedule_match = re.search(r'scheduleID:\s*(\w+);', line)
            value_match = re.search(r'value:\s*(\w+);', line)
            if schedule_match and value_match:
                schedule_id = schedule_match.group(1)
                schedule_value = value_match.group(1)
                if schedule_id not in schedule_ids:
                    schedule_ids[schedule_id] = []
                schedule_ids[schedule_id].append(schedule_value)
    
    print(f"Extracted Schedule IDs from {file_path}: {schedule_ids}")  # Debugging statement
    return schedule_ids

def compare_schedule_ids(log_files):
    schedules = {}
    for file_path in log_files:
        schedules[file_path] = extract_schedule_ids(file_path)

    common_schedule_ids = set(schedules[log_files[0]].keys())
    for file_path in log_files[1:]:
        common_schedule_ids.intersection_update(schedules[file_path].keys())

    matching_values = {}
    mismatching_values = {}
    for schedule_id in common_schedule_ids:
        values = [schedules[file_path][schedule_id] for file_path in log_files]
        if len(set(values)) == 1:
            matching_values[schedule_id] = values[0][0]
        else:
            mismatching_values[schedule_id] = values

    return matching_values, mismatching_values

def write_output(matching_values, mismatching_values, output_file):
    print("Writing output to file...")  # Debugging statement
    output_str = ""

    output_str += "Matching Values:\n"
    for schedule_id, value in matching_values.items():
        output_str += f"{schedule_id}: {value}\n"

    output_str += "\nMismatching Values:\n"
    for schedule_id, values in mismatching_values.items():
        output_str += f"{schedule_id}: {values}\n"

    print("Output string:", output_str)  # Debugging statement

    try:
        with open(output_file, 'w') as file:
            file.write(output_str)
        print("Output successfully written to file.")
    except Exception as e:
        print("Error occurred while writing to file:", e)

if __name__ == "__main__":
    log_files = ["path/to/log1{{}}.txt", "path/to/log2{{}}.txt"]  # Update with your log file paths
    output_file = "output{{}}.txt"  # Update with your desired output file path

    # Process log files
    formatted_log_files = [file_path.format(i) for i, file_path in enumerate(log_files)]
    output_file = output_file.format("")

    matching_values, mismatching_values = compare_schedule_ids(formatted_log_files)
    print("Matching Values:", matching_values)  # Debugging statement
    print("Mismatching Values:", mismatching_values)  # Debugging statement

    write_output(matching_values, mismatching_values, output_file)
