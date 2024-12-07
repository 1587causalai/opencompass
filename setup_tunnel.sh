#!/bin/bash

# Check if port 7890 is in use
if lsof -i:7890 > /dev/null 2>&1; then
    echo "Port 7890 is in use (probably by Cursor), using port 7891 instead"
    PORT=7891
else
    PORT=7890
fi

# Create SSH tunnel for SOCKS proxy without login
ssh -N -p 44773 -D $PORT root@ssh.intern-ai.org.cn -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

# The script will keep running as long as the SSH tunnel is needed
# To stop, press Ctrl+C 