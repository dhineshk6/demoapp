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

# Run the deletion command on the remote host via SSH
ssh "$HOSTNAME" "
    if [ -d '$TARGET_DIR' ]; then
        echo 'Deleting .core files in $TARGET_DIR...'
        find '$TARGET_DIR' -type f -name '*.core' -exec rm -f {} \;
        echo 'Deletion complete.'
    else
        echo 'Directory $TARGET_DIR does not exist on $HOSTNAME.'
    fi
"
