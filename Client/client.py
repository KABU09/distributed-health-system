import socket
import ssl
import argparse

from Helpers.parser import dict_to_protocol, data_to_dict
from env import PORT, HOSTNAME_CLIENT,DELIM
delim = DELIM
hostname = HOSTNAME_CLIENT
port = PORT

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', required=True, help='Usuario')
    parser.add_argument('-p', required=True, help='Contrasena')
    parser.add_argument('-w', action='store_true', help='Escribir datos')
    parser.add_argument('-r', action='store_true', help='Leer datos')
    parser.add_argument('-c', required=False, help='Cedula')
    return vars(parser.parse_args())

def get_patient_data():
    cedula = str(input('Digite la cedula del paciente: '))
    name = str(input('Digite el nombre del paciente: '))
    info = str(input('Digite la informacion del paciente: '))
    return cedula + delim  + name  + delim + info

def process_data(data):
    headers = ['status', 'cedula','name', 'info']
    d = data_to_dict(data)
    switch = {
        '0': 'Ok',
        '1': 'Error'
    }
    status = switch.get(d['status'],'Invalid status')
    if d['status'] == '0':
        if 'cedula' in d and d['cedula'] != '':
            if all(h in d for h in headers):
                print('Nombre del Paciente:', d['name'])
                print('Cedula del Paciente:', d['cedula'])
                print('Informacion del Paciente:', d['info'])
            else:
                print('Error, respuesta incompleta')
        else:
            print(status)
    elif d['status'] == '1':
        print(status)


def connect(data):
    #context = ssl.create_default_context()
    context = ssl._create_unverified_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.sendall(data.encode('utf-8'))
            d = ssock.recv(1024).decode()
            process_data(d)

def main():
    data = get_args()
    if data['w']:
        data = dict_to_protocol(data)
        if not data:
            return process_data('1')
        data += delim + get_patient_data()
    elif data['r']:
        data = dict_to_protocol(data)
        if not data:
            return process_data('1')
    else:
        return process_data('1')
    connect(data)

main()

