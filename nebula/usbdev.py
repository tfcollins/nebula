import os
import shutil
import subprocess
import psutil
import fabric
from fabric import Connection
import logging
import time

log = logging.getLogger(__name__)


class usbdev:
    def __init__(self):
        self.wait_time_seconds = 120

    def shell_out2(self, script):
        p = subprocess.Popen(
            script,
            shell=True,
            executable="/bin/bash",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (output, err) = p.communicate()
        return output.decode("utf-8")

    #
    def _check_disk_mounted(self, name="PlutoSDR", skip_exception=False):
        cmd = "sudo blkid -L " + name
        out = self.shell_out2(cmd)
        if len(out) == 0:
            return False, False
        cmd = "sudo mount -l | grep `sudo blkid -L " + name + "` | grep dev"
        out = self.shell_out2(cmd)
        out = out.split(" ")
        if len(out) > 1:
            partition = out[0]
            mountpoint = out[2]
        else:
            partition = False
            mountpoint = False
        if not skip_exception:
            if not os.path.exists(partition):
                raise Exception("partition not found: " + str(partition))
            if not os.path.isdir(mountpoint):
                raise Exception("mountpoint not found" + str(mountpoint))
        return mountpoint, partition

    def update_firmware(self, filename, device="PlutoSDR"):
        if not os.path.isfile(filename):
            raise Exception("File not found: " + filename)
        if "pluto" in device.lower():
            name = "PlutoSDR"
        else:
            name = "M2K"
        mount, partition = self._check_disk_mounted(name=name)
        log.info("Found mount: " + mount + " for partition: " + partition)
        # Send
        log.info("Copy firmware over")
        shutil.copy(filename, mount)
        # Eject
        log.info("Ejecting")
        self.shell_out2("eject " + partition)
        time.sleep(5)

    def wait_for_usb_mount(self, device):
        if "pluto" in device.lower():
            name = "PlutoSDR"
        else:
            name = "M2K"
        for k in range(self.wait_time_seconds):
            mount, partition = self._check_disk_mounted(name=name, skip_exception=True)
            time.sleep(1)
            log.info("Waiting for USB mass storage " + str(k))
            if mount and partition:
                log.info("Found USB mass storage: " + mount + " " + partition)
                return True
        return False


if __name__ == "__main__":
    u = usbdev()
    filename = "outs/plutosdr-fw-v0.32.zip"
    u.update_firmware(filename, device="pluto")
    time.sleep(3)
    u.wait_for_usb_mount(device="pluto")
