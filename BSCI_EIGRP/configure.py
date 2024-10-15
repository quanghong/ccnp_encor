import json, os, time, re, socket, traceback
from pprint import pprint, pformat
from threading import Thread

from netmiko import ConnectHandler
from feature import *
from jinja2 import FileSystemLoader, Environment
from dotenv import load_dotenv

load_dotenv('.env_prod')
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')
TEMPLATE_DIR = os.getenv('TEMPLATE_DIR')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
eigrp_devices = restore_json(os.getenv('INVENTORY_DIR') + 'eigrp_devices.json')
# pprint(eigrp_devices)


def configure_basic_eigrp(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD
    dev['device_type'] = 'cisco_ios'

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('basic_eigrp.j2')
    commands = jj_template.render(dev).splitlines()
    print('ip={}, commands={}'.format(dev['ip'], pformat(commands)))

    # Create a socket object
    source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the source IP and any available port (port 0 lets the OS pick the port)
    source_socket.bind((EVE_NG_IP_HOST_ONLY, 0))
    source_socket.connect((dev['ip'], 22))
    dev['sock'] = source_socket
    dev['verbose'] = True
    del dev['name']
    del dev['type']
    pprint(dev)

    # Connect
    connection = ConnectHandler(**dev)
    connection.enable()
    output = connection.send_config_set(commands)
    connection.save_config()
    # Verify
    routes = connection.send_command('show ip route', use_textfsm=False)
    connection.disconnect()

    print('ip={}, output={}'.format(dev['ip'], pformat(output)))

def configure_eigrp_security(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD
    dev['device_type'] = 'cisco_ios'

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('eigrp_security.j2')
    commands = jj_template.render(dev).splitlines()
    print('ip={}, commands={}'.format(dev['ip'], pformat(commands)))

    # Create a socket object
    source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the source IP and any available port (port 0 lets the OS pick the port)
    source_socket.bind((EVE_NG_IP_HOST_ONLY, 0))
    source_socket.connect((dev['ip'], 22))
    dev['sock'] = source_socket
    dev['verbose'] = True
    del dev['name']
    del dev['type']
    dev['session_log'] = './log/{}.log'.format(dev['ip'])
    dev['session_log_file_mode'] = 'append'
    pprint(dev)

    # Connect
    connection = ConnectHandler(**dev)
    connection.enable()
    output = connection.send_config_set(commands)
    connection.save_config()
    connection.disconnect()

    print('ip={}, output={}'.format(dev['ip'], pformat(output)))

def verify_eigrp_routes(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD
    dev['device_type'] = 'cisco_ios'

    # Create a socket object
    source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the source IP and any available port (port 0 lets the OS pick the port)
    source_socket.bind((EVE_NG_IP_HOST_ONLY, 0))
    source_socket.connect((dev['ip'], 22))
    dev['sock'] = source_socket
    dev['verbose'] = True
    del dev['name']
    del dev['type']
    dev['session_log'] = './solution/{}.log'.format(dev['ip'])
    dev['session_log_file_mode'] = 'append'
    pprint(dev)

    # Connect
    connection = ConnectHandler(**dev)
    # Verify
    routes = connection.send_command('show ip route eigrp', use_textfsm=True)
    connection.disconnect()

    print('ip={}, routes={}'.format(dev['ip'], pformat(routes)))
    backup_json(routes, './solution/{}.json'.format(dev['ip']))


def main():
    '''Basic EIGRP'''
    # configure_basic_eigrp(eigrp_devices[1])

    # threads = []
    # for dev in eigrp_devices:
    #     t = Thread(target=configure_basic_eigrp, args= (dev,))
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()

    '''EIGRP Security'''
    for dev in eigrp_devices:
        try:
            configure_eigrp_security(dev)
        except Exception as exc:
            print(traceback.format_exc())
            pass
    
    for dev in eigrp_devices:
        verify_eigrp_routes(dev)



if __name__ == '__main__':
    main()