# coding:utf-8
# python3.6

from .structure import *
# from .analytics import *

class BasicSolver():
    '''The basic solver for the sudoku puzzle.

    Elements:

    - structure: the structure inherited from the structure.add()
    - data: the current puzzle data
    - meta_size: the structure's meta_size inherited from the structure class in order to simplify the coding.
    - idxes_need_to_solve: list of indexes where the blank not solved [idx, ...]
    - steps: the step-by-step history of the solving process [(idx, update_num), ...]
    - ready: the step-by-step solutions which is ready to update [(idx, update_num), ...]
    - tmp_scanned_data
    - tmp_scanned_element
    # TODO: UNSOLVED, predict part
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

        self.tmp_scanned_data = None
        self.tmp_scanned_element = None
    
    def check_idx_only(self, idx, data=None, last_left=False, candidate=None):
        '''Check if the item with the index idx is the only blank of its row / column / box.

        Input:
        - idx: the index where we check
        - data: the external data we put in.
        - last_left(Boolean): if False(default), then use the scan only;
                                    if True, then use the last_left_check.
        - candidate: if None(default), then the element to be updated will be fixed with the only one left from the element_set
                            else, then the candidate will be the new value.

        Ouput:
        - flg_changed(Boolean): True if it is ready to update
        
        # TODO: UNSOLVED, element_set auto recognition.
        # TODO: SOLVED, add a parameter to determine whether to use the last_left_check
        '''
        data = data if data else list(self.data)
        # print(self.data[idx])

        # Check if the index is in ready list
        if idx in [i[0] for i in self.ready]: return False

        def check_idx_only_in_line(line, idx_in_line, element_set, candidate=candidate):
            '''check if the element with the index idx_in_line is the only one in line
            
            Input:
            - line
            - id_in_line
            - element_set

            Output:
            - flg_change
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
        
        if last_left:
            re = list(re_col & re_row & re_box)
            if len(re) == 1:
                self.ready.append((idx, re[0]))
                return True
        
        return False

    def check_idx_last_left(self, idx, data=None, last_left=True, candidate=None):
        return self.check_idx_only(idx, data=data, last_left=last_left, candidate=candidate)
    
    def check_scanned_drop(self, element, data=None ,out_scanned_data=False):
        '''Check whether the element can be scanned and dropped

        Input:
        - element
        - data(structure.data): if None(default), then we use the self.data.
        - out_scanned_data(Boolean): if False(default), then we just do the basic scan and return flg_change;
                                        if True, then we save the tmp_scanned_date in self.tmp_scanned_data
                                                                and element in self.tmp_scanned_element.

        Output:
        - flg_change

        # TODO: SOLVED, add a parameter to determine whether to save the scanned progress and element
        '''
        if data:
            self.structure.check_data_and_boxes(data=data, processed=True)
        else:
            data = list(self.data) # FIXME: SOLVED, all copy should be replaced by deepcopy
        idxes_elements_distributed = [idx for idx, i in enumerate(data) if i == element]
        idxes_need_to_solve = list(self.idxes_need_to_solve)
        tmp_scanned_data = list(data)
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
        
        flg_change = False
        for idx in idxes_need_to_solve:
            if self.check_idx_only(idx, tmp_scanned_data, candidate=element): flg_change = True
        
        if out_scanned_data:
            self.tmp_scanned_data = tmp_scanned_data
            self.tmp_scanned_element = element
        else:
            print(self.structure.display(tmp_scanned_data))
            # print(idxes_need_to_solve)

        return flg_change

    def check_area_drop(self, element):
        '''Check whether the element can be scanned in the area form and dropped

        Input:
        - element

        Output:
        - flg_change
        '''
        if self.check_scanned_drop(element, out_scanned_data=True): 
            print('No need to area drop, scanned drop is enough.')
            return True# FIXME: UNSOLVED, first update the data and then do the rest part.
        else:
            assert self.tmp_scanned_element == element, 'Scanned Error: tmp_scanned_element not the same one:' + self.tmp_scanned_element + ' != ' + element
            tmp_scanned_data = list(self.tmp_scanned_data)

        # FIXME:  SOLVED, area scanned part
        # idxes_elements_distributed = [idx for idx, i in enumerate(self.data) if i == element]
        idxes_need_to_solve = [idx for idx, i in enumerate(tmp_scanned_data) if i == '.']
        boxes = self.structure.box_idx_list

        # Box
        for box in boxes:
            box_idxes_to_solve = list(set(box) & set(idxes_need_to_solve))

            rows_of = []
            cols_of = []
            for idx in box_idxes_to_solve:
                rows_of.append(int(idx / (self.meta_size**2)))
                cols_of.append(idx % (self.meta_size**2))
            
            if len(set(rows_of)) == 1:
                row = rows_of[0]
                for idx in idxes_need_to_solve:
                    if int(idx / (self.meta_size**2)) == row: tmp_scanned_data[idx] = ''
            
            if len(set(cols_of)) == 1:
                col = cols_of[0]
                for idx in idxes_need_to_solve:
                    if idx % (self.meta_size**2) == col: tmp_scanned_data[idx] = ''
        
        # Row
        for rowi in range(self.meta_size**2):
            row = [range(rowi * (self.meta_size**2), (rowi + 1) * (self.meta_size**2))]
            row_idxes_to_solve = list(set(row) & set(idxes_need_to_solve))
            
            boxes_of = []
            for idx in row_idxes_to_solve:
                boxes_of.append(self.structure.get_boxid_by_idx(idx))

            if len(set(boxes_of)) == 1:
                box = boxes_of[0]
                for idx in idxes_need_to_solve:
                    if self.structure.get_boxid_by_idx(idx) == box: tmp_scanned_data[idx] = ''
        
        # Col
        for coli in range(self.meta_size**2):
            col = [coli + row * self.meta_size**2 for row in range(self.meta_size**2)]
            col_idxes_to_solve = list(set(col) & set(idxes_need_to_solve))
            
            cols_of = []
            for idx in col_idxes_to_solve:
                boxes_of.append(self.structure.get_boxid_by_idx(idx))

            if len(set(boxes_of)) == 1:
                box = boxes_of[0]
                for idx in idxes_need_to_solve:
                    if self.structure.get_boxid_by_idx(idx) == box: tmp_scanned_data[idx] = ''
        
        return self.check_scanned_drop(element, data=tmp_scanned_data)

    def check_grouped_dropped(self, element):
        '''Check whether the element can be scanned in group form and dropped

        Input:
        - element

        Output:
        - flg_change
        TODO: UNSOLVED, Grouped dropped part. test_demo[6]
        '''
        
        return False

    def check_squared_dropped(self, element):
        '''Check whether the element can be scanned in square form and dropped

        Input:
        - element

        Output:
        - flg_change
        TODO: UNSOLVED, Squared dropped part. test_demo[7]
        '''
        return False
    
    def update(self):
        '''Update the self.data into a new state, clear the ready and record the steps
        '''
        ready = list(self.ready)
        assert len(ready) > 0, 'Update Error: the length of ready ' + str(len(ready)) + ' is not greater than 0.'
        for t in ready:
            self.data[t[0]] = t[1]
        self.steps.extend(self.ready)
        self.ready = []
        return True
    
    