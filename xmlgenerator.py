import re
import os

def extract_and_save_xml_segments(log_file, output_dir):
    with open(log_file, 'r') as infile:
        recording = False
        segment = []
        segment_count = 0

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for line in infile:
            if "<ABC>" in line:
                recording = True
                segment = [line]  # Start a new segment
                continue

            if recording:
                segment.append(line)
                if "</ABC>" in line:
                    recording = False
                    # Save the segment to a new file
                    segment_count += 1
                    segment_filename = os.path.join(output_dir, f'segment_{segment_count}.xml')
                    with open(segment_filename, 'w') as segment_file:
                        segment_file.writelines(segment)

# Usage example with Windows file paths
log_file = r'C:\path\to\your\logfile.log'
output_dir = r'C:\path\to\output\directory'
extract_and_save_xml_segments(log_file, output_dir)
