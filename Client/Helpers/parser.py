from env import DELIM
delim = DELIM

def dict_to_protocol(data):
    
    if data['w'] and data['r']:
        return False
    elif data['w'] :
        data['w'] = 'w'
        del data['r']
        if 'c' in data:
            del data['c']
    elif data['r']:
        if not data['c']:
            return False
        data['r'] = 'r'
        del data['w']
    else:
        return False
    s = delim.join(map(str,data.values()))
    return s

def data_to_dict(data):
    headers = ['status', 'cedula','name', 'info']
    data_splitted = data.split(delim)
    d = dict(zip(headers,data_splitted))
    return d