sudo ntpd -gq
sudo /etc/init.d/ntp restart
sudo hwclock -wu
sudo hwclock -r; date
