import re

def extract_data_from_log(file_path):
    xml_data = []
    schedule_data = []
    data_bin_paths = []
    with open(file_path, 'r') as file:
        seq_no_xml = 1
        seq_no_schedule = 1
        xml_content = ""
        for line in file:
            xml_content += line
            if "</LargeActionRequest>" in line:
                xml_tags = re.findall(r'<LargeActionRequest source="LargeAction" ReqFormatVersion="1">(.*?)</LargeActionRequest>', xml_content, re.DOTALL)
                for xml_tag in xml_tags:
                    xml_data.append((seq_no_xml, xml_tag))
                    seq_no_xml += 1
                xml_content = ""
            schedule_match = re.search(r'scheduleID=(\w+)', line)
            if schedule_match:
                schedule_id = schedule_match.group(1)
                time_match = re.search(r'scheduleTime=(\d{2}:\d{2}:\d{2})', line)
                if time_match:
                    schedule_time = time_match.group(1)
                    schedule_data.append((seq_no_schedule, schedule_id, schedule_time))
                    seq_no_schedule += 1
            data_bin_path_match = re.search(r'Data Bin Path:\s*(.*)', line)
            if data_bin_path_match:
                data_bin_path = data_bin_path_match.group(1)
                data_bin_paths.append(data_bin_path.strip())
    return xml_data, schedule_data, data_bin_paths

def extract_sending_time(xml_tag):
    sending_time_match = re.search(r'<SendingTime>\d{8}-(\d{2}:\d{2}:\d{2})\.\d{3}</SendingTime>', xml_tag)
    if sending_time_match:
        return sending_time_match.group(1)
    return None

def compare_logs(log_file1, log_file2):
    xml_data1, schedule_data1, data_bin_paths1 = extract_data_from_log(log_file1)
    xml_data2, schedule_data2, data_bin_paths2 = extract_data_from_log(log_file2)

    return xml_data1, xml_data2, schedule_data1, schedule_data2, data_bin_paths1, data_bin_paths2

def output_results(xml_data1, xml_data2, schedule_data1, schedule_data2, data_bin_paths1, data_bin_paths2, output_file):
    with open(output_file, 'w') as file:
        file.write("XML Tags and Schedule Information from File 1:\n")
        for seq_no, xml_tag in xml_data1:
            sending_time = extract_sending_time(xml_tag)
            if sending_time:
                file.write(f"Seq No: {seq_no} Load in File 1, XML: {xml_tag}, SendingTime: {sending_time}\n")
            else:
                file.write(f"Seq No: {seq_no} Load in File 1, XML: {xml_tag}\n")
        for seq_no, schedule_id, schedule_time in schedule_data1:
            file.write(f"Seq No: {seq_no} Load in File 1, ScheduleID: {schedule_id}, ScheduleTime: {schedule_time}\n")

        file.write("\nData Bin Paths from File 1:\n")
        for data_bin_path in data_bin_paths1:
            file.write(f"{data_bin_path}\n")

        file.write("\nXML Tags and Schedule Information from File 2:\n")
        for seq_no, xml_tag in xml_data2:
            sending_time = extract_sending_time(xml_tag)
            if sending_time:
                file.write(f"Seq No: {seq_no} Load in File 2, XML: {xml_tag}, SendingTime: {sending_time}\n")
            else:
                file.write(f"Seq No: {seq_no} Load in File 2, XML: {xml_tag}\n")
        for seq_no, schedule_id, schedule_time in schedule_data2:
            file.write(f"Seq No: {seq_no} Load in File 2, ScheduleID: {schedule_id}, ScheduleTime: {schedule_time}\n")

        file.write("\nData Bin Paths from File 2:\n")
        for data_bin_path in data_bin_paths2:
            file.write(f"{data_bin_path}\n")

        file.write("\nComparison:\n")
        if data_bin_paths1 == data_bin_paths2:
            file.write("Data Bin Paths match in both files.\n")
        else:
            file.write("Data Bin Paths do not match in both files.\n")

        file.write("\nXML Tag Comparison:\n")
        for seq_no1, xml1 in xml_data1:
            found_matching = False
            for seq_no2, xml2 in xml_data2:
                if seq_no1 == seq_no2 and xml1 == xml2:
                    file.write(f"Seq No: {seq_no1} Load in File 1 matching Seq No: {seq_no2} in File 2\n")
                    found_matching = True
                    break
            if found_matching:
                continue
            file.write(f"Seq No: {seq_no1} Load in File 1 mismatching in File 2\n")

        for seq_no2, xml2 in xml_data2:
            found_matching = False
            for seq_no1, xml1 in xml_data1:
                if seq_no1 == seq_no2:
                    found_matching = True
                    break
            if not found_matching:
                file.write(f"Seq No: {seq_no2} Load in File 2 mismatching in File 1\n")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"
    output_file = "comparison_output.txt"

    xml_data1, xml_data2, schedule_data1, schedule_data2, data_bin_paths1, data_bin_paths2 = compare_logs(file1, file2)
    output_results(xml_data1, xml_data2, schedule_data1, schedule_data2, data_bin_paths1, data_bin_paths2, output_file)

    print(f"Comparison output written to {output_file}")
