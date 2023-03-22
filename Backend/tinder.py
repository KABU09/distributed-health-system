import threading
import socket
import time

from env import IP, UDP_NODE
from Helpers.parser import code_and_ip_to_bytes, bytes_to_code_and_ip
from random import randrange

my_ip = IP
other_ip = ''
sender = True
nodo = 'error'

udp_port = UDP_NODE

#encargado de saber si es pasivo, recibe codigo (0 o 1), mi ip y la ip del otro nodo
def isPassive(my_code, other_code, my_ip, other_ip):
    if my_code == 1: return False
    if other_code == 1: return True
    return my_ip < other_ip

#revisa si la ip del mensajes es difernte a la mia
def is_not_my_ip(my_ip, other_ip):
    return my_ip != other_ip

def process_recv_data(data):
    recv_headers = ['other_ip', 'other_port']
    ip_and_port = [data[1][0], data[1][1]]
    other_node = dict(zip(recv_headers,ip_and_port))
    recv_data = bytes_to_code_and_ip(data[0])
    return {**recv_data, **other_node}

def looking_both_passive(my_code, other_code):
    if my_code == 1 and other_code == 1: return False
    return True

def try_send(sock, code, other_ip):
    try:
        sock.sendto(code_and_ip_to_bytes(code, other_ip), ('<broadcast>', udp_port))
        return True
    except Exception as err:
        print('Exception', err)
        return False

def try_recv(sock):
    try:
        data = sock.recvfrom(1024)
        if not data: raise Exception ('No se obtuvo respuesta del nodo')
        return data
    except Exception as err:
        print('Exception', err)
        return False

def choose_node(sock, code):
    options = []
    t_end = time.time() + 2
    while time.time() < t_end:
        d = try_recv(sock)
        if not d:
            break
        data = process_recv_data(d)
        if data['code'] == 1 and looking_both_passive(code, data['code']):
            return data
        elif data['code'] == 0 and data['other_ip'] != my_ip:
            options.append(data)
    return options[randrange(len(options))] if len(options) else choose_node(sock, code)

def pair_active(sock):
    global sender
    global my_ip
    global other_ip
    global nodo
    while True:
        d = try_recv(sock)
        if not d:
            break
        data = process_recv_data(d)
        if data['code'] == 2 and data['ip'] == my_ip:
            print(data)
            sender = False
            s = try_send(sock, 3, data['other_ip'])
            if not s:
                break
            other_ip = data['other_ip']
            nodo = 'activo'
            break

def pair_passive(sock, chosen):
    global sender
    global nodo
    global my_ip
    global other_ip
    
    print(chosen)
    time.sleep(2)
    sender = False
    s = try_send(sock, 2, chosen['other_ip'])
    if s:
        other_ip = chosen['other_ip']
        while True:
            d = try_recv(sock)
            if not d:
                break
            data = process_recv_data(d)
            if data['code'] == 3:
                if data['ip'] == my_ip:
                    print(data)
                    nodo = 'pasivo'
                    break
                elif data['other_ip'] == other_ip:
                    break

def connect_partner(code = 0):
    global my_ip
    global other_ip
    global sender
    global nodo
    other_ip = ''
    sender = True
    nodo = 'error'
    t1 = threading.Thread(target=_listener, args=(code,)) #not sure if code is needed
    t2 = threading.Thread(target=_sender, args=(code,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

#encargado de enviar (0 o 1) recibe code  (0 o 1)
def _sender(code):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while sender:
            data = code_and_ip_to_bytes(code)
            sock.sendto(data, ('<broadcast>', udp_port))
            time.sleep(0.5)

#encargado de escuchar peticiones (0,1,2,3) recibe code (0 o 1)
def _listener(code):
    global sender
    global nodo
    global other_ip
    global my_ip

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('<broadcast>', udp_port))
        chosen = choose_node(sock, code)
        if(isPassive(code, chosen['code'], my_ip, chosen['other_ip'])):
            pair_passive(sock, chosen)
        else:
            pair_active(sock)

def find_partner(code=0):
    global nodo
    global my_ip
    global other_ip
    connect_partner(code)
    while nodo == 'error':
        connect_partner(code)
    return {'other_ip': other_ip, 'my_role': nodo}
    
