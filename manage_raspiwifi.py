import os
import fileinput
import subprocess
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


	os.system("systemctl start dnsmasq")
	os.system("systemctl start dhcpcd")
	os.system("hostapd -d /etc/hostapd/hostapd.conf")
	#os.system('reboot')


if __name__ == "__main__":
    reset_to_host_mode()