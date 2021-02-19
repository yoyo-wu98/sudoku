# coding:utf-8
# python3.6

from .structure import *
# from .analytics import *

class Solver():
    '''The solver for the sudoku puzzle.

    Elements:

    - structure: the structure inherited from the structure.add()
    - data: the current puzzle data
    - meta_size: the structure's meta_size inherited from the structure class in order to simplify the coding.
    - idxes_need_to_solve: list of indexes where the blank not solved [idx, ...]
    - steps: the step-by-step history of the solving process [(idx, update_num), ...]
    - ready: the step-by-step solutions which is ready to update [(idx, update_num), ...]
    - # TODO: predict part
    '''
    def __init__(self, problem_structure):
        assert problem_structure.__class__ == Structure, 'Parameter error: The problem_structure\'s class is not Structure.'
        self.structure = problem_structure
        self.data = problem_structure.data
        self.data_origin = list(self.data)
        self.meta_size = problem_structure.meta_size
        self.idxes_need_to_solve = [idx for idx, i in enumerate(self.data_origin) if i == '.']
        self.steps = []
        self.ready = [] # the [{idx : update_num} ..] of what is ready to update
    
    def check_idx_only(self, idx, data=None, candidate=None):
        '''Check if the item with the index idx is the only blank of its row / column / box.

        Input:
        - idx: the index where we check
        - data: the external data we put in.
        - candidate: if None(default), then the element to be updated will be fixed with the only one left from the element_set
                            else, then the candidate will be the new value.

        Ouput:
        - flg_changed(Boolean): True if it is ready to update
        
        # TODO: element_set auto recognition
        '''
        data = data if data else self.data
        # print(self.data[idx])

        # Check if the index is in ready list
        if idx in [i[0] for i in self.ready]: return False

        def check_idx_only_in_line(line, idx_in_line, element_set, candidate=candidate):
            '''check if the element with the index idx_in_line is the only one in line
            
            Input:
            - line
            - id_in_line
            - element_set
            '''
            candidate = candidate if candidate else list(element_set - set(line))[0]
            return candidate if (line[idx_in_line] == '.' and line.count('.') == 1) else element_set - set(line)
        
        # Check row
        row_line = data[int(idx / (self.meta_size**2)) * self.meta_size**2:int(idx / (self.meta_size**2) + 1) * self.meta_size**2]
        idx_in_row_line = idx % (self.meta_size**2)
        re_row = check_idx_only_in_line(row_line, idx_in_row_line, self.structure.element_set)
        # print(row_line, idx_in_row_line, re_row)
        if type(re_row) != set:
            self.ready.append((idx, re_row))
            return True
    
        # Check column
        col_line = [data[idx % (self.meta_size**2) + row * self.meta_size**2] for row in range(self.meta_size**2)]
        idx_in_col_line = int(idx / (self.meta_size**2))
        re_col = check_idx_only_in_line(col_line, idx_in_col_line, self.structure.element_set)
        # print(col_line, idx_in_col_line, re_col)
        if type(re_col) != set:
            self.ready.append((idx, re_col))
            return True
            
        # Check box
        box_line = [data[i] for i in self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)]]
        idx_in_box_line = self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)].index(idx)
        re_box = check_idx_only_in_line(box_line, idx_in_box_line, self.structure.element_set)
        # print(box_line, idx_in_box_line, re_box)
        if type(re_box) != set:
            self.ready.append((idx, re_box))
            return True
        
        re = list(re_col & re_row & re_box)
        if len(re) == 1:
            self.ready.append((idx, re[0]))
            return True
        
        return False
    
    def check_scanned_drop(self, element):
        '''Check whether the element can be scanned and dropped
        '''
        idxes_elements_distributed = [idx for idx, i in enumerate(self.data) if i == element]
        idxes_need_to_solve = list(self.idxes_need_to_solve)
        tmp_scanned_data = list(self.data)
        # check_in_same_row int(idx_1 / (meta_size**2)) == int(idx_2 / (meta_size**2))
        # check_in_same_col idx_1 % (meta_size**2) == idx_2 % (meta_size**2)
        # check_in_same_box self.structure.get_boxid_by_idx(idx)
        for idx in idxes_elements_distributed:
            idxes_need_to_solve = [i for i in list(idxes_need_to_solve) if ( \
              int(idx / (self.meta_size**2)) != int(i / (self.meta_size**2)) and \
              idx % (self.meta_size**2) != i % (self.meta_size**2) and \
              self.structure.get_boxid_by_idx(idx) != self.structure.get_boxid_by_idx(i) \
            )]
        for idx in list(set(self.idxes_need_to_solve) - set(idxes_need_to_solve)):
            tmp_scanned_data[idx] = ''
        print(self.structure.display(tmp_scanned_data))
        # print(idxes_need_to_solve)
        flg_change = False
        for idx in idxes_need_to_solve:
            if self.check_idx_only(idx, tmp_scanned_data, candidate=element): flg_change = True
        return flg_change
            
    