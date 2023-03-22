from env import DELIM, DELIM_PATIENTS

delim_fields = DELIM
delim_patients = DELIM_PATIENTS

def data_to_dict(data:str, headers, delim:str):
    data_splitted = data.split(delim)
    data_splitted[0] = data_splitted[0][2:] if delim == 'σ' else data_splitted[0]
    d = dict(zip(headers,data_splitted))
    d = {k: v.strip('\n') for k, v in d.items()}
    return d

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

def verify_integrity(data:dict):
    headers = ['operation','cedula','name','info']
    if not 'operation' in data:
        return False
    operation = data["operation"]

    if operation == 'w':
        if not all(h in data for h in headers):
            return False
    elif operation == 'r':
        if not all(h in data for h in headers[:2]):
            return False
    else:
        return False
    
    return True


def json_to_protocol(person):
    response = ''
    if person:
        response = person['cedula']+delim_fields + person['name'] + delim_fields + person['info']
    return response

def info_to_copy(data):
    info = 'c' + delim_fields
    for p in data:
        info +=  p + delim_patients
    
    return info[:len(info) - 1]
