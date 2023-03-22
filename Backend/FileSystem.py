
from InitialBlockTable import InitialBlockTable
from FileAddressTable import FileAddressTable
import Helpers.FileHelper as FileHelper
import Helpers.BlockHelper as BlockHelper
from Storage import Storage
from TLB import TLB
from MMU import MMU
from env import DELIM

delim_fields = DELIM

class FileSystem:
    
    def __init__(self):
        self.storage = Storage()
        self.tlb = TLB()
        self.file_address_table = FileAddressTable()
        self.initial_block_table = InitialBlockTable()
        self.mmu = MMU()

    def read_data(self, id:str)->dict:
        '''
        FileSystem.read(cedula:str)->{status, data}
        '''
        result = {'status':0, 'data':None}

        first_block_index = self.initial_block_table.search(id)
        if -1 == first_block_index:
            result['status'] = 1
            return result
        
        block_addresses = self.file_address_table.get_file_addresses(first_block_index)
        if block_addresses == []:
            result['status'] = 1
            return result

        file_blocks = []
        for address in block_addresses:
            mmu_result = self.mmu.get_virtual_page_index_and_offset(address)
            page_index = mmu_result['page']
            offset = mmu_result['offset']

            page_frame = self.tlb.search_virtual_page_in_tlb(page_index)

            if -1 != page_frame: #exists
                blocks = self.tlb.read_frame(page_frame)
                block_needed = blocks[offset]

                file_blocks.append(block_needed)
            else:
                virtual_page = []

                first = self.mmu.get_block_index(page_index, 0)
                second = self.mmu.get_block_index(page_index, 1)
                virtual_page.append(self.storage.read_block(first))
                virtual_page.append(self.storage.read_block(second))

                self.tlb.load_frame(virtual_page, page_index)

                block_needed = virtual_page[offset]
                file_blocks.append(block_needed)
        
        if len(file_blocks) <= 0:
            result['status'] = 1
            return result

        data = FileHelper.file_to_raw(file_blocks,True)
        
        result['status'] = 0
        result['data'] = data
        return result

    def __write_new_data(self, initial_block:int, id:str, data:str):
        file = FileHelper.create_file(data)
        headers  = FileHelper.get_headers_from_file(file)
        
        blocks_required = len(file)
        path = self.file_address_table.add_new_file(blocks_required)
        if [] == path:
            return FileHelper.status(1, self.file_address_table.get_available_blocks())

        self.initial_block_table.add(id, path[0])
        
        for i in range(blocks_required):
            self.storage.write_block(path[i], 0, file[i])
        
        #self.storage.print_storage()
        self.storage.update_super_block(self.file_address_table.get_available_blocks())

        return FileHelper.status(0, self.file_address_table.get_available_blocks())
    
    def __append_data_with_bytes_available(self, id:str, data:str, path:list):

        initial_block = path[0]
        header = self.storage.read_block(initial_block)
        header = FileHelper.decode_headers(header)

        available_bytes = header['max_size'] - header['current_size']  #bytes available in last blocck
        first_position = FileHelper.block_size - available_bytes
        
        data_to_append = bytearray(data, 'utf-8')
        bytes_required = len(data_to_append)
    
        if bytes_required > available_bytes: 
            
            data_encoded = bytearray(data, 'utf-8')
            data_to_append_in_last_block = data_encoded[0:available_bytes]

            data = data[available_bytes:len(data)]#data restante por hacer append
     
            last_block_index = path[0]
            self.storage.write_block(path[len(path) - 1], first_position, data_to_append_in_last_block)

            #update headers
            header['current_size'] += len(data_to_append_in_last_block)
            encoded_headers = FileHelper.generate_headers(header['current_size'], header['max_size'])
            self.storage.write_block(initial_block,0, encoded_headers)

            #se puede borrar
            new_header = self.storage.read_block(initial_block)
            new_header_decoded = FileHelper.decode_headers(new_header)

            #fin borrar

            self.__append_data_in_new_block(id, data, path)
        else: 
            #write data
            last_block_index = path[len(path) - 1]
            self.storage.write_block(last_block_index, first_position, data_to_append)

            #update headers
            header['current_size'] += len(data_to_append)
            encoded_headers = FileHelper.generate_headers(header['current_size'], header['max_size'])
            self.storage.write_block(initial_block,0, encoded_headers)

            #se puede borrar
            new_header = self.storage.read_block(initial_block)
            new_header_decoded = FileHelper.decode_headers(new_header)
            #fin borrar

        return FileHelper.status(0, self.file_address_table.get_available_blocks())

    def __append_data_in_new_block(self, id:str, data:str, path:list):
        initial_block = path[0]
        header = self.storage.read_block(initial_block)
        header = FileHelper.decode_headers(header)
        
        new_file_information = FileHelper.create_file_without_headers(data)

        file = new_file_information['File']

        file_info = FileHelper.calculate_file_info(data)

        blocks_required = file_info['blocks_required']
        wasted_bytes = file_info['wasted_bytes']


        path = self.file_address_table.add_to_existing_file(initial_block, blocks_required)
        if [] == path:
            return FileHelper.status(1, self.file_address_table.get_available_blocks())

        new_current_size = header['current_size'] + file_info['current_size']
        new_max_size = header['max_size'] + file_info['max_size']

        headers = FileHelper.generate_headers(new_current_size, new_max_size)

        self.storage.write_block(initial_block, 0, headers)#update headers

        header = self.storage.read_block(initial_block)
        header = FileHelper.decode_headers(header)
    
        for i in range(blocks_required):
            self.storage.write_block(path[i], 0, file[i])

        return FileHelper.status(0, self.file_address_table.get_available_blocks())
    

    def __append_data(self, initial_block:int, id:str, data:str):
        
        #remove id and patient's name from data
        i = data.rfind(delim_fields) + 1
        data = data[i:]
        
        required = BlockHelper.calculate_blocks_required(data)
  
        if self.get_available_blocks() < required:
            return FileHelper.status(1, self.file_address_table.get_available_blocks())

        path = self.file_address_table.get_file_addresses(initial_block)
        if [] == path:
            return FileHelper.status(1, self.file_address_table.get_available_blocks())

        header = self.storage.read_block(initial_block)
        header = FileHelper.decode_headers(header)
    
        if header['current_size'] == header['max_size']: #no bytes available
            return self.__append_data_in_new_block(id, data, path)

        elif header['current_size'] <= header['max_size']: #bytes available in last block
            return self.__append_data_with_bytes_available(id, data, path)

        else:
            return FileHelper.status(1, self.file_address_table.get_available_blocks())

    def write_data(self, id:str, data:str):

        initial_block = self.initial_block_table.search(id)

        result = None
        if -1 == initial_block: #doesnt exist        
            result = self.__write_new_data(initial_block, id, data)
        else: #append
            #PENDING: remove id and name from data
            result = self.__append_data(initial_block, id, data)

        
        self.storage.print_storage()
        self.storage.update_super_block(self.file_address_table.get_available_blocks())
        
        #fin borrar
        return result
    def get_all_data(self)->list:
        '''
        RETURN
        All the patient's data
        '''
        table = self.initial_block_table.get_all_initial_blocks()
        patients = []
        for key, value in table.items():
            result = self.read_data(key)
            status = result["status"]
            data = result["data"]
            if status == 0:
                patients.append(data)
            
        return patients

    def get_available_blocks(self):
        info = self.storage.get_super_block_info()
        available_blocks = info['available_blocks']
        return available_blocks
        
    def get_total_blocks(self):
        info = self.storage.get_super_block_info()
        total_blocks = info['total_blocks']
        return total_blocks
