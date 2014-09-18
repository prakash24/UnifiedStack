# Copyright 2014 Prakash Kumar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/bin/python

# This File sets up the cobbler node.
from general_utils import shell_command, bcolors, shell_command_true
import inspect
import os
import sys

root_path = os.path.abspath(r"../..")
sys.path.append(root_path)


from UnifiedStack.config.Config_Parser import Config


def cobbler_setup(console):
    cobbler_interface = Config.get_cobbler_field('cobbler_interface')
    cobbler_ipaddress = Config.get_cobbler_field('cobbler_ipaddress')
    cobbler_netmask = Config.get_cobbler_field('cobbler_netmask')
    cobbler_server = Config.get_cobbler_field('cobbler_server')
    cobbler_next_server = Config.get_cobbler_field('cobbler_next_server')
    cobbler_subnet = Config.get_cobbler_field('cobbler_subnet')
    cobbler_option_router = Config.get_cobbler_field('cobbler_option_router')
    cobbler_DNS = Config.get_cobbler_field('cobbler_DNS')
    cobbler_hostname = Config.get_cobbler_field('cobbler_hostname')
    cobbler_web_username = Config.get_cobbler_field('cobbler_web_username')
    cobbler_web_password = Config.get_cobbler_field('cobbler_web_password')
    cobbler_netmask = Config.get_cobbler_field('cobbler_netmask')

    shell_command_true(
        "/usr/bin/yum -y install cobbler cobbler-web screen which wget curl pykickstart fence-agents dhcp bind-chroot xinetd")
    console.cprint_progress_bar("Writing in the necessary files",60)
    shell_command("hostname " + cobbler_hostname)
    # setup cobbler
    shell_command_true(
        "sed -i 's/^default_password_crypted.*/default_password_crypted: \"$1$7DMgQ9Ew$5d4IbaDMzVQ0FbqiiOH600\"/' /etc/cobbler/settings")
    shell_command_true(
        "sed -i 's/^manage_dhcp:.*/manage_dhcp: 1/' /etc/cobbler/settings")
    shell_command_true(
        "sed -i 's/^manage_dns:.*/manage_dns: 1/' /etc/cobbler/settings")
    shell_command_true(
        "sed -i 's/^server:.*/server: " +
        cobbler_server +
        "/' /etc/cobbler/settings")
    shell_command_true(
        "sed -i 's/^next_server:.*/next_server: " +
        cobbler_next_server +
        "/' /etc/cobbler/settings")
    shell_command_true(
        "sed -i 's/^pxe_just_once:.*/pxe_just_once: 1/' /etc/cobbler/settings")

    shell_command_true(
        "sed -i 's/^module = authn_denyall/module = authn_configfile/' /etc/cobbler/modules.conf")
    console.cprint_progress_bar("Installing pre-requistes for cobbler--",65)
    shell_command_true(
        "(echo -n " +
        cobbler_web_username +
        ":\"Cobbler\": && echo -n " +
        cobbler_web_username +
        ":\"Cobbler\":" +
        cobbler_web_password +
        " | md5sum | awk '{print $1}' ) >> /etc/cobbler/users.digest") 
    console.cprint_progress_bar("Files Written",65)
    # Setup DHCP template
    shell_command_true(
        "sed -i 's/^subnet 192.168.1.0/subnet " +
        cobbler_subnet +
        "/' /etc/cobbler/dhcp.template")
    shell_command_true(
        "sed -i 's/option routers.*/option routers " +
        cobbler_option_router +
        ";/' /etc/cobbler/dhcp.template")
    shell_command_true(
        "sed -i 's/domain-name-servers.*/domain-name-servers " +
        cobbler_DNS +
        ";/' /etc/cobbler/dhcp.template")
    shell_command_true(
        "sed -i 's/range dynamic-bootp.*/deny unknown-clients;/' /etc/cobbler/dhcp.template")
    shell_command_true(
        "sed -i 's/netmask 255.255.255.0/netmask " +
        cobbler_netmask +
        "/' /etc/cobbler/dhcp.template")

    # Add CIMC addresses to DHCP
    shell_command("touch /tmp/dhcpd.CIMC.conf")
    shell_command("cp /tmp/dhcpd.CIMC.conf /etc/dhcp/")

def enable_services(console):
    # Turn on cobbler
    console.cprint_progress_bar("Starting the Cobblerd service",70)
    shell_command("systemctl start cobblerd.service")
    shell_command("systemctl enable cobblerd.service")
    shell_command("systemctl status cobblerd.service")
    # Turn on apache
    console.cprint_progress_bar("Starting the Httpd Service",75)
    shell_command("systemctl start httpd.service")
    shell_command("systemctl enable httpd.service")
    shell_command("systemctl status httpd.service")
    console.cprint_progress_bar("Starting the Xinetd Service and dhcpd Service",75)
    # Restart xinetd
    shell_command("systemctl restart xinetd.service")
    shell_command("iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT")
    shell_command("iptables -A INPUT -p tcp -m tcp --dport 443 -j ACCEPT")
    # Open up Firewall
    shell_command_true("/sbin/iptables -F")
    shell_command_true("/sbin/iptables-save > /etc/sysconfig/iptables")
   
    # start dhcpd
    shell_command("systemctl start dhcpd.service")
    shell_command("systemctl enable dhcpd.service")
    shell_command("systemctl status dhcpd.service")

def sync(console):
    console.cprint_progress_bar("Cobbler Get-loaders and Sync",80)
    console.cprint_progress_bar("Installing pre-requistes for cobbler--",95)
    shell_command("cobbler get-loaders")
    import cobbler.api as capi
    handle = capi.BootAPI()
    handle.check()
    handle.sync()
   

def mount(console):
    """Here goes the code to wget the rhel image in the /root directory"""
    console.cprint_progress_bar("Mounting the RHEL iso to /root and doing cobbler import",95)
    rhel_image_url=Config.get_general_field("rhel-image-url")
    shell_command("wget " + rhel_image_url + "-P /root/rhel-server-7.0-x86_64-dvd.iso")
    shell_command(
        "mount -t iso9660 -o loop,ro  /root/rhel-server-7.0-x86_64-dvd.iso " +
        root_path +
        "/UnifiedStack/masternode/rhel_mount")
    shell_command("rm -rf /root/rhel-server-7.0-x86_64-dvd.iso")
    

def create_install_server(console):
    shell_command(
        "cobbler import --name=RHEL7 --arch=x86_64 --path=" +
        root_path +
        "/UnifiedStack/masternode/rhel_mount")
    console.cprint_progress_bar("Task Completed",100)
