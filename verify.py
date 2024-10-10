import json, os, time, re
from pprint import pprint, pformat
from threading import Thread

from lib.telnet import TELNET
from lib.ssh import SSH
from feature import *

def show_vlan_show_trunk(dev):
    session = TELNET(host=dev['host'], username=dev['username'], password=dev['password'], port=dev['port'])
    connection = session.connect()
    print(connection, pformat(dev))

    content_vlan = ""
    connection.write(b"en\n")
    connection.write(b"show vlan\n")
    while True:
        n, match, previous_text = connection.expect([b"--More--"], 2)
        # print(n, match, previous_text)
        content_vlan += previous_text.decode()
        if n in [0, 1]:
            connection.write(b" ")
        else:
            content_vlan = re.sub(r"\s--More--\s\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08", '', content_vlan)
            break

    content_trunk = ""
    connection.write(b"show int trunk\n")
    while True:
        n, match, previous_text = connection.expect([b"--More--"], 2)
        # print(n, match, previous_text)
        content_trunk += previous_text.decode()
        if n in [0, 1]:
            connection.write(b" ")
        else:
            content_trunk = re.sub(r"\s--More--\s\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08", '', content_trunk)
            break

    content_etherchannel = ""
    connection.write(b"show etherchannel detail\n")
    while True:
        n, match, previous_text = connection.expect([b"--More--"], 2)
        # print(n, match, previous_text)
        content_etherchannel += previous_text.decode()
        if n in [0, 1]:
            connection.write(b" ")
        else:
            content_etherchannel = re.sub(r"\s--More--\s\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08", '', content_etherchannel)
            break
    session.disconnect()
    
    pprint(content_vlan)
    pprint(content_trunk)
    pprint(content_etherchannel)
    
    create_file(dev['name'] + '_vlan', './BCMSN/solution/', content_vlan)
    create_file(dev['name'] + '_trunk', './BCMSN/solution/', content_trunk)
    create_file(dev['name'] + '_etherchannel', './BCMSN/solution/', content_etherchannel)


def show_ip_route(dev):
    session = SSH(device_type='cisco_ios', ip=dev['ip'], username=dev['username'], password=dev['password'],
                  source_address=dev['host'])
    connection = session.connect()
    connection.enable()
    routes = connection.send_command('show ip route', use_textfsm=True)
    session.disconnect()

    print('ip={}, routes={}'.format(dev['host'], pformat(routes)))
    backup_json(routes, './BCMSN/solution/{}_routes.json'.format(dev['name']))


def main():
    # Load data from inventory
    file_path = './BCMSN/inventory.json'
    hosts_all = restore_json(file_path)

    '''Switches'''
    data = [dev for dev in hosts_all if dev['type'] in ['switch', 'switch_L3']]
    threads = []
    for dev in data:
        t = Thread(target=show_vlan_show_trunk, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


    '''Switch Layer 3 & Routers'''
    username = input('username: ')
    password = input('password: ')
    devices = []
    for dev in hosts_all:
        if dev['type'] in ['router', 'switch_L3']:
            dev['username'] = username
            dev['password'] = password
            dev['port'] = 22
            devices.append(dev)
    # devices = devices[:1]
    pprint(devices)

    threads = []
    for dev in devices:
        t = Thread(target=show_ip_route, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == '__main__':
    main()