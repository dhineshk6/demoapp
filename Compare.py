import difflib

def compare_log_files(file1_path, file2_path):
    # Read the content of the first log file
    with open(file1_path, 'r') as file1:
        file1_lines = file1.readlines()

    # Read the content of the second log file
    with open(file2_path, 'r') as file2:
        file2_lines = file2.readlines()

    sentences_to_compare = [
        "Error: Connection timed out",
        "Warning: Disk space low"
    ]

    # Use difflib to find the differences between the two files
    differ = difflib.Differ()
    diff = differ.compare(file1_lines, file2_lines)

    # Print only the sentences that are matching and mismatching
    for line in diff:
        for sentence in sentences_to_compare:
            if sentence in line:
                if line.startswith('  '):
                    print(f"Matching: {line.strip()}")
                elif line.startswith('- '):
                    print(f"Mismatching in File 1: {line.strip()}")
                elif line.startswith('+ '):
                    print(f"Mismatching in File 2: {line.strip()}")
                break
