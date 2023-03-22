'''
    Initial Block Table
    Contains a key value structure, where the key is a patient's ID
    and the value is the index of the first block of a file in the address table
'''

class InitialBlockTable:
    
    '''
        Intial Block Table Constructor
        Initializes an empty dictionary, the Initial Block Table
    '''
    def __init__(self):
        self.table = {} 
    
    def add(self, id:str, index:int):
        '''
            PARAMS:

            id:str: the identification (id)
            index:int: a key of the initial block

            RETURN:
            dictionary: returns the Block Initial Table updated with the new     

        '''
        if id in self.table:
            return
        else:
            self.table[id] = index
            return 
    
    def search(self, id:str):
        '''
            PARAMS:
            id:str: the identification (id)

            RETURN:
                dictionary: returns the index of the id found, otherwise return -1 if the id wasnt found    
        '''
        if id in self.table:
            return self.table[id]
        else:
            return -1

    def get_all_initial_blocks(self):
        return self.table;