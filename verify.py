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

    session.disconnect()
    
    pprint(content_vlan)
    pprint(content_trunk)
    
    create_file(dev['name'] + '_vlan', './BCMSN/solution/', content_vlan)
    create_file(dev['name'] + '_trunk', './BCMSN/solution/', content_trunk)



# def show_vlan_show_trunk_ssh(dev):
#     session = SSH(device_type='cisco_ios', ip=dev['host'], username=dev['username'], password=dev['password'])
#     connection = session.connect()
#     # connection.enable()
#     vlans = connection.send_command('show vlan', use_textfsm=True)
#     pprint(vlans)



def main():
    # username = input('username: ')
    # password = input('password: ')

    # Load data from inventory
    file_path = './BCMSN/inventory.json'
    data = restore_json(file_path)
    data = [dev for dev in data if dev['type'] == 'switch']
    # devices = []
    # for dev in data:
    #     if dev['type'] == 'switch':
    #         dev['username'] = username
    #         dev['password'] = password
    #         devices.append(dev)
    # pprint(devices)


    threads = []
    for dev in data:
        t = Thread(target=show_vlan_show_trunk, args= (dev,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()