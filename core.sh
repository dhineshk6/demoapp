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
        echo 'Listing .core files in $TARGET_DIR:'
        # List the .core files in the directory
        core_files=\$(find '$TARGET_DIR' -type f -name '*.core')
        if [ -n "\$core_files" ]; then
            echo "\$core_files"
            # Ask for user confirmation before deleting
            echo -n "Do you want to delete these files? (y/n): "
            read confirm
            if [ "\$confirm" == "y" ] || [ "\$confirm" == "Y" ]; then
                echo 'Deleting .core files...'
                # Delete the .core files
                echo "\$core_files" | xargs rm -f
                echo 'Deletion complete.'
            else
                echo 'Deletion cancelled.'
            fi
        else
            echo 'No .core files found in $TARGET_DIR.'
        fi
    else
        echo 'Directory $TARGET_DIR does not exist on $HOSTNAME.'
    fi
EOF
