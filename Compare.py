def parse_log_line(line):
    """
    Parse a log line and extract schedule ID, schedule time, and value.
    """
    parts = line.split('scheduleID=', 1)
    if len(parts) < 2:
        return None, None, None
    schedule_id, rest = parts[1].split(',', 1)
    time_parts = rest.split('scheduleTime=', 1)
    if len(time_parts) < 2:
        return None, None, None
    schedule_time, rest = time_parts[1].split(',', 1)
    value_parts = rest.split(',', 1)
    if len(value_parts) < 2:
        return None, None, None
    value, _ = value_parts[0].split(',', 1)
    return schedule_id.strip(), schedule_time.strip(), value.strip()

def compare_logs(log1_path, log2_path):
    """
    Compare two log files and identify matching and mismatching schedule IDs, times, and values.
    """
    log1_data = {}
    with open(log1_path, 'r') as log1_file:
        for line in log1_file:
            schedule_id, schedule_time, value = parse_log_line(line)
            if schedule_id is not None:
                log1_data[schedule_id] = (schedule_time, value)
    
    matching = []
    mismatching = []
    with open(log2_path, 'r') as log2_file:
        for line in log2_file:
            schedule_id, schedule_time, value = parse_log_line(line)
            if schedule_id is not None:
                if schedule_id in log1_data:
                    if log1_data[schedule_id] == (schedule_time, value):
                        matching.append((schedule_id, schedule_time, value))
                    else:
                        mismatching.append((schedule_id, log1_data[schedule_id], (schedule_time, value)))
    
    return matching, mismatching

if __name__ == "__main__":
    log1_path = "path/to/log1.txt"
    log2_path = "path/to/log2.txt"
    matching, mismatching = compare_logs(log1_path, log2_path)
    print("Matching:")
    for item in matching:
        print(item)
    print("Mismatching:")
    for item in mismatching:
        print(item)
