"""
* DISK STORAGE
* This class simulates the storage in the computer
* Allows to write and read blocks of data
"""
from Helpers.BlockHelper import copy_block
from Helpers.FileHelper import decode_headers

class Storage:
    
    def __init__(self):
        self.block_size = 16
        self.amount_of_blocks = 32
        self.storage = []

        for row in range(0, self.amount_of_blocks):
            block = bytearray(self.block_size)
            self.storage.append(block)
        #superblock
        self.super_block_attr_size = 4
        
        superblock = self.generate_super_block(self.amount_of_blocks)
        self.write_block(0,0, superblock)

    def update_super_block(self, available_blocks)->None:
        superblock = self.generate_super_block(available_blocks)
        self.write_block(0,0,superblock)


    def generate_super_block(self, available_blocks:int)->bytearray:

        total_blocks_in_bytes = self.amount_of_blocks.to_bytes(self.super_block_attr_size, 'big')
        available_blocks_in_bytes = available_blocks.to_bytes(self.super_block_attr_size, 'big')
        block_size_in_bytes = self.block_size.to_bytes(self.super_block_attr_size, 'big')
    
        empty_block = int(0).to_bytes(self.super_block_attr_size, 'big')

        superblock = bytearray(self.block_size)
        superblock[:] = bytearray(total_blocks_in_bytes+available_blocks_in_bytes+block_size_in_bytes+empty_block)
        return superblock

    def get_super_block_info(self)->dict:
        '''
        RETURN
        dict {'total_blocks':total_blocks, 'available_blocks':available_blocks, 'block_size':block_size}
        '''
        superblock = self.read_block(0)

        start = 0
        last = self.super_block_attr_size
        total_blocks_in_bytes = superblock[start:last]

        start = self.super_block_attr_size
        last = self.super_block_attr_size*2
        available_blocks_in_bytes = superblock[start:last]

        start = self.super_block_attr_size*2
        last = self.super_block_attr_size*3
        block_size_in_bytes = superblock[start: last]

        total_blocks = int.from_bytes(total_blocks_in_bytes, byteorder='big')
        available_blocks = int.from_bytes(available_blocks_in_bytes, byteorder='big')
        block_size = int.from_bytes(block_size_in_bytes, byteorder='big')

        return {'total_blocks':total_blocks, 'available_blocks':available_blocks, 'block_size':block_size}

    def print_storage(self):
        print('\n')
        for index in range(self.amount_of_blocks):
            print("index: ",index,' size:',len(self.storage[index]), "block: ",self.storage[index])
    
    def read_blocks(self, start:int, last:int):
        return self.storage[start:last]

    def read_block(self, index:int):
        return self.storage[index]
    
    def validate_data_to_write(self, block_index:int, start:int, data:bytearray):

        # try:
        #     decoded_data = data.decode('utf-8').strip()
        # except:
        #     raise Exception('data must be a bytearray-like object')

        if len(data) > self.block_size:
            raise Exception('data size must be less or equal to ',self.block_size)
        
        if start + len(data) > self.block_size:
            raise Exception('data is too log')
        
        if not start >= 0:
            raise Exception('start argument must be positive. Start=',start)


    def write_block(self, block_index:int, start:int, data:bytearray):
        self.validate_data_to_write(block_index, start, data)

        size_in_bytes = len(data)
        block = self.read_block(block_index)
        for i in range(0, len(data)):
            block[i+start] = data[i]
