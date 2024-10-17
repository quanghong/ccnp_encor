import json, os, time, re, socket, traceback
from pprint import pprint, pformat
from threading import Thread
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, Environment

from feature import *
# from lib.ssh import SSH
from netmiko import ConnectHandler

load_dotenv()
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')
TEMPLATE_DIR = os.getenv('TEMPLATE_DIR')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
LOG_DIR = os.getenv('LOG_DIR')

devices_inv = restore_json(os.getenv('INVENTORY_DIR') + 'devices.json')
# pprint(devices_inv)


def configure_ospf_multi_area(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ospf_multi_area.j2')
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
    # AFTER OSPF CONVERGENCE COMMEND SEND_CONFIG_SET
    # print('ip={}, change AREA, lost connection!!!'.format(dev['ip']))
    # connection.send_config_set(commands, read_timeout=10)

    # LOST CONNECTION AFTER SENDING COMMANDS, NEED SAVE_CONFIG AFTER OSPF CONVERGENCE AGAIN!
    connection.save_config()
    # Verify
    neighbors = connection.send_command('show ip ospf neighbor', use_textfsm=False)
    routes = connection.send_command('show ip route ospf', use_textfsm=False)
    connection.disconnect()

    print('ip={}, neighbors={}'.format(dev['ip'], pformat(neighbors)))
    print('ip={}, routes={}'.format(dev['ip'], pformat(routes)))

def configure_ospf_optimization(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ospf_optimization.j2')
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
    # # AFTER OSPF CONVERGENCE COMMEND SEND_CONFIG_SET
    # print('ip={}, change network type, lost connection!!!'.format(dev['ip']))
    # connection.send_config_set(commands, read_timeout=10)

    # LOST CONNECTION AFTER SENDING COMMANDS, NEED SAVE_CONFIG AFTER OSPF CONVERGENCE AGAIN!
    connection.save_config()
    # Verify
    neighbors = connection.send_command('show ip ospf neighbor', use_textfsm=False)
    routes = connection.send_command('show ip route ospf', use_textfsm=False)
    databases = connection.send_command('show ip ospf database', use_textfsm=False)
    connection.disconnect()

    print('ip={}, neighbors={}'.format(dev['ip'], pformat(neighbors)))
    print('ip={}, routes={}'.format(dev['ip'], pformat(routes)))
    print('ip={}, databases={}'.format(dev['ip'], pformat(databases)))

def configure_ospf_security(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ospf_security.j2')
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
    # # AFTER OSPF CONVERGENCE COMMEND SEND_CONFIG_SET
    # print('ip={}, change network type, lost connection!!!'.format(dev['ip']))
    # connection.send_config_set(commands, read_timeout=10)

    # LOST CONNECTION AFTER SENDING COMMANDS, NEED SAVE_CONFIG AFTER OSPF CONVERGENCE AGAIN!
    connection.save_config()
    # Verify
    neighbors = connection.send_command('show ip ospf neighbor', use_textfsm=False)
    passive_interfaces = connection.send_command('show ip protocols', use_textfsm=False)
    authen_interfaces = connection.send_command('show ip ospf interface', use_textfsm=False)
    connection.disconnect()

    print('ip={}, neighbors={}'.format(dev['ip'], pformat(neighbors)))
    print('ip={}, passive_interfaces={}'.format(dev['ip'], pformat(passive_interfaces)))
    print('ip={}, authen_interfaces={}'.format(dev['ip'], pformat(authen_interfaces)))

def configure_ospf_redundancy(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ospf_redundancy.j2')
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
    # Verify
    neighbors = connection.send_command('show ip ospf neighbor', use_textfsm=False)
    routes = connection.send_command('show ip route ospf', use_textfsm=False)
    connection.disconnect()

    print('ip={}, neighbors={}'.format(dev['ip'], pformat(neighbors)))
    print('ip={}, routes={}'.format(dev['ip'], pformat(routes)))

def configure_ospf_path_selection(dev):
    dev['username'] = USERNAME
    dev['password'] = PASSWORD

    jj_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    jj_template = jj_env.get_template('ospf_path_selection.j2')
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
    
    if dev['ip'] == '10.255.255.2': #R2
        # before selection
        connection.send_command('traceroute 10.100.8.8', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 0', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 1', use_textfsm=False)

        connection.send_config_set(commands, read_timeout=10)
        connection.save_config()

        # after selection
        connection.send_command('show ip ospf interface tun 0', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 1', use_textfsm=False)
        # wait for a while to relearn routes
        time.sleep(1)
        connection.send_command('traceroute 10.100.8.8', use_textfsm=False)
    
    else: #R5
        # before selection
        connection.send_command('traceroute 10.100.7.7', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 0', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 1', use_textfsm=False)

        connection.send_config_set(commands, read_timeout=10)
        connection.save_config()

        # after selection
        connection.send_command('show ip ospf interface tun 0', use_textfsm=False)
        connection.send_command('show ip ospf interface tun 1', use_textfsm=False)
        # wait for a while to relearn routes
        time.sleep(1)
        connection.send_command('traceroute 10.100.7.7', use_textfsm=False)
    
    connection.disconnect()

def main():
    '''OSPF Multi area'''
    # threads = []
    # for dev in devices_inv:
    #     try:
    #         configure_ospf_multi_area(dev)
    #     except Exception as exc:
    #         print(traceback.format_exc())
    # #     t = Thread(target=configure_ospf_multi_area, args= (dev,))
    # #     t.start()
    # #     threads.append(t)
    # # for t in threads:
    # #     t.join()

    '''OSPF Optimization'''
    # list_configure_order = ['R2', 'R5', 'R1', 'R4', 'SW1', 'SW4', 'SW2', 'SW3']
    # list_configure = get_list_device_configure(devices_inv, list_configure_order)
    # for dev in list_configure:
    #     try:
    #         configure_ospf_optimization(dev)
    #     except Exception as exc:
    #         print(traceback.format_exc())

    '''OSPF Security'''
    # for dev in list_configure:
    #     try:
    #         configure_ospf_security(dev)
    #     except Exception as exc:
    #         print(traceback.format_exc())

    '''OSPF Security'''
    # list_configure_order = ['SW1', 'SW2']
    # list_configure = get_list_device_configure(devices_inv, list_configure_order)
    # for dev in list_configure:
    #     try:
    #         configure_ospf_redundancy(dev)
    #     except Exception as exc:
    #         print(traceback.format_exc())

    '''OSPF Path Selection'''
    list_configure_order = ['R2', 'R5']
    list_configure = get_list_device_configure(devices_inv, list_configure_order)
    for dev in list_configure:
        try:
            configure_ospf_path_selection(dev)
        except Exception as exc:
            print(traceback.format_exc())

if __name__ == '__main__':
    main()