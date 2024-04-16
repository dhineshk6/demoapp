def compare_log_files():
    """
    Compare two log files and print matching and mismatching scheduled IDs and their values.
    """
    file1_path = "file1.log"  # Hardcoded file path for file 1
    file2_path = "file2.log"  # Hardcoded file path for file 2
    output_file = "comparison_output.txt"  # Output file path

    def read_log_file(file_path):
        """
        Read a log file and return a dictionary with scheduled IDs as keys and their corresponding values.
        Exclude time, process ID, memory usage, and file descriptors from the log.
        """
        scheduled_ids = {}
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line based on '[' and ']'
                parts = line.strip().split('[')
                if len(parts) > 1:
                    schedule_part = parts[1].split(']')[0]
                    schedule_parts = schedule_part.split('; ')
                    for schedule in schedule_parts:
                        # Split the schedule into key-value pairs
                        schedule_pair = schedule.split(': ')
                        if len(schedule_pair) == 2:
                            key = schedule_pair[0].strip()
                            value = schedule_pair[1].strip()
                            # Extracting only the 'scheduleID' key
                            if key == 'scheduleID':
                                scheduled_ids[key] = value
        return scheduled_ids

    file1_data = read_log_file(file1_path)
    file2_data = read_log_file(file2_path)

    common_ids = set(file1_data.keys()) & set(file2_data.keys())

    matching_ids = [scheduled_id for scheduled_id in common_ids if file1_data[scheduled_id] == file2_data[scheduled_id]]
    mismatching_ids = [scheduled_id for scheduled_id in common_ids if file1_data[scheduled_id] != file2_data[scheduled_id]]

    with open(output_file, 'w') as output:
        output.write("Matching scheduled IDs and their values:\n")
        for scheduled_id in matching_ids:
            output.write(f"{scheduled_id}: {file1_data[scheduled_id]};\n")

        output.write("\nNot matching scheduled IDs and their values:\n")
        for scheduled_id in mismatching_ids:
            output.write(f"{scheduled_id}: {file1_data.get(scheduled_id, 'Not found')}; {file2_data.get(scheduled_id, 'Not found')};\n")

# Usage example:
compare_log_files()
