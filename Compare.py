def parse_log_line(line):
    """
    Parse a log line and extract schedule ID, schedule time, and value.
    """
    parts = line.split('scheduleID=')
    if len(parts) < 2:
        return None, None
    schedule_id, rest = parts[1].split(',', 1)
    
    time_parts = rest.split('scheduleTime=')
    if len(time_parts) < 2:
        return None, None
    schedule_time, _ = time_parts[1].split(',', 1)

    return schedule_id.strip(), schedule_time.strip()

def compare_logs(log1_path, log2_path):
    """
    Compare two log files and identify matching and mismatching schedule IDs and times.
    """
    log1_data = set()
    with open(log1_path, 'r') as log1_file:
        for line in log1_file:
            schedule_id, schedule_time = parse_log_line(line)
            if schedule_id is not None:
                log1_data.add((schedule_id, schedule_time))
    
    log2_data = set()
    with open(log2_path, 'r') as log2_file:
        for line in log2_file:
            schedule_id, schedule_time = parse_log_line(line)
            if schedule_id is not None:
                log2_data.add((schedule_id, schedule_time))

    matching = log1_data.intersection(log2_data)
    mismatching = log1_data.symmetric_difference(log2_data)
    
    return matching, mismatching

if __name__ == "__main__":
    log1_path = "path/to/log1.txt"
    log2_path = "path/to/log2.txt"
    matching, mismatching = compare_logs(log1_path, log2_path)
    
    print("Matching:")
    for schedule_id, schedule_time in matching:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}")

    print("\nMismatching:")
    for schedule_id, schedule_time in mismatching:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}")
