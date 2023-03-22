from env import DELIM
from urllib.parse import parse_qs
delim = DELIM

headers = ['user','password','operation','cedula','name','info']

#extract data to dict
def data_to_dict(data:str, headers, delim:str):
    data_splitted = data.split(delim)
    data_splitted[0] = data_splitted[0][2:] if delim == 'σ' else data_splitted[0]
    d = dict(zip(headers,data_splitted))
    d = {k: v.strip('\n') for k, v in d.items()}
    return d


def verify_integrity(data:dict):
    if not 'operation' in data:
        return False
    operation = data["operation"]

    if(operation == 'w'):
        if not all(h in data for h in headers):
            return False
    elif operation == 'r':
        if not all(h in data for h in headers[:4]):
            return False
    else:
        return False
    
    return True

#extract auth data
def get_data_auth(data):
    dataFiltered = dict()
    dataFiltered["user"] = data["user"]
    dataFiltered["password"] = data["password"]
    dataFiltered["operation"] = data["operation"]
    return dataFiltered

#data from patient
def get_data_to_save(data:dict):
    dataFiltered = dict()
    dataFiltered["cedula"] = data["cedula"]
    dataFiltered["name"] = data["name"]
    dataFiltered["info"] = data["info"]
    return dataFiltered

#parse json data to protocol
def json_to_protocol(person):
    response = ''
    if person:
        response = person['cedula'] + delim + person['name'] + delim + person['info']
    return response

def generate_headers(data:str, delim:str):
    return [(f"user{i}") for i in range(data.count(delim) + 1)]

def ip_code_and_size_to_bytes(code:int, ip1:str, ip2:str = '', *, size:int):
    ip1 = [int(x) for x in ip1.split('.')]
    if ip2 : ip2 = [int(x) for x in ip2.split('.')]
    data:bytes = []
    data = ip1 + (ip2 if ip2 else [])
    data.insert(0, code)
    data.append(size)
    return bytes(data)

def bytes_to_ip_code_and_size(data:bytes):
    two_ip = len(data) == 10
    headers = ['code','ip_pasivo', 'ip_activo','size']
    headers = headers if two_ip else headers[0:2] + headers[3:]

    ip1 = []
    ip2 = []

    ip1 = [str(x) for x in data[1:5]]
    ip1 =  '.'.join(ip1)

    if two_ip: 
        ip2 = [str(x) for x in data[5:9]] 
        ip2 =  '.'.join(ip2)
    
    size = data[9] if two_ip else data[5]
    info = []
    info.append(data[0])
    if two_ip: info.append(ip2)
    info.append(ip1)
    info.append(size)

    return dict(zip(headers,info))

def code_and_ip_to_bytes(code:int, ip:str = ''):
    data = []
    data.append(code)
    ip1 = []
    if ip:
        ip1 = [int(x) for x in ip.split('.')]
    data+= ip1

    return bytes(data)

def bytes_to_code_and_ip(data:bytes):
    code_and_ip = len(data) == 5
    headers = ['code', 'ip']
    headers = headers if code_and_ip else headers[:1]
    info = []
    info.append(data[0])
    if code_and_ip:
        ip = [str(x) for x in data[1:5]] 
        ip =  '.'.join(ip)
        info.append(ip)
    
    return dict(zip(headers,info))

def parse_body(body:str):
    return {k: v[0] for k, v in parse_qs(body).items()}

def to_sigma(body, op):
    if op == 'w':
        return body['username'] + delim + body['password'] + delim + op + delim + body['patientId'] + delim + body['patientName'] + delim + body['patient_other_info']
    elif op =='r':
        return body['username'] + delim + body['password'] + delim + op + delim + body['patientId']
