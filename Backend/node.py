import threading
import socket
import time

from env import DELIM, DELIM_PATIENTS, IP, UDP_NODE, UDP_INTERFACE, TCP_NODE, TCP_INTERFACE
from FileSystem import FileSystem
from Helpers.parser import ip_code_and_size_to_bytes, bytes_to_ip_code_and_size, data_to_dict, verify_integrity, json_to_protocol, info_to_copy, generate_headers
from tinder import find_partner

delim_fields = DELIM
delim_patients = DELIM_PATIENTS
udp_port_node = UDP_NODE
udp_port_interface =UDP_INTERFACE
tcp_port_interface = TCP_INTERFACE
tcp_port_node = TCP_NODE

sender = True
lock = threading.Lock()
node_info = {
    'my_ip': IP,
    'my_role': '',
    'other_ip': '',
    'other_tcp':None,
    'uptodate': True
}

fs = FileSystem()

def send_pair_udp(my_ip, other_ip, size):
    global sender
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        data = ip_code_and_size_to_bytes(0, my_ip, other_ip, size=size)
        while sender:
            sock.sendto(data, ('<broadcast>', udp_port_interface))
            time.sleep(2)

def send_passive_udp(my_ip, other_ip, size):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        data = ip_code_and_size_to_bytes(1, other_ip, size=size)
        sock.sendto(data, ('<broadcast>', udp_port_interface))

def try_recv(sock):
    try:
        data = sock.recv(1024)
        if not data: raise Exception ('No se obtuvo respuesta del nodo')
        return data
    except Exception as err:
        print('Recv', err)
        return False

def connect_and_listen(my_ip, port, timeout = False):
    conn = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout: sock.settimeout(7)
        sock.bind((my_ip, port))
        sock.listen(1)
        conn, addr = sock.accept()
        if timeout: conn.settimeout(7)
    except Exception as err:
        print('Listen', err)
        conn = None
    return conn

def connect_and_connect(other_ip, port, timeout = False):
    sock = None
    if not other_ip: return sock
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout: sock.settimeout(7)
        time.sleep(5)
        sock.connect((other_ip, port))  
    except Exception as err:
        print('Connect', err)
        sock = None
    return sock

def try_send(sock, data):
    try:
        sock.sendall(data.encode('utf-8'))
        return True
    except Exception as err:
        print('Send', err)
        return False

def process_information(data):
    global fs
    response = '1'
    if data['operation'] == 'r':
        response = fs.read_data(data['cedula'])
        print('Respuesta desde file system', response)
        if response['status'] == 0:
            return str(response['status']) + delim_fields + response['data']   
        else:
            return str(response['status'])

    elif data['operation'] == 'w':
        response = fs.write_data(data['cedula'], json_to_protocol(data))
        print('Respuesta desde file system', response)
        if response['status'] == 0:
            return str(response['status']) + delim_fields + str(response['blocks_available'])
        else:
            return str(response['status'])

    return response

def copy_all_info_to_node(sock):
    global fs
    info = fs.get_all_data()
    if not info: return 'empty'
    data = info_to_copy(info)
    copy = try_send(sock, data)
    if not copy: return 'error'
    data_recv =  try_recv(sock)
    if not data_recv: return 'error'
    data = data_to_dict(data_recv.decode(), ['code', 'size'], delim_fields)
    if data['code'] == '1': return 'error'
    return True

def copy_info_to_node(data, sock):
    send = try_send(sock, data)
    if not send: return 'error'
    data_recv =  try_recv(sock)
    if not data_recv: return 'error'
    data = data_to_dict(data_recv.decode(), ['code', 'size'], delim_fields)
    if data['code'] == '1': return 'error'
    return True

def process_request():
    global node_info
    global sender
    sock = connect_and_listen(node_info['my_ip'], tcp_port_interface)
    if sock:
        print('Conectado a la interfaz')
        sender = False
        if node_info['my_role'] == 'pasivo':
            with lock:
                node_info['my_role'] = 'activo'
            threading.Thread(target=try_partner_again,args=(1,), daemon=True).start()
        while True:
            data = try_recv(sock)
            if not data: break
            recv_data = data_to_dict(data.decode(), ['operation', 'cedula', 'name', 'info'], delim_fields)
            integrity = verify_integrity(recv_data)
            if not integrity:
                send = try_send(sock, '1')
                if not send: break
                continue
            response = process_information(recv_data)
            send = try_send(sock, response)
            if not send: break
            
            if node_info['other_tcp']:
                if recv_data['operation'] == 'w':
                    copy = copy_info_to_node(data.decode(), node_info['other_tcp'])
                    if copy == 'error': 
                        threading.Thread(target=try_partner_again,args=(1,), daemon=True).start()
                

def try_partner_again(code=0):
    global node_info
    with lock:
        node_info['other_ip'] = ''
        node_info['my_role'] = ''
        node_info['other_tcp'] = None
        node_info['uptodate'] =  False
    find_partner_and_save(code)
    if node_info['other_tcp']:
        send_passive_udp(node_info['my_ip'], node_info['other_ip'], fs.get_available_blocks())
        if code == 1 and not node_info['uptodate']:
            copy = copy_all_info_to_node(node_info['other_tcp'])
            node_info['uptodate'] =  True
            if copy == 'error': 
                threading.Thread(target=try_partner_again,args=(1,), daemon=True).start()


def find_partner_and_save(code = 0):
    global node_info
    res = find_partner(code)
    with lock:
        node_info['other_ip'] = res['other_ip']
        node_info['my_role'] = res['my_role']
    if node_info['my_role'] == 'activo':
        with lock:
            node_info['other_tcp'] = connect_and_listen(node_info['my_ip'], tcp_port_node, True)
        if not node_info['other_tcp']:
            try_partner_again(code)
    elif node_info['my_role'] == 'pasivo':
        with lock:
            node_info['other_tcp'] = connect_and_connect(node_info['other_ip'], tcp_port_node)
        if not node_info['other_tcp']:
            try_partner_again(code)

def process_backup(data):
    global fs
    op =  data_to_dict(data.decode(), ['operation'], delim_fields)
    if op['operation'] == 'w':
        data_recv = data_to_dict(data.decode(), ['operation', 'cedula', 'name', 'info'], delim_fields)
        response = fs.write_data(data_recv['cedula'], json_to_protocol(data_recv))
        if response['status'] == 1:
            return '1'
        return '0' + delim_fields + str(fs.get_available_blocks())
    elif op['operation'] == 'c':
        responses = []
        patients = data_to_dict(data.decode(), generate_headers(data.decode(), delim_patients), delim_patients)
        for k, v in patients.items():
            p = data_to_dict(v, ['cedula', 'name', 'info'], delim_fields)
            print('Patient 220', p)
            response = fs.write_data(p['cedula'], v)
            responses.append(response['status'])
        if 1 in responses:
            return '1'
        return '0' + delim_fields + str(fs.get_available_blocks())

def receive_backup():
    global node_info
    while True:
        recv = try_recv(node_info['other_tcp'])
        if recv:
            response = process_backup(recv)
            try_send(node_info['other_tcp'], response)
        else:
            threading.Thread(target=try_partner_again,args=(1,), daemon=True).start()
            break

def run():
    find_partner_and_save()
    print(f"Tengo la ip {node_info['my_ip']}, soy role {node_info['my_role']} y estoy conectado con {node_info['other_ip']}")
    if node_info['my_role'] == 'activo': threading.Thread(target=send_pair_udp,args=(node_info['my_ip'], node_info['other_ip'], fs.get_available_blocks()), daemon=True).start()
    if node_info['my_role'] == 'pasivo': threading.Thread(target=receive_backup, daemon=True).start()
    process_request()

run()
