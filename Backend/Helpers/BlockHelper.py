import math

block_size = 16
amount_of_blocks = 32

def split_str_every_nth_position(data:str, position:int):
    '''
    PARAMS
    
    data:str is the data to be writed in disk
    positin:int is the ntn position when the data will be splitted

    RETURN

    [str] returns an array of str elements
    '''
    split_strings = []
    
    for index in range(0, len(data), position):
        split_strings.append(data[index:index+position])

    return split_strings

def split_bytearray_every_nth_position(data_encoded:bytearray, position:int)->list:
    blocks = []
    for index in range(0, len(data_encoded), position):
        blocks.append(data_encoded[index:index+position])
    return blocks

def generate_blocks(data:str)->bytearray:
    '''
    PARAMS

    data:str is the data to be writed in disk

    RETURN

    [bytearray] returns an array with bytearray elements
    '''
    data_encoded = bytearray(data, 'utf-8')
    blocks = split_bytearray_every_nth_position(data_encoded, block_size)

    return blocks

def blocks_to_str(blocks:list):
    '''
    PARAMS

    [bytearray] returns an array with bytearray elements of block size

    RETURN

    data:str is the data to be writed sended to another node
    '''
    size = len(blocks)


    data_encoded = bytearray(size*block_size)

    counter = 0
    for block in blocks:
        for i in range(len(block)):
            data_encoded[counter] = block[i]
            counter = counter + 1
    
    data = data_encoded.decode('utf-8', 'ignore')
    data = data.rstrip('\x00')
    
    return data

def calculate_blocks_required(data:str):
    '''
    PARAMS

    data:str is the data to be writed in disk

    RETURN

    int is the number of min blocks required for writting the data in disk
    '''
    data_encoded = bytearray(data, 'utf-8')
    size = len(data_encoded)
    return math.ceil( size / block_size )

def calculate_wasted_bytes(data:str, blocks_required:int)->int:
    '''
    PARAMS

    data:str is the data to be writed in disk

    RETURN

    int is the number of empty bytes when data be trasnformed to blocks
    '''
    data_encoded = bytearray(data, 'utf-8')
    size = len(data_encoded)
    max_size = blocks_required*block_size
    return  max_size % size

def copy_block(block:bytearray)->bytearray:
    block_copied = bytearray(block_size)
    for index in range(block_size):
        block_copied[index] = block[index]
    return block_copied

def combine_blocks(block_array_1:list, block_array_2:list):
    block_array_combined = []

    for block in block_array_1:
        block_copied = copy_block(block)
        block_array_combined.append(block_copied)

    for block in block_array_2:
        block_copied = copy_block(block)
        block_array_combined.append(block_copied)

    return block_array_combined