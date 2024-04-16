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
