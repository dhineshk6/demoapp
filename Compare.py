def read_log_file(file_path):
    """
    Read a log file and return a dictionary with scheduled IDs as keys and their corresponding values.
    """
    scheduled_ids = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                scheduled_id, value = parts
                scheduled_ids[scheduled_id] = value
    return scheduled_ids

def compare_log_files():
    """
    Compare two log files and check if they have the same values for the scheduled IDs.
    """
    file1_path = "file1.log"  # Hardcoded file path for file 1
    file2_path = "file2.log"  # Hardcoded file path for file 2
    output_file = "comparison_output.txt"  # Output file path

    with open(output_file, 'w') as output:
        file1_data = read_log_file(file1_path)
        file2_data = read_log_file(file2_path)

        common_ids = set(file1_data.keys()) & set(file2_data.keys())

        for scheduled_id in common_ids:
            if file1_data[scheduled_id] != file2_data[scheduled_id]:
                output.write(f"Scheduled ID {scheduled_id} has different values in the two log files:\n")
                output.write(f"File 1: {file1_data[scheduled_id]}\n")
                output.write(f"File 2: {file2_data[scheduled_id]}\n\n")

        unique_ids_file1 = set(file1_data.keys()) - set(file2_data.keys())
        unique_ids_file2 = set(file2_data.keys()) - set(file1_data.keys())

        if unique_ids_file1:
            output.write("Scheduled IDs present only in File 1:\n")
            for scheduled_id in unique_ids_file1:
                output.write(f"{scheduled_id}: {file1_data[scheduled_id]}\n")
            output.write("\n")

        if unique_ids_file2:
            output.write("Scheduled IDs present only in File 2:\n")
            for scheduled_id in unique_ids_file2:
                output.write(f"{scheduled_id}: {file2_data[scheduled_id]}\n")

# Usage example:
compare_log_files()
