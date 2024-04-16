import gzip

def read_log_file(file_path):
    """
    Read a log file (compressed or uncompressed) and return a dictionary with scheduled IDs as keys and their corresponding values.
    """
    scheduled_ids = {}
    if file_path.endswith('.gz'):
        with gzip.open(file_path, 'rt') as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    scheduled_id, value = parts
                    scheduled_ids[scheduled_id] = value
                else:
                    print(f"Ignoring invalid line: {line}")
    else:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    scheduled_id, value = parts
                    scheduled_ids[scheduled_id] = value
                else:
                    print(f"Ignoring invalid line: {line}")
    return scheduled_ids

def compare_log_files():
    """
    Compare two log files (one of which can be compressed) and check if they have the same values for the scheduled IDs.
    """
    file1_path = "file1.log"  # Hardcoded file path for file 1
    file2_path = "file2.log.gz"  # Hardcoded file path for file 2 (compressed)

    file1_data = read_log_file(file1_path)
    file2_data = read_log_file(file2_path)

    common_ids = set(file1_data.keys()) & set(file2_data.keys())

    for scheduled_id in common_ids:
        if file1_data[scheduled_id] != file2_data[scheduled_id]:
            print(f"Scheduled ID {scheduled_id} has different values in the two log files:")
            print(f"File 1: {file1_data[scheduled_id]}")
            print(f"File 2: {file2_data[scheduled_id]}")
            print()

    unique_ids_file1 = set(file1_data.keys()) - set(file2_data.keys())
    unique_ids_file2 = set(file2_data.keys()) - set(file1_data.keys())

    if unique_ids_file1:
        print("Scheduled IDs present only in File 1:")
        for scheduled_id in unique_ids_file1:
            print(f"{scheduled_id}: {file1_data[scheduled_id]}")
        print()

    if unique_ids_file2:
        print("Scheduled IDs present only in File 2:")
        for scheduled_id in unique_ids_file2:
            print(f"{scheduled_id}: {file2_data[scheduled_id]}")

# Usage example:
compare_log_files()
