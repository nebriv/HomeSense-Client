import os
import fileinput
import subprocess
import time
from RaspiWifi.libs.configuration_app import app

def reset_to_host_mode():
    if not os.path.isfile('/etc/raspiwifi/host_mode'):
        os.system('rm -f /etc/wpa_supplicant/wpa_supplicant.conf')
        os.system('rm -f /home/pi/Projects/RaspiWifi/tmp/*')
        os.system('rm /etc/cron.raspiwifi/apclient_bootstrapper')
        os.system('cp /usr/lib/raspiwifi/reset_device/static_files/aphost_bootstrapper /etc/cron.raspiwifi/')
        os.system('chmod +x /etc/cron.raspiwifi/aphost_bootstrapper')
        os.system('mv /etc/dhcpcd.conf /etc/dhcpcd.conf.original')
        os.system('cp /usr/lib/raspiwifi/reset_device/static_files/dhcpcd.conf /etc/')
        os.system('mv /etc/dnsmasq.conf /etc/dnsmasq.conf.original')
        os.system('cp /usr/lib/raspiwifi/reset_device/static_files/dnsmasq.conf /etc/')
        os.system('cp /usr/lib/raspiwifi/reset_device/static_files/dhcpcd.conf /etc/')
        os.system('touch /etc/raspiwifi/host_mode')

        os.system("systemctl stop dnsmasq")
        os.system("systemctl stop dhcpcd")
        os.system("systemctl stop wpa_supplicant")
        os.system("killall wpa_supplicant")
        os.system("ifconfig wlan0 down")
        time.sleep(1)
        os.system("hostapd -d /etc/hostapd/hostapd.conf -B")
        os.system("systemctl start dnsmasq")
        os.system("systemctl start dhcpcd")
        os.system("touch /etc/raspiwifi/host_mode")
        app.app.run(host='0.0.0.0', port=80)


def run_command(command):
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
    result = result.read()
    return result

def test_network_connection():
    r = run_command("ping 8.8.8.8 -c 1")
    print(r)
    if "bytes from 8.8.8.8" in r:
        return True

def reset_to_client_mode():
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
    if test_network_connection():
        print("We're connected")
    else:
        print("uhhh trying again?")
        reset_to_client_mode()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action='store_true')
    parser.add_argument("--client", action='store_true')

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
    else:
        print("No arguments.")
        exit()