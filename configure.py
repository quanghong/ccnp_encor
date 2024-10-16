import json, os, time, re, socket, traceback
from pprint import pprint, pformat
from threading import Thread
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, Environment

from feature import *
from lib.telnet import TELNET

load_dotenv()
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')
TEMPLATE_DIR = os.getenv('TEMPLATE_DIR')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

devices_inv = restore_json(os.getenv('INVENTORY_DIR') + 'inventory.json')
pprint(devices_inv)

def enable_ssh(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('enable_ssh.j2')
    commands = jj_template.render(dev).splitlines()
    print('name={}, commands={}'.format(dev['name'], pformat(commands)))

    # Connect
    session = TELNET(host=dev['host'], username=dev['username'], password=dev['password'], port=dev['port'])
    connection = session.connect()
    print(connection, pformat(dev))

    config = ""
    for cmd in commands:
        cmd += "\n"
        connection.write(cmd.encode('ascii'))
        time.sleep(0.5)
        config += connection.read_until(b"#", timeout=10).decode()

    connection.close()
    print('name={}, config={}'.format(dev['name'], pformat(config)))

def configure_basic_ospf(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('basic_ospf.j2')
    commands = jj_template.render(dev).splitlines()
    print('name={}, commands={}'.format(dev['name'], pformat(commands)))

    # Connect
    session = TELNET(host=dev['host'], username=dev['username'], password=dev['password'], port=dev['port'])
    connection = session.connect()
    print(connection, pformat(dev))

    config = ""
    connection.write(b"\n")
    time.sleep(2)
    connection.write(b"en\n")
    connection.write(b"conf t\n")
    for cmd in commands:
        cmd += "\n"
        connection.write(cmd.encode('ascii'))
        time.sleep(0.5)
        config += connection.read_until(b"#", timeout=10).decode()

    connection.write(b"end\n")
    connection.write(b"wr mem\n")
    connection.close()
    print('name={}, config={}'.format(dev['name'], pformat(config)))

def main():
    '''Enable SSH'''
    threads = []
    for dev in devices_inv:
        t = Thread(target=enable_ssh, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    '''Basic EIGRP'''

    '''Basic OSPF'''
    for dev in devices_inv:
        configure_basic_ospf(dev)

    '''Basic IS-IS'''
    
    '''Basic BGP'''


if __name__ == '__main__':
    main()