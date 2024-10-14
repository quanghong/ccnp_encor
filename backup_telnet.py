import json, os, time, re
from pprint import pprint, pformat
from threading import Thread

from lib.telnet import TELNET
from feature import *
from jinja2 import FileSystemLoader, Environment

PATH_CODE = input('PATH_CODE: ')
TEMPLATE_DIR = '{}/{}/{}'.format(os.path.curdir, PATH_CODE, input('TEMPLATE_DIR: '))
USERNAME = input('username: ')
PASSWORD = input('password: ')

def backup(dev):
    session = TELNET(host=dev['host'], username=dev['username'], password=dev['password'], port=dev['port'])
    connection = session.connect()
    print(connection, pformat(dev))

    config = ""
    
    connection.write(b"\n")
    time.sleep(2)
    connection.write(b"en\n")
    connection.write(b"show run\n")
    while True:
        n, match, previous_text = connection.expect([b"\r\n\s--More--\s", b"\r\nend", b"end\r\n\r\n"], 10)
        config += previous_text.decode()
        # print(repr(config))
        if n == 0:
            connection.write(b" ")
            # print(repr(config))
        else:
            # elif n in range(1, 3):
            # print(match)
            config = re.sub(r"\x1b]0;\S+\x07", '', config)
            # config = re.sub(r"\s--More--\s\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08", '', config)
            config = re.sub(r"\s--More--\s\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08", '', config)
            break
    # print(config)
    session.disconnect()

    create_file(dev['name'] + '_init', './{}/backup/'.format(PATH_CODE), config)
    # create_file(dev['name'] + '_final', './{}/backup/'.format(PATH_CODE), config)

def enable_ssh(dev):
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('enable_ssh.j2')
    commands = jj_template.render(data)
    # pprint(commands.splitlines())

    session = TELNET(host=dev['host'], username=dev['username'], password=dev['password'], port=dev['port'])
    connection = session.connect()
    print(connection, pformat(dev))

    for cmd in commands.splitlines():
        cmd += "\n"
        connection.write(cmd.encode('ascii'))
        time.sleep(0.5)

    session.disconnect()


def main():
    # Load data from inventory
    file_path = './{}/inventory.json'.format(PATH_CODE)
    data = restore_json(file_path)
    pprint(data)

    '''Enable SSH'''
    threads = []
    for dev in data:
        t = Thread(target=enable_ssh, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    '''Backup configure'''
    threads = []
    for dev in data:
        t = Thread(target=backup, args= (dev,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    # We can enable and backup config in one time connection.
    # OR backup config with ssh by ansible library.

if __name__ == '__main__':
    main()