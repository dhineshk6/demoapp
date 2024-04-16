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
                parts = line.strip().split('[')
                if len(parts) > 1:
                    schedule_part = parts[1].split(']')[0]
                    schedule_parts = schedule_part.split('; ')
                    for schedule in schedule_parts:
                        schedule_pair = schedule.split(': ')
                        if len(schedule_pair) == 2:
                            key = schedule_pair[0].strip()
                            value = schedule_pair[1].strip()
                            if key == 'scheduleID':
                                scheduled_ids[value] = value
        print(f"Data extracted from {file_path}: {scheduled_ids}")
        return scheduled_ids

    file1_data = read_log_file(file1_path)
    file2_data = read_log_file(file2_path)
    
    print("File 1 Data:", file1_data)
    print("File 2 Data:", file2_data)

    common_ids = set(file1_data.keys()) & set(file2_data.keys())
    print("Common IDs:", common_ids)

    matching_ids = [scheduled_id for scheduled_id in common_ids if file1_data[scheduled_id] == file2_data[scheduled_id]]
    print("Matching IDs:", matching_ids)

    mismatching_ids = [scheduled_id for scheduled_id in common_ids if file1_data[scheduled_id] != file2_data[scheduled_id]]
    print("Mismatching IDs:", mismatching_ids)

    with open(output_file, 'w') as output:
        output.write("Matching scheduled IDs and their values:\n")
        for scheduled_id in matching_ids:
            output.write(f"{scheduled_id}: {file1_data[scheduled_id]};\n")

        output.write("\nNot matching scheduled IDs and their values:\n")
        for scheduled_id in mismatching_ids:
            output.write(f"{scheduled_id}: {file1_data.get(scheduled_id, 'Not found')}; {file2_data.get(scheduled_id, 'Not found')};\n")

# Usage example:
compare_log_files()
