#!/bin/bash

# Enable debugging
set -x

# Check if the correct number of arguments is provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <ssh_host> <ssh_port> <ssh_username> <ssh_password>"
    exit 1
fi

# Assign arguments to variables
SSH_HOST=$1
SSH_PORT=$2
SSH_USERNAME=$3
SSH_PASSWORD=$4

# Define the main directory name
MAIN_DIR="SSH-Tunnel-VPN-Server-main"

# Define the paths to the files
LOCAL_ZIP_FILE="$HOME/$MAIN_DIR.zip"
LOCAL_DB_FILE="./db.sqlite3"
REMOTE_DIR="~"

# Install sshpass if not installed
if ! command -v sshpass &> /dev/null; then
    echo "sshpass is required but it's not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y sshpass
fi

# Ensure SSH key is generated
if [ ! -f "$HOME/.ssh/id_rsa.pub" ]; then
    ssh-keygen -t rsa -b 2048 -f "$HOME/.ssh/id_rsa" -N ""
fi

# Copy SSH key to the remote server
sshpass -p "$SSH_PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USERNAME@$SSH_HOST"

# Install unzip on the remote server if not installed
ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USERNAME@$SSH_HOST" "if ! command -v unzip &> /dev/null; then sudo apt-get update && sudo apt-get install -y unzip; fi"

# Copy the zip file to the remote server
scp -o StrictHostKeyChecking=no -P "$SSH_PORT" "~/$LOCAL_ZIP_FILE" "$SSH_USERNAME@$SSH_HOST:$REMOTE_DIR"

# Unzip the file on the remote server with overwrite option
ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USERNAME@$SSH_HOST" "unzip -o ~/$MAIN_DIR.zip -d ~"

# Copy the db.sqlite3 file to the remote server
scp -o StrictHostKeyChecking=no -P "$SSH_PORT" "$LOCAL_DB_FILE" "$SSH_USERNAME@$SSH_HOST:~/$MAIN_DIR/db.sqlite3"

# Run the install.sh script in the unzipped directory on the remote server
ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USERNAME@$SSH_HOST" "cd ~/$MAIN_DIR && bash install.sh"

echo "Operations completed successfully."
