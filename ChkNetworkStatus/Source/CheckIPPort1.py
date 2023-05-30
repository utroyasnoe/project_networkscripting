__author__ = "Dad"
__email__ = "yourname@studytafensw.edu.au"
__copyright__ = "Copyright Gelos Enterprise"
__license__ = "Proprietary"
__last_update_date__ = "00/00/0000"
__version__ = "1.0.1"
__status__ = "Development"

"""Describe the program here in few sentences"""

# Imports
"""Script requires user input in two separate strings, subnet and mask. If subnet is provided
in format X.X.X.X/YY, mask is auto calculated from user's input. List of ports to scan
is provided in ports.txt file from Parameters directory"""


# Functions


# Program

import ipaddress
import os
import socket
import subprocess
import datetime
#from pywin32 import win32evtlogutil !!!!!!Install pywin32 before uncommenting!!!!!!
#from pywin32 import win32event
#from pywin32 import win32evtlog


def validate_subnet_mask(subnet, mask):
    try:
        network = ipaddress.IPv4Network(f"{subnet}/{mask}", strict=False)
        return str(network.network_address) == subnet
    except ValueError:
        return False


def read_port_numbers(file_path):
    with open(file_path, "r") as file:
        port_numbers = file.read().splitlines()
    return port_numbers


def get_subnet():
    while True:
        user_data = input("Enter the IP subnet: ")
        if '/' in user_data:
            subnet = str(user_data.split('/')[0])
            mask = str(user_data.split('/')[1])
        else:
            subnet = user_data
            mask = input("Enter the subnet mask: ")
        if validate_subnet_mask(subnet, mask):
            return subnet, mask
        else:
            print("Invalid subnet and subnet mask combination. Please try again.")


def read_port_numbers():
    script_directory = os.path.dirname(__file__)
    with open(os.path.join(os.path.join(script_directory, "Parameters"), "ports.txt"), "r") as file:
        port_numbers = file.read().splitlines()
    return port_numbers


def get_ip_addresses(subnet, mask):
    network = ipaddress.ip_network(subnet + '/' + mask)
    print(network)
    ip_addresses = [str(ip) for ip in network.hosts()]
    ip_addresses = ip_addresses[10::2]
    return ip_addresses


def is_reachable(ip):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def scan_ports(ip_addresses, port_numbers):
    open_ports = []
    closed_ports = []
    unreachable_address = []
    for ip in ip_addresses:
        if is_reachable(ip) == False:
            print(f"IP address {ip} is not reachable. Skipping port check.")
            unreachable_address.append(ip)
        else:
            for port in port_numbers:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        result = sock.connect_ex((ip, int(port)))
                        if result == 0:
                            open_ports.append((ip, port))
                        else:
                            closed_ports.append((ip, port))
                except socket.error:
                    pass
    return open_ports, closed_ports, unreachable_address


def write_to_log(open_ports, closed_ports, unreachable_address):
    log_file = os.path.join(os.path.dirname(__file__), "ip_port_log.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as file:
        file.write("\n" + "="*10 + timestamp + "\n")
        file.write("Open ports:" + "\n")
        for ip, port in open_ports:
            file.write(f"{ip}:{port}\n")
        file.write("Closed ports:" + "\n")
        for ip, port in closed_ports:
            file.write(f"{ip}:{port}\n")
        file.write("Unreachable hosts:" + "\n")
        for ip in unreachable_address:
            file.write(ip + "\n")


#def write_event_log(ip, port):
    #event_id = 7777
    #event_type = win32evtlog.EVENTLOG_INFORMATION_TYPE
    #event_category = 0
    #strings = (f"Open port detected: {ip}:{port}",)
    #data = None
    #win32evtlogutil.ReportEvent("Application", event_id, event_category, event_type, strings, data)


subnet, mask = get_subnet()
print("Valid subnet and subnet mask combination provided:")
print("Subnet:", subnet)
print("Subnet Mask:", mask)

port_numbers = read_port_numbers()

print("Port numbers from file:")
for port in port_numbers:
    print(port)

ip_addresses = get_ip_addresses(subnet, mask)

print("IP addresses from subnet:")
for ip in ip_addresses:
    print(ip)

proceed = input("Do you want to proceed with scanning the open ports? (y/n): ")

if proceed.lower() == 'y':
    open_ports, closed_ports, unreachable_address = scan_ports(ip_addresses, port_numbers)
    print("Open ports:")
    for ip, port in open_ports:
        #write_event_log(ip, port)
        print(f"{ip}:{port}")
    print("Closed ports:")
    for ip, port in closed_ports:
        print(f"{ip}:{port}")
    print('Unreachable hosts:')
    for ip in unreachable_address:
        print(ip)
    write_to_log(open_ports, closed_ports, unreachable_address)

else:
    print("Scanning aborted.")
