from math import ceil
from env import DELIM

delim = DELIM

class Node_info:
    def __init__(self):
        self.data = []

    def add_new_pair(self, ip1, ip2, size):
        node = self.get_node_by_ip(ip1)
        if not node:
            self.data.append({'ip_activo': ip1, 'ip_pasivo': ip2, 'size': size, 'tcp':None, 'cedulas':[]})
        return self.get_node_by_ip(ip1)

    def get_node_by_ip(self, ip):
        return next((d for d in self.data if d['ip_activo'] == ip or d['ip_pasivo'] == ip), None)

    def get_node_by_id(self, id):
        return next((d for d in self.data for c in d['cedulas'] if c == id), None)
    
    def update_passive(self, ip_activo, ip_pasivo, size): #maybe size
        info = self.get_node_by_ip(ip_activo)
        if info:
            info['ip_pasivo'] = ip_pasivo
            #size missing

    def add_id(self, node, id): #maybe check if id is already saved 
        node['cedulas'].append(id)

    def get_available_node(self, data):
        block_size = self.blocks_needed(data)
        return next((d for d in self.data if d['size'] > block_size), None)
    
    def get_all_data(self):
        return self.data

    def blocks_needed(self, data):
        total_bytes = len(bytearray(data, 'utf-8'))
        return ceil(total_bytes / 16)

    def delete_node(self, node):
        for n in self.data:
            if node['ip_activo'] == n['ip_activo']:
                self.data.remove(n)

