import struct
from . import BlockHelper as blockhelper

block_size = blockhelper.block_size
amount_of_blocks = blockhelper.amount_of_blocks
header_attribute_size = 8 #en bytes

def create_file(raw:str)->list:
    '''
    PARAMS:

    raw:str is the data string that you want to transform into a file (list of bytearrays)
    
    RETURN:
    list[bytearray: is a file respresentation in list of bytearrays

    '''
    blocks_required = blockhelper.calculate_blocks_required(raw)
    max_size = blocks_required*block_size
    wasted_bytes = blockhelper.calculate_wasted_bytes(raw, blocks_required)
    current_size = max_size - wasted_bytes

    headers_block = generate_headers(current_size + block_size, max_size+block_size)
    content_blocks = blockhelper.generate_blocks(raw)

    headers_size_in_blocks = len(headers_block) / block_size
    content_size_in_blocks = len(content_blocks)

    file_size_in_blocks = headers_size_in_blocks + content_size_in_blocks
    file = []

    file.append(headers_block)

    for index in range(content_size_in_blocks):
        file.append(content_blocks[index])

    return file
def calculate_file_info(raw:str)->dict:
    '''
    RETURN
    dict {"blocks_required":blocks_required, 'wasted_bytes':wasted_bytes, 'current_size':current_size, 'max_size':max_size}
    '''
    blocks_required = blockhelper.calculate_blocks_required(raw)
    wasted_bytes = blockhelper.calculate_wasted_bytes(raw, blocks_required)
    max_size = blocks_required*block_size
    current_size = max_size - wasted_bytes
    return {"blocks_required":blocks_required, 'wasted_bytes':wasted_bytes, 'current_size':current_size, 'max_size':max_size}

def create_file_without_headers(raw:str)->list:
    
    blocks_required = blockhelper.calculate_blocks_required(raw)
    wasted_bytes = blockhelper.calculate_wasted_bytes(raw, blocks_required)
    content_blocks = blockhelper.generate_blocks(raw)
    content_size_in_blocks = len(content_blocks)

    file = []

    for index in range(content_size_in_blocks):
        file.append(content_blocks[index])

    return {'File': file, 'blocks_required':blocks_required, 'wasted_bytes': wasted_bytes}

def generate_headers(current_size:int, max_size:int)->bytearray:
    '''
    PARAMS:

    current_size:int is the file current size in bytes
    max_size:int is the max size in byte a file can growth
    
    RETURN:
    bytearray: a header block that can be appended in front of a file

    '''
    headers = bytearray(block_size)

    current_size_packed = struct.pack('>Q',current_size)
    max_size_packed = struct.pack('>Q', max_size)
    
    current_size_packed_bytearray = bytearray(current_size_packed)
    max_size_packed_bytearray = bytearray(max_size_packed)

    for index in range(len(current_size_packed_bytearray)):
        headers[index] = current_size_packed_bytearray[index]

    for index in range(len(max_size_packed_bytearray)):
        headers[header_attribute_size + index] = max_size_packed_bytearray[index]
    
    return headers
    
def decode_headers(headers:bytearray)->dict:
    '''
    PARAMS:

    headers:bytearray is the block header of a file
    
    RETURN:
    dict: {'current_size':current_size, 'max_size':max_size}

    '''
    current_size_packed_bytearray = bytearray(header_attribute_size)
    max_size_packed_bytearray = bytearray(header_attribute_size)

    for index in range(header_attribute_size):
        current_size_packed_bytearray[index] = headers[index]
    
    for index in range(header_attribute_size):
        max_size_packed_bytearray[index] = headers[header_attribute_size+index]

    current_size = (struct.unpack('>Q', current_size_packed_bytearray))[0]
    max_size = (struct.unpack('>Q', max_size_packed_bytearray))[0]

    return {'current_size':current_size, 'max_size':max_size}

def get_headers_from_file(file:list)->bytearray:
    '''
    PARAMS:

    file:list[bytearray] is file blocks
    
    RETURN:
    bytearray: a copy of the header block

    '''
    headers = bytearray(block_size)
    headers = blockhelper.copy_block(file[0])
    return headers

def remove_headers(file:list)->list:
    '''
    PARAMS:

    file:list[bytearray] is file blocks
    
    RETURN:
    list[bytearray]: file blocks without headers

    '''
    file_size = len(file)
    file_without_headers = []
    for index in range(1, file_size):
        block = blockhelper.copy_block(file[index])
        file_without_headers.append(block)

    return file_without_headers

def file_to_raw(file:list, has_headers:bool)->str:
    '''
    PARAMS:

    file:list[bytearray] is file blocks
    has_headers:boolean flag indicates if the file contains headers. If you set has_headers to False it means that your program previously called remove_headers(file) first that returns the content blocks

    RETURN:
    str: a content file raw. The original data tha was saved in disk

    '''

    data_decoded = None
    if has_headers == False:
        data_decoded = blockhelper.blocks_to_str(file)
    else:
        file_without_headers = remove_headers(file)
        
        data_decoded = blockhelper.blocks_to_str(file_without_headers)

    return data_decoded
    
def status(status:int, blocks_available:int):
    return {'status':status, 'blocks_available':blocks_available}
