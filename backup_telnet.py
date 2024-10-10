import json, os, time, re
from pprint import pprint, pformat
from threading import Thread

from lib.telnet import TELNET
from feature import *

path_code = input('path_code: ')

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

    # create_file(dev['name'] + '_init', './{}/backup/.format(path_code)', config)
    create_file(dev['name'] + '_final', './{}/backup/'.format(path_code), config)


def main():
    # Load data from inventory
    file_path = './{}/inventory.json'.format(path_code)
    data = restore_json(file_path)
    # pprint(data)

    threads = []
    for dev in data:
        t = Thread(target=backup, args= (dev,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()