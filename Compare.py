def compare_log_files():
    """
    Compare two log files and print all matching scheduled IDs and their values.
    If a scheduled ID is not matching, print its value from both files.
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
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if 'scheduleID:' in line:
                        parts = line.strip().split(';')
                        for part in parts:
                            if 'scheduleID:' in part:
                                schedule_id, value = part.strip().split(':')
                                scheduled_ids[schedule_id.strip()] = value.strip()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        return scheduled_ids

    file1_data = read_log_file(file1_path)
    file2_data = read_log_file(file2_path)
    
    print("File 1 Data:", file1_data)
    print("File 2 Data:", file2_data)

    common_ids = set(file1_data.keys()) & set(file2_data.keys())
    print("Common IDs:", common_ids)

    with open(output_file, 'w') as output:
        output.write("Matching scheduled IDs and their values:\n")
        for scheduled_id in common_ids:
            if file1_data.get(scheduled_id) == file2_data.get(scheduled_id):
                output.write(f"{scheduled_id}: {file1_data.get(scheduled_id)}; {file2_data.get(scheduled_id)}\n")

        output.write("\nNot matching scheduled IDs and their values from File 1:\n")
        for scheduled_id, value in file1_data.items():
            if scheduled_id not in common_ids:
                output.write(f"{scheduled_id}: {value}\n")

        output.write("\nNot matching scheduled IDs and their values from File 2:\n")
        for scheduled_id, value in file2_data.items():
            if scheduled_id not in common_ids:
                output.write(f"{scheduled_id}: {value}\n")

# Usage example:
compare_log_files()
