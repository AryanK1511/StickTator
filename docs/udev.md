# Understanding UDEV Commands

Here's a comprehensive breakdown of important UDEV commands and their purposes:

## Device Monitoring and Information

### `sudo udevadm monitor --property`

- Real-time monitoring of device events on your system
- Shows detailed properties of devices as they're added/removed
- Useful for debugging UDEV rules and device connections
- Output includes vendor IDs, product IDs, and other device attributes

### `lsusb`

- Lists all USB devices currently connected to your system
- Output format: `Bus XXX Device XXX: ID XXXX:XXXX Manufacturer Device_Name`
- Example output: `Bus 001 Device 006: ID 054c:02a5 Sony Corp. MicroVault Flash Drive`

### `lsblk`

- Lists all block devices (storage devices) in a tree format
- Shows disk partitions, mount points, and sizes
- Useful for identifying where USB drives are mounted
- Example: `/dev/sda`, `/dev/sdb`, etc.

## UDEV Rules Location and Management

### `/etc/udev/rules.d/80-local.rules`

- Directory for custom UDEV rules
- `80-` prefix determines rule priority (higher numbers load later)
- Rules in this file override default system rules
- Common format:

  ```bash
  SUBSYSTEM=="block", ACTION=="add", ENV{ID_VENDOR_ID}=="054c", ENV{ID_MODEL_ID}=="02a5", RUN+="/path/to/script.sh"
  ```

## Rule Components Explained

```bash
SUBSYSTEM=="block"        # Matches block devices (storage)
ACTION=="add"            # Triggers on device connection
ACTION=="remove"         # Triggers on device removal
ENV{ID_VENDOR_ID}       # Vendor ID of the device
ENV{ID_MODEL_ID}        # Product ID of the device
RUN+=""                 # Script to execute when rule matches
```

## Testing and Debugging Rules

1. After adding or modifying rules, reload them:

   ```bash
   sudo udevadm control --reload-rules
   ```

2. Monitor rule triggers:

   ```bash
   sudo udevadm monitor --property
   ```

3. Check system logs for script execution:

   ```bash
   tail -f /tmp/udev.log
   ```

## Example Rule for Sony USB Drive

```bash
# /etc/udev/rules.d/80-local.rules
SUBSYSTEM=="block", ACTION=="add", ENV{ID_VENDOR_ID}=="054c", ENV{ID_MODEL_ID}=="02a5", RUN+="/usr/local/bin/setup.sh"
```
