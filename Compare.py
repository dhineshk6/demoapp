import re

def extract_data_from_log(file_path):
    xml_data = []
    schedule_data = []
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
    return xml_data, schedule_data

def extract_sending_time(xml_tag):
    sending_time_match = re.search(r'<SendingTime>\d{8}-(\d{2}:\d{2}:\d{2})\.\d{3}</SendingTime>', xml_tag)
    if sending_time_match:
        return sending_time_match.group(1)
    return None

def compare_logs(log_file1, log_file2):
    xml_data1, schedule_data1 = extract_data_from_log(log_file1)
    xml_data2, schedule_data2 = extract_data_from_log(log_file2)

    return xml_data1, xml_data2, schedule_data1, schedule_data2

def output_results(xml_data1, xml_data2, schedule_data1, schedule_data2, output_file):
    with open(output_file, 'w') as file:
        file.write("XML Tags and Schedule Information from File 1:\n")
        for seq_no, xml_tag in xml_data1:
            sending_time = extract_sending_time(xml_tag)
            if sending_time:
                file.write(f"Seq No: {seq_no}, XML: {xml_tag}, SendingTime: {sending_time}\n")
            else:
                file.write(f"Seq No: {seq_no}, XML: {xml_tag}\n")
        for seq_no, schedule_id, schedule_time in schedule_data1:
            file.write(f"Seq No: {seq_no}, ScheduleID: {schedule_id}, ScheduleTime: {schedule_time}\n")

        file.write("\nXML Tags and Schedule Information from File 2:\n")
        for seq_no, xml_tag in xml_data2:
            sending_time = extract_sending_time(xml_tag)
            if sending_time:
                file.write(f"Seq No: {seq_no}, XML: {xml_tag}, SendingTime: {sending_time}\n")
            else:
                file.write(f"Seq No: {seq_no}, XML: {xml_tag}\n")
        for seq_no, schedule_id, schedule_time in schedule_data2:
            file.write(f"Seq No: {seq_no}, ScheduleID: {schedule_id}, ScheduleTime: {schedule_time}\n")

        file.write("\nComparison:\n")
        matching_orders = []
        mismatching_orders = []
        for (seq_no1, xml1), (seq_no2, xml2) in zip(xml_data1, xml_data2):
            sending_time1 = extract_sending_time(xml1)
            sending_time2 = extract_sending_time(xml2)
            if sending_time1 and sending_time2 and sending_time1.split(':')[0] == sending_time2.split(':')[0] and sending_time1.split(':')[1] == sending_time2.split(':')[1] and sending_time1.split(':')[2] == sending_time2.split(':')[2]:
                matching_orders.append(seq_no1)
            else:
                mismatching_orders.append((seq_no1, seq_no2))

        if matching_orders:
            file.write("\nMatching Seq Nos:\n")
            for seq_no in matching_orders:
                file.write(f"Seq No: {seq_no}\n")

        if mismatching_orders:
            file.write("\nMismatching Seq Nos:\n")
            for seq_no1, seq_no2 in mismatching_orders:
                file.write(f"Seq No: {seq_no1} from File 1 does not match Seq No: {seq_no2} from File 2\n")

if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"
    output_file = "comparison_output.txt"

    xml_data1, xml_data2, schedule_data1, schedule_data2 = compare_logs(file1, file2)
    output_results(xml_data1, xml_data2, schedule_data1, schedule_data2, output_file)

    print(f"Comparison output written to {output_file}")
