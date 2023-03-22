'''
MMU class translate physical to virtual addresses and viceverse
'''
class MMU:

    def __init__(self):
        self.block_size = 16
        self.amount_of_blocks = 32
        self.virtual_page_size = 2
        self.ammount_of_virtual_pages = self.amount_of_blocks / self.virtual_page_size
    
    def get_virtual_page_index_and_offset(self, block_index:int)->dict:
        '''
        PARAMS
        block_index:int  block index of the hard drive storage

        RETURNS
        Dict {'page', 'offset'}
        '''
        virtual_page_index = int(block_index / self.virtual_page_size)
        offset = block_index % self.virtual_page_size

        return {'page':virtual_page_index, 'offset': offset}

    
    def get_block_index(self, virtual_page_index:int, offset:int):
        '''
        PARAMS
        virtual_page_index:int  block index of the hard drive storage
        offset:int is the offset inside the virtual page

        RETURNS
        block_index:int block index of the hard drive storage
        '''
        block_index = int(self.virtual_page_size * virtual_page_index + offset)
        return block_index
