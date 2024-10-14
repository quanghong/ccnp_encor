import json, os, time, re, socket
from pprint import pprint, pformat
from threading import Thread

from netmiko import ConnectHandler
from feature import *
from jinja2 import FileSystemLoader, Environment
from dotenv import load_dotenv

load_dotenv()
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')
# print(EVE_NG_IP_HOST_ONLY)
PATH_CODE = input('PATH_CODE: ')
TEMPLATE_DIR = '{}/{}/{}'.format(os.path.curdir, PATH_CODE, input('TEMPLATE_DIR: '))
USERNAME = input('username: ')
PASSWORD = input('password: ')

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
    routes = connection.send_command('show ip route', use_textfsm=False)
    connection.disconnect()

    print('ip={}, routes={}'.format(dev['ip'], pformat(routes)))


def main():
    # Load data from inventory
    file_path = './{}/eigrp_devices.json'.format(PATH_CODE)
    data = restore_json(file_path)
    # pprint(data)

    threads = []
    for dev in data:
        t = Thread(target=configure_basic_eigrp, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()