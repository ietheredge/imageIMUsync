import subprocess
import smtplib
from email.mime.text import MIMEText
import datetime
import netrc
import ConfigParser

##load in configuration (host, address, secrets)
Config = ConfigParser.ConfigParser()
Config.read("sendIPinfoemail.ini")

HOST = Config.get('Settings', 'hostname')
to = Config.get('Settings', 'toaddress')
secrets = netrc.netrc()
username, account, password = secrets.authenticators(HOST)

##connect to email server
smtpserver = smtplib.SMTP(HOST, 587)
smtpserver.ehlo()  
smtpserver.starttls()  
smtpserver.ehlo()
smtpserver.login(username, password)  

##get info
today = datetime.datetime.today()  

arg='ip route list'  
p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
data = p.communicate()  

##compose email and send
msg = MIMEText(data[0]) 
msg['Subject'] = 'IP infor For pi2c  on %s' % today.strftime('%b %d %Y %T')
msg['From'] = username
msg['To'] = to

smtpserver.sendmail(username, [to], msg.as_string())

##disconnect from server
smtpserver.quit()
