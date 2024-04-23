import re
import xml.etree.ElementTree as ET

def parse_log_line(line):
    """
    Parse a log line and extract schedule ID, schedule time, month, and date.
    """
    # Define regular expression patterns
    pattern_schedule_id = r'scheduleID=(\w+),'
    pattern_schedule_time = r'scheduleTime=(\d{2}:\d{2}:\d{2})'
    pattern_month_date = r'(\w{3}\s+\d{1,2})'
    pattern_xml_content = r'<data[^>]*>(.*?)<\/data>'

    # Search for patterns in the line
    match_schedule_id = re.search(pattern_schedule_id, line)
    match_schedule_time = re.search(pattern_schedule_time, line)
    match_month_date = re.search(pattern_month_date, line)
    match_xml_content = re.search(pattern_xml_content, line)

    # Extract schedule ID, schedule time, month, and date
    schedule_id = match_schedule_id.group(1) if match_schedule_id else None
    schedule_time = match_schedule_time.group(1) if match_schedule_time else None
    month_date = match_month_date.group(1) if match_month_date else None
    xml_content = match_xml_content.group(1) if match_xml_content else None

    # Return extracted values
    return schedule_id, schedule_time, month_date, xml_content

def compare_logs(log1_path, log2_path):
    """
    Compare two log files and identify matching and mismatching schedule IDs, times, and XML content.
    """
    log1_data = {}
    with open(log1_path, 'r') as log1_file:
        for line in log1_file:
            schedule_id, schedule_time, month_date, xml_content = parse_log_line(line)
            if schedule_id is not None:
                log1_data[schedule_id] = (schedule_time, month_date, xml_content)
    
    log2_data = {}
    with open(log2_path, 'r') as log2_file:
        for line in log2_file:
            schedule_id, schedule_time, month_date, xml_content = parse_log_line(line)
            if schedule_id is not None:
                log2_data[schedule_id] = (schedule_time, month_date, xml_content)

    matching = {k: (v, log2_data[k]) for k, v in log1_data.items() if k in log2_data}
    mismatching = {k: (v, log2_data[k]) for k, v in log1_data.items() if k not in log2_data}
    mismatching.update({k: (None, v) for k, v in log2_data.items() if k not in log1_data})
    
    return log1_data, log2_data, matching, mismatching

def print_log_data(log_data, file_name):
    """
    Print schedule IDs, times, months, and XML content from a log file.
    """
    print(f"Schedule IDs, Times, Months, and XML Content from {file_name}:")
    for schedule_id, (schedule_time, month_date, xml_content) in log_data.items():
        print(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time}, Month and Date: {month_date}, XML Content: {xml_content if xml_content else 'N/A'}")

if __name__ == "__main__":
    log1_path = "path/to/log1.txt"
    log2_path = "path/to/log2.txt"
    log1_data, log2_data, matching, mismatching = compare_logs(log1_path, log2_path)
    
    print_log_data(log1_data, "File 1")
    print()
    print_log_data(log2_data, "File 2")
    print()
    print("Matching:")
    for schedule_id, (data1, data2) in matching.items():
        print(f"Schedule ID: {schedule_id}")
        print(f"File 1: {data1}")
        print(f"File 2: {data2}")
        print()
    
    print("Mismatching:")
    for schedule_id, (data1, data2) in mismatching.items():
        print(f"Schedule ID: {schedule_id}")
        if data1 is not None:
            print(f"File 1: {data1}")
        if data2 is not None:
            print(f"File 2: {data2}")
        print()
