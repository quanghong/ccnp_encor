import json, os, time, re
from pprint import pprint, pformat
from lib.telnet import TELNET
from threading import Thread

def backup_json(data, file_path):                                                  
    with open(file_path, "w") as ObjFile:
        ObjFile.write(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True))
        ObjFile.close()

def restore_json(file_path):
    data = {}
    if os.path.isfile(file_path):
        with open(file_path, 'r') as ObjFile:
            dataform = ObjFile.read()
            if dataform:
                data = json.loads(dataform)
            ObjFile.close()
    return data

def create_file(nameFile, pathFile, config):
    x_file = pathFile + nameFile + '.txt'
    fl = open(x_file, 'w')
    fl.write(config)
    fl.close()

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

    create_file(dev['name'] + '_init', './BCMSN/backup/', config)


def main():
    # Load data from inventory
    file_path = './BCMSN/inventory.json'
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