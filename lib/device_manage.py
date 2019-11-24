import os
import fileinput
import subprocess
import time
if __name__ != "__main__":
    from .RaspiWifi.libs.configuration_app import app
    from . import conn_test
    from . import display
import multiprocessing, signal
import socket

script_dir = os.path.dirname(os.path.realpath(__file__))

def setup():
    remove_confgs()
    copy_new_confgs()

def backup_confgs():
    run_command('sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.original')
    run_command('sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.original')
    run_command('sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.original')
    run_command('sudo cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.original')
    run_command('sudo cp /etc/systemd/system/homesense.service /etc/systemd/system/homesense.service.original')

def remove_confgs():
    run_command('sudo mv /etc/dhcpcd.conf /etc/dhcpcd.conf.original')
    run_command('sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.original')
    run_command('sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.original')
    run_command('sudo mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.original')
    run_command('sudo mv /etc/systemd/system/homesense.service /etc/systemd/system/homesense.service.original')

def copy_new_confgs():
    run_command('sudo cp %s/config_files/dhcpcd.conf /etc/dhcpcd.conf' % script_dir)
    run_command('sudo cp %s/config_files/dnsmasq.conf /etc/dnsmasq.conf' % script_dir)
    run_command('sudo cp %s/config_files/hostapd.conf /etc/hostapd/hostapd.conf' % script_dir)
    run_command('sudo cp %s/config_files/homesense.service /etc/systemd/system/homesense.service' % script_dir)
    run_command('sudo systemctl daemon-reload')
    run_command('sudo rm -rf /etc/raspiwifi')
    run_command('sudo mkdir /etc/raspiwifi')

def reset_to_host_mode():
    if not os.path.isfile('/etc/raspiwifi/host_mode'):
        display.screen.display_blocker("Wifi Host")
        display.screen.update_screen(["Starting WiFi Hotspot..."], "Wifi Host")
        print("Cleaning up config files")
        run_command('mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.orginal')
        run_command('touch /etc/raspiwifi/host_mode')

        print("Stopping services")
        run_command("systemctl stop dnsmasq")
        run_command("systemctl stop dhcpcd")
        run_command("systemctl stop wpa_supplicant")
        run_command("dhclient -r wlan0")

        print("Killing running processes")
        run_command("killall wpa_supplicant")
        run_command("killall hostapd")


        print("Bringing wlan0 down")
        run_command("ifconfig wlan0 down")
        time.sleep(1)
        print("Starting hostapd")

        run_command("hostapd -d /etc/hostapd/hostapd.conf -B")
        print("Starting dnsmasq and dhcpcd")
        run_command("systemctl start dnsmasq")
        run_command("systemctl start dhcpcd")

        display.screen.update_screen(["Connect to WiFi:", "HomeSense Wifi"], "Wifi Host")
        print("Running raspiwifi app")

        app_args = {"host": "0.0.0.0", "port":80}
        p = multiprocessing.Process(target=app.app.run, kwargs=app_args)
        p.start()

        while True:
            if os.path.isfile('/etc/wpa_supplicant/wpa_supplicant.conf.tmp') or os.path.isfile('/etc/wpa_supplicant/wpa_supplicant.conf'):
                time.sleep(4)
                p.terminate()
                break
        #app.app.run(host='0.0.0.0', port=80)
        display.screen.remove_blocker()
        reset_to_client_mode()
    else:
        print("AP mode already running")


def run_command(command):
    #result = subprocess.check_output(command.split(" "))
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
    result = str(result)
    return result

def reset_to_client_mode(retry=3):
    print("Removing host mode flag")
    run_command("rm /etc/raspiwifi/host_mode")

    print("Stopping dhcpcd and dnsmasq")
    run_command("systemctl stop dhcpcd")
    run_command("systemctl stop dnsmasq")

    print("Stopping hostapd")
    run_command("killall hostapd")

    print("Bringing wlan0 down and back up")
    run_command("ifconfig down wlan0")
    run_command("ifconfig up wlan0")
    time.sleep(1)

    print("Starting wpa_supplicant")
    if os.path.isfile('/etc/wpa_supplicant/wpa_supplicant.conf'):
        run_command("wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0 -B")
    elif os.path.isfile('/etc/wpa_supplicant/wpa_supplicant.conf.original'):
        print("Using original file")
        run_command("wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf.original -i wlan0 -B")

    print("Starting dhclient")
    run_command("dhclient wlan0")
    print("Testing network connection")
    if conn_test.test_network_connection():
        print("We're connected")
        return True
    else:
        print("uhhh trying again?")
        if retry > 0:
            retry = retry -1
            reset_to_client_mode(retry)
        else:
            return False

def reset_device():
    display.screen.display_blocker("Device Reset")
    display.screen.update_screen(["Resetting Device..."], "Device Reset")
    run_command("rm /home/pi/HomeSense/sensor.dat")
    setup()
    run_command("reboot")

if __name__ == "__main__":
    import argparse
    from lib.RaspiWifi.libs.configuration_app import app
    from lib import display
    from lib import conn_test

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action='store_true')
    parser.add_argument("--client", action='store_true')
    parser.add_argument("--device", action='store_true')

    args = parser.parse_args()
    if args.host and args.client:
        print("Wrong answer")
        exit()
    elif args.host:
        print("Running in AP Host Mode")
        reset_to_host_mode()
    elif args.client:
        print("Running in Client Mode")
        reset_to_client_mode()
    elif args.device:
        print("Reseting device")
        reset_device()
    else:
        print("No arguments.")
        exit()