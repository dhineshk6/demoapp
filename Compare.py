import re

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

def compare_logs(log1_path, log2_path, output_file):
    """
    Compare two log files and identify matching and mismatching schedule IDs and times.
    """
    log1_data = set()
    with open(log1_path, 'r') as log1_file:
        for line in log1_file:
            schedule_id, schedule_time, month_date, xml_content = parse_log_line(line)
            if schedule_id is not None:
                log1_data.add((schedule_id, schedule_time, month_date, xml_content))
    
    log2_data = set()
    with open(log2_path, 'r') as log2_file:
        for line in log2_file:
            schedule_id, schedule_time, month_date, xml_content = parse_log_line(line)
            if schedule_id is not None:
                log2_data.add((schedule_id, schedule_time, month_date, xml_content))

    matching = log1_data.intersection(log2_data)
    mismatching = log1_data.symmetric_difference(log2_data)
    
    # Write output to file
    with open(output_file, 'w') as f:
        f.write("Schedule IDs, Times, Months, and XML Content from File 1:\n")
        for schedule_id, schedule_time, month_date, xml_content in log1_data:
            f.write(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time},  XML Content: {xml_content}\n")

        f.write("\nSchedule IDs, Times, Months, and XML Content from File 2:\n")
        for schedule_id, schedule_time, month_date, xml_content in log2_data:
            f.write(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time},  XML Content: {xml_content}\n")

        f.write("\nMatching:\n")
        for schedule_id, schedule_time, month_date, xml_content in matching:
            f.write(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time},  XML Content: {xml_content}\n")

        f.write("\nMismatching:\n")
        for schedule_id, schedule_time, month_date, xml_content in mismatching:
            f.write(f"Schedule ID: {schedule_id}, Schedule Time: {schedule_time},  XML Content: {xml_content}\n")

if __name__ == "__main__":
    log1_path = "path/to/log1.txt"
    log2_path = "path/to/log2.txt"
    output_file = "output.txt"
    compare_logs(log1_path, log2_path, output_file)
