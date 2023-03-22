import socket
import ssl
import threading

from env import PORT, HOSTNAME_INTERFACE,DELIM, DELIM_PATIENTS, UDP_NODE, UDP_INTERFACE, TCP_INTERFACE, TCP_NODE
from Helpers.parser import data_to_dict, get_data_auth, get_data_to_save, verify_integrity, ip_code_and_size_to_bytes, bytes_to_ip_code_and_size, json_to_protocol, parse_body, to_sigma
from Helpers.database import find_patient, save_patient
from Helpers.auth import authenticate_user
from Helpers.express import get_type_and_file, serve_file, generate_search_result, handle_404, handle_400
from tinder_table import Node_info
from logs import log
from kiss_headers import parse_it
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

hostname = HOSTNAME_INTERFACE
port = PORT

delim_fields = DELIM
delim_patients = DELIM_PATIENTS
udp_port_node = UDP_NODE
udp_port_interface =UDP_INTERFACE
tcp_port_interface = TCP_INTERFACE
tcp_port_node = TCP_NODE


condition = threading.Condition()
lock = threading.Lock()

lock_table = threading.Lock()

n = Node_info()
l = log()

def process_recv_data(data):
    recv_headers = ['other_ip', 'other_port']
    ip_and_port = [data[1][0], data[1][1]]
    other_node = dict(zip(recv_headers,ip_and_port))
    recv_data = bytes_to_ip_code_and_size(data[0])
    return {**recv_data, **other_node}

def update_active(node):
    with lock_table:
        node['ip_activo'] =  node['ip_pasivo']
        node['ip_pasivo'] =  None

def connect_to_node(ip):
    sock = None
    if not ip: return sock
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(7)
        sock.connect((ip, tcp_port_interface))  
    except Exception as err:
        print('Connect', err)
        sock = None
    return sock

def connect_to_passive(node):
    update_active(node)
    sock = connect_to_node(node['ip_activo'])
    result = save_node_tcp(sock, node)
    if not result:
        return False
    return True 

def save_size(node, response, data):
    if response['status'] == '0' and data['operation'] == 'w':
        with lock_table:
            node['size'] = int(response['size'])

def process_client_response(node, data, response):
    log_respuesta(data, node['ip_activo'], response['status'])
    if response['status'] == '1': 
        return '1'
    elif response['status'] == '0':
        if data['operation'] == 'r':
            return '0' + delim_fields + json_to_protocol(get_data_to_save(response))
        elif data['operation'] == 'w':
            save_id(node, data['cedula'])
            return '0'

def log_solicitud(data, ip_nodo):
    if data['operation'] == 'w':
        l.log_solicitud_escritura(json_to_protocol(get_data_to_save(data)), ip_nodo)
    elif data['operation'] == 'r':
        l.log_solicitud_lectura(data['cedula'], ip_nodo)

def log_respuesta(data, ip_nodo, estado):
    if data['operation'] == 'w':
        l.log_respuesta_escritura(json_to_protocol(get_data_to_save(data)), ip_nodo, estado)
    elif data['operation'] == 'r':
        l.log_respuesta_lectura(data['cedula'], ip_nodo, estado)

def send_info_to_node(node, data):
    try:
        response_headers = ['status', 'cedula', 'name', 'info'] if data['operation'] == 'r' else ['status', 'size']
        log_solicitud(data, node['ip_activo'])
        info = ''
        if data['operation'] == 'w':
            info = data['operation'] + delim_fields + json_to_protocol(get_data_to_save(data))
        else:
            info = data['operation'] + delim_fields + data['cedula']
        node['tcp'].sendall(info.encode('utf-8'))
        response = node['tcp'].recv(1024)
        if not response: raise Exception ('No se obtuvo respuesta del nodo')
        response = data_to_dict(response.decode(), response_headers, delim_fields)
        save_size(node, response, data)
        return process_client_response(node, data, response)
    except Exception as err:
        print('Send', err)
        log_respuesta(data, node['ip_activo'], '1')
        passive_try = connect_to_passive(node)
        if not passive_try:
            with lock_table:
                n.delete_node(node)
            return '1'
        else:
            return send_info_to_node(node, data)

def save_node_tcp(sock, node):
    with lock_table:
        node['tcp'] =  sock
    if sock: return True
    return False

def connect_to_pair(node): 
    sock = connect_to_node(node['ip_activo'])
    result = save_node_tcp(sock, node)
    if not result: 
        update_active(node)
        sock = connect_to_node(node['ip_activo'])
        result_save = save_node_tcp(sock, node)
        if not result_save: update_active(node) 
    return result

def save_data(data):
    node = None
    if data['code'] == 0:
        with lock_table:
            node = n.add_new_pair(data['ip_activo'], data['ip_pasivo'], data['size'])
        connect = connect_to_pair(node)
        if not connect:
            with lock_table:
                n.delete_node(node)
        else:
            print(f"Pareja {node}")
    elif data['code'] == 1:
        with lock_table:
            n.update_passive(data['other_ip'], data['ip_pasivo'], data['size'])


def try_recv(sock):
    try:
        data = sock.recvfrom(1024)
        if not data: raise Exception ('No se obtuvo respuesta del nodo')
        return data
    except Exception as err:
        print('Exception', err)
        return False

def listen_UDP():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('<broadcast>', udp_port_interface))
        while True:
            d = try_recv(sock)
            if d:
                data = process_recv_data(d) 
                save_data(data)

def save_id(node, id):
     with lock_table:
        n.add_id(node, id)

def resourceIsAvailable():
    return not lock.locked()

def reader(request):
    with condition:
        node = n.get_node_by_id(request['cedula'])
        if not node:
            log_solicitud(request, 'Algun nodo')
            log_respuesta(request, f"Cedula no existe", '1')
            return '1'
        else:
            response = send_info_to_node(node, {'operation':request['operation'], 'cedula':request['cedula']})
            return response

def writer(request):
    with lock:
        with condition:
            with lock_table:
                node = n.get_node_by_id(request["cedula"])
            if node:
                with lock_table:
                    available = node['size'] > n.blocks_needed(request['info'])
                if available:
                    response = send_info_to_node(node, {'operation': request['operation'],**get_data_to_save(request)})
                    return response
                else:
                    log_solicitud(request, node['ip_activo'])
                    log_respuesta(request, node['ip_activo'], '1')
                    return '1'
            else:
                with lock_table:
                    node = n.get_available_node(json_to_protocol(get_data_to_save(request)))
                if node:
                    response = send_info_to_node(node, {'operation': request['operation'],**get_data_to_save(request)})
                    return response
                else:
                    log_solicitud(request, 'Algun nodo')
                    log_respuesta(request, 'No hay nodos disponibles', '1')
                    return '1'

def read_request(body, conn):
    req = to_sigma(body, 'r')
    data_res = send_to_backend(req)
    data_res = data_to_dict(data_res, ['status', 'cedula', 'name', 'info'], delim_fields)
    if data_res['status'] == '0':
        conn.send(b"HTTP/1.1 200 OK\n")
        conn.send(b"Content-Type: text/html\n\n")
        res = generate_search_result(data_res['name'], data_res['cedula'], data_res['info'])
        conn.send(res.encode('utf-8'))
    elif data_res['status'] == '1':
        handle_404(conn)
    elif data_res['status'] == '2':
        handle_400(conn)

def write_request(body, conn):
    req = to_sigma(body, 'w')
    data_res = send_to_backend(req)

    if data_res == '0':
        body = {'username':body['username'], 'password': body['password'], 'patientId':body['patientId']}
        read_request(body,conn)

    elif data_res == '1':
        handle_404(conn)
    elif data_res == '2':
        handle_400(conn)

def serve(conn, op:str, route:str, body:str, headers):
    print(body)
    if op == 'GET': 
        l.log_solicitud(op, route)
        return serve_file(conn, route)
    if op == 'POST':
        l.log_solicitud(op, route, headers['Content-Type'], headers['Content-Length'])
        if route == '/read':
            read_request(body, conn)
        elif route == '/add-patient':
            write_request(body, conn)
        else:
            handle_404(conn)
    else:
        handle_400(conn)
    
def server(conn, addr):
    p = HttpParser()
    data = conn.recv(1024)
    try:
        nparsed = p.execute(data, len(data))
        body = parse_body(p.recv_body().decode('utf-8'))
    
        op = p.get_method()
        route = p.get_path()
        print(op)
        print(route)

        serve(conn, op, route, body, p.get_headers())
    except Exception as err:
        print(err)
        handle_400(conn)
    conn.close()

def send_to_backend(recv):
    status = '0'

    request = data_to_dict(recv, ['user','password','operation','cedula','name','info'], delim_fields)

    integrity = verify_integrity(request)

    if not integrity:
        status = '2'
        return status

    is_authenticated = authenticate_user(get_data_auth(request))

    if not is_authenticated:
         status = '2'
         return status

    if request["operation"] == 'w': #write data
        response = writer(request)
        return response
    elif request["operation"] == 'r': #read data
         response = reader(request)
         return response
    else:
         status = '1'
         return status

def make_conection():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('./certificate.pem', './private.key')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((hostname, port))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                try:
                    conn, addr = ssock.accept()
                    threading.Thread(target=server, args=(conn, addr), daemon=True).start()
                except:
                    pass

def main():
    threading.Thread(target=listen_UDP, daemon=True).start()
    make_conection()

main()
