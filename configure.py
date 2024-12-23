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


class NetworkLessons():
    def __init__(self):
        pass
    
    def configure_ip_address(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('ip_address_local_as_community.j2')
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

    def configure_bgp_weight_attribute(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_weight_attribute.j2')
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

    def configure_bgp_local_preference_attribute(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_local_preference_attribute.j2')
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

    def configure_bgp_as_path_prepending(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_as_path_prepending.j2')
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
    
    def configure_bgp_multi_exit_discriminator(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_MED_attribute.j2')
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

    def configure_bgp_no_advertise_community(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_no_advertise_community.j2')
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

    def configure_bgp_no_export_community(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_no_export_community.j2')
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

    def configure_bgp_local_as_community(self, dev):
        dev['username'] = USERNAME
        dev['password'] = PASSWORD

        jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        jj_template = jj_env.get_template('bgp_local_as_community.j2')
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
    # threads = []
    # for dev in devices_inv:
    #     t = Thread(target=enable_ssh, args= (dev,))
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()

    # CHANGE ENVIROMENT VARIABLE TO CONFIGURE BASIC PROTOCOLS

    '''INE ALL in one'''
    '''Basic EIGRP'''

    # '''Basic OSPF'''
    # threads = []
    # for dev in devices_inv:
    #     t = Thread(target=configure_basic_ospf, args= (dev,))
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()


    '''Network Lessons CCIE Routing & Switching'''
    '''Basic BGP'''
    classNL = NetworkLessons()
    threads = []
    for dev in devices_inv:
        
        '''Basic connectivity'''
        # t = Thread(target=classNL.configure_ip_address, args= (dev,))
        
        '''Path Attributes'''
        # t = Thread(target=classNL.configure_bgp_weight_attribute, args= (dev,))
        # t = Thread(target=classNL.configure_bgp_local_preference_attribute, args= (dev,))
        # t = Thread(target=classNL.configure_bgp_as_path_prepending, args= (dev,))
        # t = Thread(target=classNL.configure_bgp_multi_exit_discriminator, args= (dev,))

        '''Communities'''
        # t = Thread(target=classNL.configure_bgp_no_advertise_community, args= (dev,))
        # t = Thread(target=classNL.configure_bgp_no_export_community, args= (dev,))
        t = Thread(target=classNL.configure_bgp_local_as_community, args= (dev,))
        

        t.start()
        threads.append(t)
    for t in threads:
        t.join()



if __name__ == '__main__':
    main()