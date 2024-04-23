import re

def extract_data_from_log(file_path):
    schedule_data = []
    with open(file_path, 'r') as file:
        for line in file:
            schedule_match = re.search(r'scheduleID:\s*(\w+);\s*time:\s*(\d{2}:\d{2}:\d{2});\s*xml:\s*(.+)', line)
            if schedule_match:
                schedule_id = schedule_match.group(1)
                time = schedule_match.group(2)
                xml_content = schedule_match.group(3)
                schedule_data.append((schedule_id, time, xml_content))
    return schedule_data

def compare_logs(log_file1, log_file2):
    data_file1 = extract_data_from_log(log_file1)
    data_file2 = extract_data_from_log(log_file2)

    matching_data = []
    mismatching_data = []

    for item1 in data_file1:
        for item2 in data_file2:
            if item1[0] == item2[0] and item1[1] == item2[1] and item1[2] == item2[2]:
                matching_data.append((item1, item2))
                break
        else:
            mismatching_data.append(item1)

    return data_file1, data_file2, matching_data, mismatching_data

def output_results(file1_data, file2_data, matching_data, mismatching_data):
    with open("output.txt", 'w') as file:
        file.write("Data from File 1:\n")
        for item in file1_data:
            file.write(f"scheduleID: {item[0]}, time: {item[1]}, xml: {item[2]}\n")

        file.write("\nData from File 2:\n")
        for item in file2_data:
            file.write(f"scheduleID: {item[0]}, time: {item[1]}, xml: {item[2]}\n")

        file.write("\nMatching Data:\n")
        for item1, item2 in matching_data:
            file.write(f"From File 1: scheduleID: {item1[0]}, time: {item1[1]}, xml: {item1[2]}\n")
            file.write(f"From File 2: scheduleID: {item2[0]}, time: {item2[1]}, xml: {item2[2]}\n")
        
        file.write("\nMismatching Data from File 1:\n")
        for item in mismatching_data:
            file.write(f"scheduleID: {item[0]}, time: {item[1]}, xml: {item[2]}\n")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"

    file1_data, file2_data, matching_data, mismatching_data = compare_logs(file1, file2)
    output_results(file1_data, file2_data, matching_data, mismatching_data)
