# coding:utf-8
# python3.6

from .structure import *
from itertools import combinations
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
    - tmp_scanned_data # TODO: SOLVED, make self.tmp_scanned_data a list of dict {element: tmp_scanned_data ...} and delete self.tmp_scanned_element
    # - tmp_scanned_element

    Functions:
    - display
    - update: Update the self.data into a new state, clear the ready and record the steps
    - check_idx_only
    - check_idx_last_left
    - check_scanned_drop
    - check_area_drop
    - check_grouped_dropped
    - check_squared_dropped
    # TODO: UNSOLVED, predict part
    # FIXME: SOLVED, save_ready & save_scanned_data seperated
    '''
    def __init__(self, problem_structure):
        assert problem_structure.__class__ == Structure, 'Parameter error: The problem_structure\'s class is not Structure.'
        self.structure = problem_structure
        self.data = problem_structure.data # the same as the structure.data, synchronous
        self.data_origin = list(self.data)
        self.meta_size = problem_structure.meta_size
        self.idxes_need_to_solve = [idx for idx, i in enumerate(self.data_origin) if i == '.']
        self.steps = []
        self.ready = [] # the [{idx : update_num} ..] of what is ready to update
        self.display = problem_structure.display

        self.methods = {'scanned': self.check_scanned_drop, \
                    'area':self.check_area_drop, \
                    'group': self.check_group_drop, \
                    'square': self.check_square_drop}

        self.tmp_scanned_data = {ele:list(self.data_origin) for ele in problem_structure.element_set}
        # self.tmp_scanned_element = None
    
    def check_idx_only(self, idx, data=None, last_left=False, candidate=None, save_ready=True):
        '''Check if the item with the index idx is the only blank of its row / column / box.

        Input:
        - idx: the index where we check
        - data: the external data we put in.
        - last_left(Boolean): if False(default), then use the scan only;
                                    if True, then use the last_left_check.
        - candidate: if None(default), then the element to be updated will be fixed with the only one left from the element_set
                            else, then the candidate will be the new value.
        - save_ready: if True(default), then save the ready to update into self.ready; else, then just scan and update the tmp_scanned_data

        Ouput:
        - flg_changed(Boolean): True if it is ready to update
        
        # TODO: UNSOLVED, element_set auto recognition.
        # TODO: SOLVED, add a parameter to determine whether to use the last_left_check
        '''
        data = data if data else list(self.data)
        # print(self.data[idx])

        # Check if the index is already in ready list
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
            candidate = candidate if candidate else list(element_set - set(line))[0] if len(element_set - set(line)) == 1 else element_set - set(line)
            return candidate if (line[idx_in_line] == '.' and line.count('.') == 1) else element_set - set(line)
        
        # Check row
        row_line = data[int(idx / (self.meta_size**2)) * self.meta_size**2:int(idx / (self.meta_size**2) + 1) * self.meta_size**2]
        idx_in_row_line = idx % (self.meta_size**2)
        re_row = check_idx_only_in_line(row_line, idx_in_row_line, self.structure.element_set)
        # print(row_line, idx_in_row_line, re_row)
        if type(re_row) != set:
            if re_row in row_line:
                return False
            if save_ready:
                self.ready.append((idx, re_row))
            return True
    
        # Check column
        col_line = [data[idx % (self.meta_size**2) + row * self.meta_size**2] for row in range(self.meta_size**2)]
        idx_in_col_line = int(idx / (self.meta_size**2))
        re_col = check_idx_only_in_line(col_line, idx_in_col_line, self.structure.element_set)
        # print(col_line, idx_in_col_line, re_col)
        if type(re_col) != set:
            if re_col in col_line:
                return False
            if save_ready:
                self.ready.append((idx, re_col))
            return True
            
        # Check box
        box_line = [data[i] for i in self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)]]
        idx_in_box_line = self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)].index(idx)
        re_box = check_idx_only_in_line(box_line, idx_in_box_line, self.structure.element_set)
        # print(box_line, idx_in_box_line, re_box)
        if type(re_box) != set:
            if re_box in box_line:
                return False
            if save_ready:
                self.ready.append((idx, re_box))
            return True
        
        if last_left:
            re = list(re_col & re_row & re_box)
            if len(re) == 1:
                if re[0] in col_line or re[0] in row_line or re[0] in box_line:
                    return False
                if save_ready:
                    self.ready.append((idx, re[0]))
                return True
        
        return False

    def check_idx_last_left(self, idx, data=None, last_left=True, candidate=None, save_ready=True):
        return self.check_idx_only(idx, data=data, last_left=last_left, candidate=candidate, save_ready=save_ready)
    
    def check_scanned_drop(self, element, fresh=False, data=None, save_scanned_data=True, save_ready=True):
        '''Check whether the element can be scanned and dropped

        Input:
        - element
        - data(structure.data): if None(default), then we use the self.data. # TODO: SOLVED, Just leave them both. decide use data /(fresh and self.tmp_scanned_data) to pass the data.
        # - save_scanned_data(Boolean): if False, then we just do the basic scan and return flg_change;
        #                                 if True(default), then we save the tmp_scanned_date in self.tmp_scanned_data.
        - save_ready

        Output:
        - flg_change

        # TODO: SOLVED, add a parameter to determine whether to save the scanned progress and element
        '''
        if data:
            self.structure.check_data_and_boxes(data=data, processed=True)
        else:
            data = list(self.tmp_scanned_data[element]) if not fresh else list(self.data) # FIXME: SOLVED, all copy should be replaced by deepcopy
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
            if self.check_idx_only(idx, tmp_scanned_data, candidate=element, save_ready=save_ready): flg_change = True
        
        if save_scanned_data:
            self.tmp_scanned_data[element] = tmp_scanned_data
        # print(self.structure.display(tmp_scanned_data[element]))
        # print(idxes_need_to_solve)

        return flg_change

    def scan_all(self, method='scanned', fresh=False, save_scanned_data=True, save_ready=False): # BUG: SOLVED, scan all does not work for square
        '''Scan all the elements in self.element_set with selected method
        Input:
        - method: check_scanned_drop(default)
        - save_ready
        '''
        re = {ele: False for ele in self.structure.element_set}
        for ele in self.structure.element_set:
            re[ele] = self.methods[method](ele, fresh=fresh, save_scanned_data=save_scanned_data, save_ready=save_ready)
            print('method : ', method, '\n result ready : ', {chr(int(int(t[0])/(self.meta_size**2)) + ord('A'))+ str(int(t[0])%(self.meta_size**2) + 1) : t[1] for t in self.ready})
        return any(list(re.values()))

    def check_area_drop(self, element, fresh=False, save_scanned_data=False, save_ready=False):
        '''Check whether the element can be scanned in the area form and dropped

        Input:
        - element
        - fresh(Boolean): if False(default), then we use the self.tmp_scanned_data as the data
                    if True, then we use the self.data as the new data
        - save_scanned_data(Boolean)

        Output:
        - flg_change
        BUG: UNSOLVED, STILL not fixed!!!
        '''
        if self.check_scanned_drop(element, save_scanned_data=False, save_ready=False):
            # print('Before area drop, scanned drop can also make some changes.')
            pass
            # self.update()
            # return self.check_area_drop(element)
            # return True # FIXME: SOLVED, first update the data and then do the rest part.
        tmp_scanned_data = list(self.tmp_scanned_data[element]) if not fresh else list(self.data)

        # FIXME:  SOLVED, area scanned part. test_demo[6]
        # idxes_elements_distributed = [idx for idx, i in enumerate(self.data) if i == element]
        idxes_need_to_solve = [idx for idx, i in enumerate(tmp_scanned_data) if i == '.']
        boxes = self.structure.box_idx_list

        # Box
        # print('Box : ')
        for box in boxes:
            # print('box : ', box)
            if element in [tmp_scanned_data[idx] for idx in box]:
                continue
            box_idxes_to_solve = list(set(box) & set(idxes_need_to_solve))

            rows_of = []
            cols_of = []
            for idx in box_idxes_to_solve:
                rows_of.append(int(idx / (self.meta_size**2)))
                cols_of.append(idx % (self.meta_size**2))
            
            if len(set(rows_of)) == 1:
                row = rows_of[0]
                # print(' - row : ', row)
                for idx in idxes_need_to_solve:
                    if int(idx / (self.meta_size**2)) == row and idx not in box: tmp_scanned_data[idx] = ''
            
            if len(set(cols_of)) == 1:
                col = cols_of[0]
                # print(' - col : ', col)
                for idx in idxes_need_to_solve:
                    if idx % (self.meta_size**2) == col and idx not in box: tmp_scanned_data[idx] = ''
        
        # Row
        # print('Row : ')
        for rowi in range(self.meta_size**2):
            row = range(rowi * (self.meta_size**2), (rowi + 1) * (self.meta_size**2))
            if element in [tmp_scanned_data[idx] for idx in row]:
                continue
            row_idxes_to_solve = list(set(row) & set(idxes_need_to_solve))
            
            boxes_of = []
            for idx in row_idxes_to_solve:
                boxes_of.append(self.structure.get_boxid_by_idx(idx))

            if len(set(boxes_of)) == 1:
                box = boxes_of[0]
                # print(' - box : ', box)
                for idx in idxes_need_to_solve:
                    if self.structure.get_boxid_by_idx(idx) == box and idx not in row: tmp_scanned_data[idx] = ''
        
        # Col
        # print('Col : ')
        for coli in range(self.meta_size**2):
            col = [coli + row * self.meta_size**2 for row in range(self.meta_size**2)]
            if element in [tmp_scanned_data[idx] for idx in col]:
                continue
            col_idxes_to_solve = list(set(col) & set(idxes_need_to_solve))
            
            boxes_of = []
            for idx in col_idxes_to_solve:
                boxes_of.append(self.structure.get_boxid_by_idx(idx))

            if len(set(boxes_of)) == 1:
                box = boxes_of[0]
                # print(' - box : ', box)
                for idx in idxes_need_to_solve:
                    if self.structure.get_boxid_by_idx(idx) == box and idx not in col: tmp_scanned_data[idx] = ''
        
        if save_scanned_data:
            self.tmp_scanned_data[element] = tmp_scanned_data
        return self.check_scanned_drop(element, data=tmp_scanned_data, save_ready=save_ready)

    def check_group_drop(self, element, fresh=False, save_scanned_data=False, save_ready=True):
        '''Check whether the element can be scanned in group form and dropped

        Input:
        - element
        - fresh(Boolean)
        - save_scanned_data(Boolean)

        Output:
        - flg_change
        TODO: SOLVED, Group dropped part. test_demo[7:10]
        BUG: UNSOLVED, STILL not fixed!!!
        '''
        if self.check_scanned_drop(element, save_scanned_data=False, save_ready=False): 
            # print('Before grouped drop, scanned drop can also make some changes.')
            pass
            # self.update()
            # return self.check_group_drop(element)
            # return True # FIXME: SOLVED, no need to first update the data, just do the rest part.
        tmp_scanned_data = list(self.tmp_scanned_data[element]) if not fresh else list(self.data)
        # FIXME:  SOLVED, group scanned part
        idxes_need_to_solve = [idx for idx, i in enumerate(tmp_scanned_data) if i == '.']
        # print(idxes_need_to_solve)
        boxes = self.structure.box_idx_list
        box_rows = []
        box_cols = []
        for box in boxes:
            box_idxes_to_solve = list(set(box) & set(idxes_need_to_solve))

            box_rows.append(set([int(idx / (self.meta_size**2)) for idx in box_idxes_to_solve]))
            box_cols.append(set([idx % (self.meta_size**2) for idx in box_idxes_to_solve]))
        # print('box_rows', box_rows)
        # print('box_cols', box_cols)
        max_row_len = max([len(s) for s in box_rows])
        max_col_len = max([len(c) for c in box_cols])

        # Row group
        for iter_num in range(2, max_row_len + 1): # FIXME: UNSOLVED, REWIRTE THIS PART, MAKE SURE THAT THE GROUP PART DO NOT BE DELETED 
            combines = list(combinations(box_rows, iter_num))
            # print('combines:')
            for combine in combines:
                # print('combine:', combine)
                if all(list(map(lambda x: x == combine[0], combine))) and len(combine[0]) == iter_num:
                    print('Found the group drop part is', combine, ' rows.')
                    print(self.display(self.tmp_scanned_data[element]))
                    rows = combine[0]
                    for idx in idxes_need_to_solve:
                        if int(idx / (self.meta_size**2)) in rows:
                            # print('dropped', idx)
                            tmp_scanned_data[idx] = ''
        
        # Col group
        for iter_num in range(2, max_col_len + 1):
            combines = list(combinations(box_cols, iter_num))
            # print('combines:')
            for combine in combines:
                # print('combine:', combine)
                if all(list(map(lambda x: x == combine[0], combine))) and len(combine[0]) == iter_num:
                    # print('Found the group drop part is', combine, ' cols.')
                    cols = combine[0]
                    for idx in idxes_need_to_solve:
                        if idx % (self.meta_size**2) in cols: 
                            # print('dropped', idx)
                            tmp_scanned_data[idx] = '' # TODO: SOLVED, make every solver save their tmp_scanned_data
        
        # print(self.display(tmp_scanned_data))
        if save_scanned_data:
            self.tmp_scanned_data[element] = tmp_scanned_data
        return self.check_scanned_drop(element, data=tmp_scanned_data, save_ready=save_ready)

    def check_square_drop(self, element, fresh=False, save_scanned_data=False, save_ready=True):
        '''Check whether the element can be scanned in square form and dropped

        Input:
        - element
        - fresh(Boolean)
        - save_scanned_data(Boolean)

        Output:
        - flg_change

        TODO: SOLVED, Square dropped part. test_demo[11]
        '''
        if self.check_scanned_drop(element, save_scanned_data=False, save_ready=False): 
            # print('Before square drop, scanned drop can also make some changes.')
            pass
            # self.update()
            # return self.check_group_drop(element)
            # return True # FIXME: SOLVED, no need to first update the data, just do the rest part. test_demo[11]
        tmp_scanned_data = list(self.tmp_scanned_data[element]) if not fresh else list(self.data)
        # FIXME:  SOLVED, group scanned part
        idxes_need_to_solve = [idx for idx, i in enumerate(tmp_scanned_data) if i == '.']
        # print(idxes_need_to_solve)
        rows_of = []
        cols_of = []
        for row in range(self.meta_size**2):
            row_idxes_to_solve = list(set(range(row * self.meta_size**2, (row + 1) * self.meta_size**2)) & set(idxes_need_to_solve))
            rows_of.append(set([idx % (self.meta_size**2) for idx in row_idxes_to_solve]))
        for col in range(self.meta_size**2):
            col_idxes_to_solve = list(set([col + row * self.meta_size**2 for row in range(self.meta_size**2)]) & set(idxes_need_to_solve))
            cols_of.append(set([int(idx / (self.meta_size**2)) for idx in col_idxes_to_solve]))

        # Row group
        for iter_num in range(2, self.meta_size):
            combines = list(combinations(rows_of, iter_num))
            # print('combines:')
            for combine in combines:
                # print('combine:', combine)
                if all(list(map(lambda x: x == combine[0], combine))) and len(combine[0]) == iter_num:
                    # print('Found the square drop part is', combine, ' rows.')
                    cols = combine[0]
                    for idx in idxes_need_to_solve:
                        if idx % (self.meta_size**2) in cols:
                            # print('dropped', idx)
                            tmp_scanned_data[idx] = ''
        
        # Col group
        for iter_num in range(2, self.meta_size):
            combines = list(combinations(cols_of, iter_num))
            # print('combines:')
            for combine in combines:
                # print('combine:', combine)
                if all(list(map(lambda x: x == combine[0], combine))) and len(combine[0]) == iter_num:
                    # print('Found the square drop part is', combine, ' cols.')
                    rows = combine[0]
                    for idx in idxes_need_to_solve:
                        if int(idx / (self.meta_size**2)) in rows: 
                            # print('dropped', idx)
                            tmp_scanned_data[idx] = ''
        
        # print(self.display(tmp_scanned_data[element]))
        if save_scanned_data:
            self.tmp_scanned_data[element] = tmp_scanned_data
        return self.check_scanned_drop(element, data=tmp_scanned_data, save_ready=save_ready)
    
    def update(self):
        '''Update the self.data into a new state, clear the ready and record the steps.
        Make sure that the length of ready is greater than 0.
        '''
        ready = list(self.ready)
        assert len(ready) > 0, 'Update Error: the length of ready ' + str(len(ready)) + ' is not greater than 0.'
        for t in ready:
            self.data[t[0]] = t[1]
        self.steps.extend(self.ready)
        self.ready = []
        return True
    
    def step(self, data=None):
        '''A step of the solution:
            1. scan every element, checking for all ready to update, save ready(scanned - area - group - square);
            2. update the blanks;
            
        Input:
        - data: if None(default), then use self.data
        TODO: SOLVED, step part
        BUG: UNSOLVED, solve not complete, CHECKED its area scan part BUG, forget to check for element already exists.
        BUG: UNSOLVED, scan drop also has a bug
        '''
        if data:
            self.structure.check_data_and_boxes(data=data, processed=True)
        else:
            data = self.data
        re = {method : False for method in self.methods}
        for method in self.methods:
            if method == 'scanned':
                re[method] = self.scan_all(method, fresh=True, save_scanned_data=True, save_ready=True)
            else:
                re[method] = self.scan_all(method, fresh=False, save_scanned_data=False, save_ready=True)
        # print(self.display())
        print('re step : ', re)
        print('Before - ready: ', {chr(int(int(t[0])/(self.meta_size**2)) + ord('A'))+ str(int(t[0])%(self.meta_size**2) + 1) : t[1] for t in self.ready})
        if any(list(re.values())):
            re_step = self.update()
            print(self.display())
            print('After - ready: ', self.ready)
            return re_step
        else:
            return False
        
    def check(self, data=None):
        '''Check the selected data for whether it contains some blanks can be updated.
        
        Input:
        - data: if None(default), then use the self.data.
        TODO: SOLVED, check all part. NEED TO TEST AND RECHECK.
        FIXME: SOLVED, make every check optional for save_ready.

        Output:
        - flg: True if the puzzle can be updated now
        '''
        if data:
            self.structure.check_data_and_boxes(data=data, processed=True)
        else:
            data = self.data
        # for ele in self.element_set:
        # scan_all(self, method='scanned', fresh=False, save_scanned_data=True)
        re = {method : False for method in self.methods}
        for method in self.methods:
            if method == 'scanned':
                re[method] = self.scan_all(method, fresh=True, save_scanned_data=True, save_ready=False)
            else:
                re[method] = self.scan_all(method, fresh=False, save_scanned_data=False, save_ready=False)
        return any(list(re.values()))

    def done_check(self, data=None):
        '''Check if the puzzle already be solved.

        - data: if None(default), then use the self.data.
        '''
        if data:
            self.structure.check_data_and_boxes(data=data, processed=True)
        else:
            data = self.data
        return all([item in self.structure.element_set for item in data])

    def solve(self):
        '''Do the whole process of our basic solver until nothing can be done by basic solver.
        '''
        while not self.done_check() and self.step():
            continue
        print(self.display())
        return self.done_check()