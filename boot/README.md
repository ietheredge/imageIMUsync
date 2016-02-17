
#Housekeeping scripts to perform at start up of raspberrypi (running Raspbian)

#You may need to:
sudo chmod +x sendIPinfoemail.py

#and in order to run this at start up edit:
sudo nano /etc/rc.local
#add
 _IP=$(hostname -I) || true  
 if [ "$_IP" ]; then  
   printf "My IP address is %s\n" "$_IP"  
   python  [path to folder]/sendIPinfoemail.py    <<<--THIS LINE!!!  
 fi  
 exit 0   

#The data used is stored in two places within the root folder. less sensitive stuff in a config file (.ini) the more sensitive stuff in the netrc file (/.netrc)

#config file should be formatted like this:
[Settings]  
hostname: [your email host name, eg: smtp.gmail.com]  
toaddress: [emailaddress you want to send to]  
compname: [the name of your machine eg: RaspberryPi]  

#and... the netrc
machine [your email host] login [loginID] password [PWD]  
