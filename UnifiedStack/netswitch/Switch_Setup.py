#   Copyright 2014 Sudarshan Kumar
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# Switch_setup.py:
# Establishes an ssh session to the switch.
# Configures the switch.

import paramiko
import time

# TODO ip, username and password will be taken from config file later.
ip = '10.106.16.253'
username = 'sdu'
password = '1@#$sDu%^7'

class SwitchConfigurator:

    def establish_connection(self, ipaddress, username, password):
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()
        # Automatically add untrusted hosts (make sure okay for security policy
        # in your environment)
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # initiate SSH connection
        remote_conn_pre.connect(
            ipaddress,
            username=username,
            password=password)
        print "SSH connection established to %s" % ipaddress
        # Use invoke_shell to establish an 'interactive session'
        # remote_conn = remote_conn_pre.invoke_shell()
        print "Interactive SSH session established"
        return remote_conn_pre

    def configure_switch(self):
        # Calling the function to make the ssh connection
        remote_conn_client = self.establish_connection(
            ipaddress=ip,
            username=username,
            password=password)
        # Use invoke_shell to establish an 'interactive session'
        remote_conn = remote_conn_client.invoke_shell()
        output = remote_conn.recv(1000)
        print output
        # sending configuration commands to switch
        for line in open('sw_commands.txt'):
        #error check for ssh connection and send function
            try:
                remote_conn.send(line)
            except socket.error as e:
                print "Connection is not established : " + e.strerror
        # Adding a delay to let the commands work. Add at the end of all
        # commands
        time.sleep(2)
        output = remote_conn.recv(5000)
        print output

if __name__ == "__main__":
    sw_config = SwitchConfigurator()
    sw_config.configure_switch()
