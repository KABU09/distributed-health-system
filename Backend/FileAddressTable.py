'''
    File address table
    It contains a structure that allows to save the indexes of the blocks
    where a specific patient file is found.
'''

class FileAddressTable:

    '''
        FILE ADDRESS TABLE Constructor
        Initialize a vector of 32 spaces with none
        The amount of available blocks is 31 because the first block is skipped
        The next block free as the first (when the list is empty) and the next block free
    '''
    def __init__(self):
        self.table = [None]*32
        self.free_blocks = 31
        self.next_free_block = 1

   
    '''
        PARAMS:

        number_of_blocks:int, number of blocks
        
        RETURN:
        list: return an empty list if the block number if is higher than the number of available blocks
        It updates the amount of available blocks, also the next free block is updated in the table

    '''
    def add_new_file(self, number_of_blocks:int):
        if number_of_blocks > self.free_blocks:
            return []
        else:
            route = []
            for i in range(self.next_free_block, len(self.table)):
                if len(route) == number_of_blocks:
                    self.table[i-1] = -1
                    self.next_free_block = i
                    break
                else:
                    if self.table[i] == None:
                        self.table[i] = i+1
                        route.append(i)
            self.free_blocks -= number_of_blocks
            return route

    def add_to_existing_file(self, initial_block:int, number_of_blocks:int):
        '''
        PARAMS:

        initial_block:int, number of initial block 
        number_of_blocks: int, number of blocks 
        
        RETURN:
        list: return an empty list if the block number if is higher than the number of available blocks, else, return a list
        with the route of a file

        '''
        if number_of_blocks > self.free_blocks:
            return []
        else:
            found = False
            i = initial_block
            route = []
            while i < len(self.table) and not(found):  
                if self.table[i] == -1: 
                    self.table[i] = self.next_free_block
                    found = True
                else:
                    i+=1

            for x in range(self.next_free_block, len(self.table)+1): 
                if len(route) == number_of_blocks:
                    self.table[x-1] = -1
                    self.next_free_block = x
                    break
                else: 
                    if x != len(self.table):   
                        self.table[x] = x+1
                    route.append(x)

            self.free_blocks -= number_of_blocks
            return route
    
    def get_file_addresses(self, initial_block:int):
        '''
        PARAMS:

        initial_block:int, number of initial block 
        
        RETURN:
        list: return an empty list if the block number if is higher than the number of available blocks, else, return a list
        with the route of a file

        '''
        route = []
        i = initial_block
        while i != -1:
            route.append(i)
            i = self.table[i]
            if i == len(self.table):
                break
        return route

    def get_available_blocks(self):
        '''

        RETURN:
        int: number of free blocks in the file address table

        '''
        if self.free_blocks < 0:
            return 0
        else:
            return self.free_blocks