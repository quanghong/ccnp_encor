import json, os, time, re, socket, traceback
from pprint import pprint, pformat
from threading import Thread
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, Environment

from feature import *
# from lib.ssh import SSH
from netmiko import ConnectHandler
from copy import deepcopy

load_dotenv()
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')
TEMPLATE_DIR = os.getenv('TEMPLATE_DIR')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
LOG_DIR = os.getenv('LOG_DIR')

devices_inv = restore_json(os.getenv('INVENTORY_DIR') + 'devices.json')
# pprint(devices_inv)


def configure_ibgp(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ibgp_peerings.j2')
    commands = jj_template.render(dev).splitlines()
    print('name={}, commands={}'.format(dev['name'], pformat(commands)))

    # Create a socket object
    source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the source IP and any available port (port 0 lets the OS pick the port)
    source_socket.bind((EVE_NG_IP_HOST_ONLY, 0))
    source_socket.connect((dev['ip'], 22))
    dev['sock'] = source_socket
    dev['verbose'] = True
    del dev['name']
    del dev['type']
    dev['session_log'] = '{}/{}.log'.format(LOG_DIR, dev['ip'])
    dev['session_log_file_mode'] = 'append'
    pprint(dev)

    # Connect
    connection = ConnectHandler(**dev)
    connection.enable()
    connection.send_config_set(commands, read_timeout=10)
    connection.save_config()

    # wait for 30s to convergence
    # Verify
    neighbors = connection.send_command('show ip bgp summary', use_textfsm=False)
    connection.disconnect()

    print('ip={}, neighbors={}'.format(dev['ip'], pformat(neighbors)))


def main():
    '''iBGP Peerings'''
    list_configure_order = ['R1', 'R4', 'SW1', 'SW2']
    list_configure = get_list_device_configure(deepcopy(devices_inv), list_configure_order)
    for dev in list_configure:
        try:
            configure_ibgp(dev)
        except Exception as exc:
            print(traceback.format_exc())



if __name__ == '__main__':
    main()