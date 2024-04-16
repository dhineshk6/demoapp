import re

def parse_log_line(line):
    """
    Parse a log line and extract schedule ID, schedule time, month, and date.
    """
    match = re.search(r'(\w{3}\s+\d{1,2})', line)
    if match:
        month_date = match.group(1)
    else:
        month_date = None

    parts = line.split('scheduleID=')
    if len(parts) < 2:
        return None, None, None, None
    schedule_id, rest = parts[1].split(',', 1)
    
    time_parts = rest.split('scheduleTime=')
    if len(time_parts) < 2:
        return None, None, None, None
    schedule_time, _ = time_parts[1].split(',', 1)

    return schedule_id.strip(), schedule_time.strip(), month_date.strip() if month_date else None

def compare_logs(log1_path, log2_path):
    """
    Compare two log files and identify matching and mismatching schedule IDs, times, months, and dates.
    """
    log1_data = set()
    with open(log1_path, 'r') as log1_file:
        for line in log1_file:
            schedule_id, schedule_time, month_date = parse_log_line(line)
            if schedule_id is not None:
                log1_data.add((schedule_id, schedule_time, month_date))
    
    log2_data = set()
    with open(log2_path, 'r') as log2_file:
        for line in log2_file:
            schedule_id, schedule_time, month_date = parse_log_line(line)
            if schedule_id is not None:
                log2_data.add((schedule_id, schedule_time, month_date))

    matching = log1_data.intersection(log2_data)
    mismatching = log1_data.symmetric_difference(log2_data)
    
    return log1_data, log2_data, matching, mismatching

if __name__ == "__main__":
    log1_path = "path/to/log1.txt"
    log2_path = "path/to/log2.txt"
    log1_data, log2_data, matching, mismatching = compare_logs(log1_path, log2_path)
    
    print("Schedule IDs, Times, Months, and Dates from File 1:")
    for schedule_id, schedule_time, month_date in log1_data:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}, Month and Date: {month_date if month_date else 'N/A'}")

    print("\nSchedule IDs, Times, Months, and Dates from File 2:")
    for schedule_id, schedule_time, month_date in log2_data:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}, Month and Date: {month_date if month_date else 'N/A'}")

    print("\nMatching:")
    for schedule_id, schedule_time, month_date in matching:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}, Month and Date: {month_date if month_date else 'N/A'}")

    print("\nMismatching:")
    for schedule_id, schedule_time, month_date in mismatching:
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}, Month and Date: {month_date if month_date else 'N/A'}")
