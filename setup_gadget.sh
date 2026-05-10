#!/bin/bash
# High-Efficiency BadUSB Setup for Pi Zero 2 W - Composite HID + RNDIS

# --- CLEANUP ---
if [ -d "/sys/kernel/config/usb_gadget/g1" ]; then
    echo "Resetting existing USB gadget..."
    echo "" | sudo tee /sys/kernel/config/usb_gadget/g1/UDC 2>/dev/null
    sudo rm /sys/kernel/config/usb_gadget/g1/configs/c.1/hid.usb0 2>/dev/null
    sudo rm /sys/kernel/config/usb_gadget/g1/configs/c.1/rndis.usb0 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/os_desc/c.1 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/configs/c.1 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/functions/hid.usb0 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/functions/rndis.usb0 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1/strings/0x409 2>/dev/null
    sudo rm -rf /sys/kernel/config/usb_gadget/g1 2>/dev/null
fi

# --- START SETUP ---
sudo modprobe libcomposite
cd /sys/kernel/config/usb_gadget/
sudo mkdir -p g1
cd g1

# IDs
echo 0x1d6b | sudo tee idVendor # Linux Foundation
echo 0x0104 | sudo tee idProduct # Multifunction Composite Gadget
echo 0x0100 | sudo tee bcdDevice
echo 0x0200 | sudo tee bcdUSB

# Windows-specific OS Descriptors for RNDIS
echo 0xEF | sudo tee bDeviceClass
echo 0x02 | sudo tee bDeviceSubClass
echo 0x01 | sudo tee bDeviceProtocol

sudo mkdir -p strings/0x409
echo "1234567890" | sudo tee strings/0x409/serialnumber
echo "Suryaganthan R" | sudo tee strings/0x409/manufacturer
echo "Astra Kernel Multi-Tool" | sudo tee strings/0x409/product

# Config setup
sudo mkdir -p configs/c.1/strings/0x409
echo "Config 1: HID + RNDIS" | sudo tee configs/c.1/strings/0x409/configuration
echo 250 | sudo tee configs/c.1/MaxPower

# --- HID FUNCTION ---
sudo mkdir -p functions/hid.usb0
echo 1 | sudo tee functions/hid.usb0/protocol
echo 1 | sudo tee functions/hid.usb0/subclass
echo 8 | sudo tee functions/hid.usb0/report_length
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 | sudo tee functions/hid.usb0/report_desc

# --- RNDIS FUNCTION ---
sudo mkdir -p functions/rndis.usb0
# Set specific Windows RNDIS compatible IDs
echo "RNDIS" | sudo tee functions/rndis.usb0/os_desc/interface.rndis/compatible_id
echo "516201" | sudo tee functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id

# OS Descriptors setup
sudo mkdir -p os_desc
echo 1 | sudo tee os_desc/use
echo 0xcd | sudo tee os_desc/bc_vendor_code
echo "MSFT100" | sudo tee os_desc/qw_sign
sudo ln -s configs/c.1 os_desc/c.1

# --- LINK FUNCTIONS ---
sudo ln -s functions/hid.usb0 configs/c.1/
sudo ln -s functions/rndis.usb0 configs/c.1/

# --- ENABLE GADGET ---
ls /sys/class/udc | sudo tee UDC
echo "Astra Kernel: Composite HID + RNDIS Created Successfully."
