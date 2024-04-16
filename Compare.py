def read_log_file(file_path):
    
    scheduled_ids = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('; ')
            scheduled_id = None
            value = None
            for part in parts:
                key_value = part.split(': ')
                if len(key_value) == 2:
                    key, val = key_value
                    if key.strip() == "scheduledID":
                        scheduled_id = val.strip()
                    elif key.strip() == "value":
                        value = val.strip()
            if scheduled_id is not None and value is not None:
                scheduled_ids[scheduled_id] = value
    return scheduled_ids

def compare_log_files():
    """
    Compare two log files and print matching and mismatching scheduled IDs and their values.
    """
    file1_path = "file1.log"  # Hardcoded file path for file 1
    file2_path = "file2.log"  # Hardcoded file path for file 2
    output_file = "comparison_output.txt"  # Output file path

    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2, open(output_file, 'w') as output:
        file1_data = read_log_file(file1_path)
        file2_data = read_log_file(file2_path)

        common_ids = set(file1_data.keys()) & set(file2_data.keys())

        output.write("Matching scheduled IDs and their values:\n")
        for scheduled_id in common_ids:
            if file1_data[scheduled_id] == file2_data[scheduled_id]:
                output.write(f"{scheduled_id}: {file1_data[scheduled_id]}\n")

        output.write("\nMismatching scheduled IDs and their values:\n")
        for scheduled_id in common_ids:
            if file1_data.get(scheduled_id) != file2_data.get(scheduled_id):
                output.write(f"{scheduled_id}: \n")
                output.write(f"  File 1: {file1_data.get(scheduled_id)}\n")
                output.write(f"  File 2: {file2_data.get(scheduled_id)}\n")

# Usage example:
compare_log_files()
