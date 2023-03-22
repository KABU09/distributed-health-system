'''
* TLB
* Contiene una estructura capaz de guardar paginas, representadas mediante bytes.
* Asimismo contiene el algoritmo de segunda oportunidad que permite hacer el reemplazo
* de paginas en los marcos. 
'''

from Helpers.BlockHelper import copy_block

class TLB:
    
    def __init__(self):
        self.last_used_frame = 0
        self.number_of_frames = 4
        self.page_frames = [None]*self.number_of_frames
        self.tlb = [None]*self.number_of_frames
    
     # Carga una la pagina 'page' a un marco
    def load_frame(self, page:list, virtual_page_index:int):
        flag = self.search_virtual_page_in_tlb(virtual_page_index)
        if self.last_used_frame < self.number_of_frames and flag == -1:
            self.page_frames[self.last_used_frame] = page
            row = [virtual_page_index, self.last_used_frame, 0] #virtual page index, frame, reference bit
            self.tlb[self.last_used_frame] = row
            self.last_used_frame+=1
        else:
            if flag == -1:
                self.second_chance_algorithm(page, virtual_page_index)
        return 
    
    def search_virtual_page_in_tlb(self, virtual_page:int):
        index = -1
        for row in self.tlb:
            if row != None:
                if row[0] == virtual_page:
                    index = row[1]
                    break
            else:
                break
        return index

    def second_chance_algorithm(self, page:bytearray, virtual_page_index:int):
        front = self.tlb.pop(0)
        second_chance_pages = []
        flag = False
        while True:
            if front[2] == 0 and not flag:
                index = front[1]
                new_row = [virtual_page_index, index, 0]
                self.tlb.append(new_row)
                self.page_frames[index] = page
                flag = True
            else:
                if len(second_chance_pages) == self.number_of_frames or flag:
                    while len(second_chance_pages) != 0:
                        front = second_chance_pages.pop(0)
                        front[2] = 0
                        self.tlb.append(front)
                    
                    if flag:
                        break
                    else:
                        front = self.tlb.pop(0)
                else:
                    second_chance_pages.append(front)
                    if len(self.tlb) != 0:
                        front = self.tlb.pop(0)

        return 

    def read_frame(self, index:int):
        if index < 0 or index >= self.number_of_frames:
            return []
        else:
            for row in self.tlb:
                if row[1] == index:
                    row[2] = 1
                    break
            return self.page_frames[index]