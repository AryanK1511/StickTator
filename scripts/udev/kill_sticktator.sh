#!/usr/bin/bash
# Filename: /usr/local/bin/kill_sticktator.sh
# Logs: /tmp/udev.log
# Change udev rules using : sudo vim /etc/udev/rules.d/80-local.rules
# SUBSYSTEM=="block", ACTION=="remove", ENV{ID_VENDOR_ID}=="054c", ENV{ID_MODEL_ID}=="02a5", RUN+="/usr/local/bin/kill_sticktator.sh"

if [ -f "/tmp/sticktator.pid" ]; then
    MAIN_PID=$(cat /tmp/sticktator.pid)
    
    # First try graceful shutdown with SIGTERM
    kill -TERM $MAIN_PID 2>/dev/null
    pkill -TERM -P $MAIN_PID 2>/dev/null
    
    # Give the process time to cleanup and send disconnect message
    TIMEOUT=10
    COUNTER=0
    while [ $COUNTER -lt $TIMEOUT ] && ps -p $MAIN_PID >/dev/null 2>&1; do
        sleep 1
        COUNTER=$((COUNTER + 1))
    done
    
    # If process is still running after timeout, force kill
    if ps -p $MAIN_PID >/dev/null 2>&1; then
        echo "Process didn't terminate gracefully, force killing at $(date)" >> /tmp/udev.log
        pkill -KILL -P $MAIN_PID 2>/dev/null
        kill -KILL $MAIN_PID 2>/dev/null
    else
        echo "Process terminated gracefully at $(date)" >> /tmp/udev.log
    fi
    
    # Cleanup
    rm -f /tmp/sticktator.pid
    rm -rf /home/aryank1511/Desktop/StickTatorUSBClient
    echo "Cleanup completed at $(date)" >> /tmp/udev.log
else
    echo "No PID file found for StickTator at $(date)" >> /tmp/udev.log
fi
