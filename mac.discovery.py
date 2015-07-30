__author__ = 'sambyers'
import urllib2
import paramiko
import getpass
from time import sleep
import sys
import re

def main():

    def disable_paging(remote_conn):
        '''Dsiable paging on a Cisco device'''

        remote_conn.send("terminal length 0\n")
        sleep(1)

        # Assign the output from the router
        output = remote_conn.recv(1000)

        return output


    url = "http://api.macvendors.com/"


    # Set some Paramiko parameters
    remote_conn_pre=paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    switch_ip = raw_input('Switch IP: ')
    switch_username = raw_input('Username: ')
    switch_password = getpass.getpass()

    re_mac = re.compile('([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})')
    re_port = re.compile('((Gi|Fa)([0-9]\/[0-9]\/[0-9][0-9])|(Gi|Fa)([0-9]\/[0-9]\/[0-9])|(Gi|Fa)([0-9]\/[0-9][0-9])|(Gi|Fa)([0-9]\/[0-9]))')


    if switch_ip and switch_username:

        remote_conn_pre.connect(switch_ip, username=switch_username, password=switch_password,look_for_keys=False,allow_agent=False)
        remote_conn = remote_conn_pre.invoke_shell()
        output = remote_conn.recv(5000)
        paging_output = disable_paging(remote_conn)
        remote_conn.send("show mac add dyn\n")
        sleep(1)
        show_mac = remote_conn.recv(5000)

        show_mac = show_mac.split('\n')

        for line in show_mac:
            mac = re.findall(re_mac,line)
            port = re.findall(re_port,line)
            if mac:
                mac_string = mac[0]
            if port:
                port_tuple = port[0]
                port_string = port_tuple[0]
            try:
                manufacturer = urllib2.urlopen(url + mac_string).read()
            except:
                manufacturer = 'Did not find a manufacturer for this MAC.'

            if mac and manufacturer:
                #print 'MAC: ' + mac_string + '    Port: ' + port_string + '    Manufacturer: ' + manufacturer
                print 'MAC: ' + mac_string
                print 'Port: ' + port_string
                print 'Manufacturer: ' + manufacturer
                print "\n"
    else:
        print 'Not enough information entered.'
        sys.exit()

if __name__ == '__main__':
    main()
