#!/usr/bin/bash

# Filename: /usr/local/bin/setup.sh
# Logs: /tmp/udev.log
# Change udev rules using : sudo vim /etc/udev/rules.d/80-local.rules
# SUBSYSTEM=="block", ACTION=="add", ENV{ID_VENDOR_ID}=="054c", ENV{ID_MODEL_ID}=="02a5", RUN+="/usr/local/bin/setup.sh"

/usr/bin/date >> /tmp/udev.log
sleep 5

USER_PATH="/home/aryank1511"
USB_PATH="/media/aryank1511/STICKTATOR/StickTatorUSBClient"
DEST_PATH="$USER_PATH/Desktop/StickTatorUSBClient"
VENV_PATH="$DEST_PATH/venv"
ENV_FILE="$DEST_PATH/.env"
LOG_FILE="/tmp/udev.log"

if [ -d "$USB_PATH" ]; then
   cp -r "$USB_PATH" "$USER_PATH/Desktop/"
   chown -R aryank1511:aryank1511 "$DEST_PATH"
   su - aryank1511 -c "python3 -m venv $VENV_PATH"
   su - aryank1511 -c "source $VENV_PATH/bin/activate && pip3 install -r $DEST_PATH/requirements.txt"
   echo "SERVER_URL='2d19-216-249-49-30.ngrok-free.app'" > "$ENV_FILE"
   chown aryank1511:aryank1511 "$ENV_FILE"
   su - aryank1511 -c "($VENV_PATH/bin/python3 $DEST_PATH/main.py & echo \$! > /tmp/sticktator.pid)" >> $LOG_FILE 2>&1
   echo "Setup completed successfully" >> $LOG_FILE
else
   echo "StickTatorUSBClient folder not found on USB" >> $LOG_FILE
fi
