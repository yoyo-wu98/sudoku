# coding:utf-8
# python3.6

# from .structure import *
# from .analytics import *

class Solver():
    '''The solver for the sudoku puzzle.

    Elements:
    - structure: the structure inherited from the structure.add()
    - puzzle: the current puzzle
    - meta_size: the structure's meta_size inherited from the structure class in order to simplify the coding.
    - steps: the step-by-step history of the so
    '''
    def __init__(self, problem_structure):
        self.structure = problem_structure
        self.puzzle = problem_structure.data
        self.puzzle_origin = self.puzzle
        self.meta_size = problem_structure.meta_size
        self.steps = []
        self.ready = [] # the [{idx : update_num} ..] of what is ready to update
    
    def check_idx_for_only_one_blank(self, idx):
        def check_line_for_only_one_blank(line, idx_in_line, element_set):
            return element_set - set(line) if (line[idx_in_line] == '.' and len(element_set - set(line)) == 1) else None
        
        print(self.puzzle[idx])
        
        # Check row
        row_line = self.puzzle[int(idx / (self.meta_size**2)) * self.meta_size**2:int(idx / (self.meta_size**2) + 1) * self.meta_size**2]
        print(row_line)
        idx_in_row_line = idx % (self.meta_size**2)
        print(idx_in_row_line)
        re_row = check_line_for_only_one_blank(row_line, idx_in_row_line, self.structure.element_set)
        print(re_row)
        if re_row:
            self.ready.append({idx : list(re_row)[0]})
            return
    
        # Check column
        col_line = [self.puzzle[idx % (self.meta_size**2) + row * self.meta_size**2] for row in range(self.meta_size**2)]
        print(col_line)
        idx_in_col_line = int(idx / (self.meta_size**2))
        print(idx_in_col_line)
        re_col = check_line_for_only_one_blank(col_line, idx_in_col_line, self.structure.element_set)
        print(re_col)
        if re_col:
            self.ready.append({idx : list(re_col)[0]})
            return
            
        # Check box
        box_line = [self.puzzle[i] for i in self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)]]
        print(box_line)
        idx_in_box_line = self.structure.box_idx_list[self.structure.get_boxid_by_idx(idx)].index(idx)
        print(idx_in_box_line)
        re_box = check_line_for_only_one_blank(box_line, idx_in_box_line, self.structure.element_set)
        print(re_box)
        if re_box:
            self.ready.append({idx : list(re_box)[0]})
            return
        
    # def check_