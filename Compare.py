if __name__ == "__main__":
    file1 = "file1.log"
    file2 = "file2.log"
    output_file = "comparison_output.txt"
    xml_data1, xml_data2, schedule_data1, schedule_data2, data_bin_paths1, data_bin_paths2 = compare_logs(file1, file2)

    # Keep track of matched sequence numbers from File 2
    matched_seq_numbers_file2 = set()

    with open(output_file, 'w') as file:
        # Previous code for writing to the output file...
        file.write("\nXML Tag Comparison:\n")
        for seq_no1, xml1 in xml_data1:
            found_matching = False
            for seq_no2, xml2 in xml_data2:
                if seq_no2 not in matched_seq_numbers_file2 and xml1[1] == xml2[1]:
                    file.write(f"Seq No: {seq_no1} Load in File 1 matching Seq No: {seq_no2} in File 2\n")
                    found_matching = True
                    # Mark the sequence number from File 2 as matched
                    matched_seq_numbers_file2.add(seq_no2)
                    break
            if not found_matching:
                file.write(f"Seq No: {seq_no1} Load in File 1 mismatching in File 2\n")

        # Remaining code for comparison and writing to the output file...
