#!/bin/bash

HOSTFILE="hosts.txt"  # Your file containing the list of hosts
OUTPUTFILE="mount_status.txt"

# Clear the output file before writing new results
> "$OUTPUTFILE"

# Loop through each host in the file
while read -r host; do
    echo "Checking $host..."
    
    # Connect via zssh and execute the commands
    result=$(zssh username@"$host" <<EOF
    cd /var/hostlinks/"$host" && df -h
    exit
EOF
)

    # Check if /d/d1 is in the result
    if echo "$result" | grep -q "/d/d1"; then
        echo "$host yes" >> "$OUTPUTFILE"
    else
        echo "$host no" >> "$OUTPUTFILE"
    fi

done < "$HOSTFILE"

echo "Check completed. Results saved in $OUTPUTFILE."
