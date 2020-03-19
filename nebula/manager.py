import os
import time

import yaml
from nebula.netconsole import netconsole
from nebula.network import network
from nebula.pdu import pdu
from nebula.tftpboot import tftpboot
from nebula.uart import uart


class manager:
    """ Board Manager """

    def __init__(self, monitor="uart", configfilename=None):
        # Check if config info exists in yaml
        self.configfilename = configfilename
        if configfilename:
            stream = open(configfilename, "r")
            configs = yaml.safe_load(stream)
            stream.close()
        else:
            configs = None

        if "netconsole" in monitor.lower():
            monitor_uboot = netconsole(port=6666, logfilename="uboot.log")
            monitor_kernel = netconsole(port=6669, logfilename="kernel.log")
            self.monitor = [monitor_uboot, monitor_kernel]
        elif "uart" in monitor.lower():
            if "uart-config" not in configs:
                configfilename = None
            else:
                configfilename = self.configfilename
            u = uart(yamlfilename=configfilename)
            self.monitor = [u]

        if "network-config" not in configs:
            configfilename = None
        else:
            configfilename = self.configfilename
        self.net = network(yamlfilename=configfilename)

        if "pdu-config" not in configs:
            configfilename = None
        else:
            configfilename = self.configfilename
        self.power = pdu(yamlfilename=configfilename)

        self.boot_src = tftpboot()

    def get_status(self):
        pass

    def load_boot_bin(self):
        pass

    def board_reboot(self):
        # Try to reboot over SSH first
        try:
            self.net.reboot_board()
        except Exception as ex:
            # Try power cycling
            print("SSH reboot failed, power cycling", str(ex))
            self.power.power_cycle_board()
            time.sleep(40)
            try:
                self.net.check_board_booted()
            except Exception as ex:
                print("Still cannot get to board after power cycling")
                print("Exception", str(ex))
                try:
                    print("SSH reboot failed again after power cycling")
                    print("Forcing UART override on power cycle")
                    print("Power cycling")
                    self.power.power_cycle_board()
                    print("Spamming ENTER to get UART console")
                    for k in range(60):
                        self.monitor.write_data("\r\n")
                        time.sleep(0.1)

                    self.monitor.load_system_uart()
                    time.sleep(20)
                    self.net.check_board_booted()
                except Exception as ex:
                    raise Exception("Getting board back failed", str(ex))

    def run_test(self):
        # Move BOOT.BIN, kernel and devtree to target location
        # self.boot_src.update_boot_files()

        # Start loggers
        for mon in self.monitor:
            mon.start_log()
        # Power cycle board
        self.board_reboot()

        # Check IIO context and devices

        # Run tests

        # Stop and collect logs
        for mon in self.monitor:
            mon.stop_log()


if __name__ == "__main__":
    # import pathlib

    # p = pathlib.Path(__file__).parent.absolute()
    # p = os.path.split(p)
    # p = os.path.join(p[0], "resources", "nebula-zed-fmcomms2.yaml")

    # m = manager(configfilename=p)
    # m.run_test()
    pass
