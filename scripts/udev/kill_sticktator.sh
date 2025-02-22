#!/usr/bin/bash

# Filename: /usr/local/bin/kill_sticktator.sh
# Logs: /tmp/udev.log
# Change udev rules using : sudo vim /etc/udev/rules.d/80-local.rules
# SUBSYSTEM=="block", ACTION=="remove", ENV{ID_VENDOR_ID}=="054c", ENV{ID_MODEL_ID}=="02a5", RUN+="/usr/local/bin/kill_sticktator.sh"

if [ -f "/tmp/sticktator.pid" ]; then
    MAIN_PID=$(cat /tmp/sticktator.pid)
    
    # Kill the entire process group
    pkill -TERM -P $MAIN_PID
    kill -TERM -$MAIN_PID
    
    # Force kill if still running after 5 seconds
    sleep 5
    if ps -p $MAIN_PID > /dev/null; then
        pkill -KILL -P $MAIN_PID
        kill -KILL -$MAIN_PID
    fi
    
    rm /tmp/sticktator.pid
    echo "Killed StickTator processes at $(date)" >> /tmp/udev.log
    
    rm -rf /home/aryank1511/Desktop/StickTatorUSBClient
    echo "Removed folder at $(date)" >> /tmp/udev.log
else
    echo "No PID file found for StickTator at $(date)" >> /tmp/udev.log
fi
