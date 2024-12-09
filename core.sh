#!/bin/bash

# Prompt the user for the hostname
read -p "Enter the hostname of the target system: " HOSTNAME

# Define the target directory on the remote host
TARGET_DIR="/var/tmp/cores"

# Check if the user entered a hostname
if [ -z "$HOSTNAME" ]; then
    echo "No hostname provided. Exiting..."
    exit 1
fi

# Check if we can connect to the host via SSH
ssh -q "$HOSTNAME" exit
if [ $? -ne 0 ]; then
    echo "Unable to connect to $HOSTNAME. Please check the hostname and try again."
    exit 2
fi

# Run the command to list and delete .core files on the remote host via SSH
ssh "$HOSTNAME" << EOF
    if [ -d '$TARGET_DIR' ]; then
        echo 'Listing .core files in $TARGET_DIR with sizes:'
        # List the .core files with their sizes using ls -lh
        core_files=\$(find '$TARGET_DIR' -type f -name '*.core')
        if [ -n "\$core_files" ]; then
            echo "\$core_files" | while read -r file; do
                # Show file sizes using ls -lh
                ls -lh "\$file"
            done
            # Automatically delete the .core files
            echo 'Deleting .core files...'
            echo "\$core_files" | xargs rm -f
            echo 'Deletion complete.'
        else
            echo 'No .core files found in $TARGET_DIR.'
        fi
    else
        echo 'Directory $TARGET_DIR does not exist on $HOSTNAME.'
    fi
EOF
