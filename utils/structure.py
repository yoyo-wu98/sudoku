# coding:utf-8
# python3.6

class Structure():
    '''The structure of the sudoku.
    
    Elements:
    - data(list(str)):
        A list of all elements in this grid.
        All elements are strings.
        e.g. ['1', '.', '.', '4', '3', '4', '1', '.', '.', '3', '2', '1', '2', '.', '.', '3']
    - meta_size(int): 
        The size of the meta grid's box if this is a regular sudoku.
    - box_idx_list(list(list)):
        The list containing all lists of indexes in the same box.
        The idx of the box in box_idx_list is used as boxid.
    - element_set(set):
        The elements we use in puzzle.
    - flg_regular(Boolean):
        If the sudoku puzzle is the regular one.
        This flag is specially designed to optimize the time complexity of the box parts.
        True - regular one(9x9 sudoku with 3x3 boxes.)
    
    Functions:
    - display:
        Display the current situation of the sudoku.
        Output:
        - display_result(str)
    '''
    def __init__(self, data, meta_size=None, box_idx_list=None, element_set=None):
        '''Initialize the sudoku puzzle, we format the puzzle into our structure and check its validity.
        We also create a box_idx_list for representing all boxes.
        
        Input:
        - data(str):
            A string short for this sudoku puzzle.
            This string contains all the numbers we already know.
            All elements are split by ','.
            And '.' represents blank.
            e.g. ".,.,.,.,.,.,.,.,.,.,.,6,.,9,3,.,.,.,9,.,.,7,6,.,.,.,4,4,.,.,.,.,6,.,3,.,.,.,.,8,.,.,.,.,2,.,1,.,.,.,.,8,5,.,7,.,.,6,5,.,.,4,.,.,8,4,.,.,.,9,.,.,.,.,3,2,.,.,.,.,."
        - meta_size(int):
            e.g. 3(default)for 9x9; 4 for 16x16; 5 for 25x25
        - box_idx_list(list(list)):
            e.g. None(default): if meta_size == 2, then [[0, 4, 1, 5], [2, 6, 3, 7], [8, 12, 9, 13], [10, 14, 11, 15]];
                                if meta_size == 3, then [[0,1,2,9,10,11,18,19,20], [3,4,5,12,13,14,21,22,23], [6,7,8,15,16,17,24,25,26], \
                                                        [27,28,29,36,37,38,45,46,47], [30,31,32,39,40,41,48,49,50], [33,34,35,42,43,44,51,52,53]], \
                                                        [54,55,56,63,64,65,72,73,74], [57,58,59,66,67,68,75,76,77], [60,61,62,69,70,71,78,79,80]].

        - element_set(set):
            e.g. None(default): if meta_size == 3, then {'1', '2', '3', '4', '5', '6', '7', '8', '9'}

        # TODO: UNSOLVED, recognize the elements and collect them into a set.
        # TODO: UNSOLVED, restrict the input data: No '.' or '?'.
        '''
        self.data = data.replace(' ', '').strip('\n').split(',')
        self.meta_size = meta_size if meta_size else int(len(self.data)**(1/4))
        self.box_idx_list = box_idx_list if box_idx_list \
            else [sum([[i + int(k/(self.meta_size)) * self.meta_size**3 + (k%self.meta_size) * self.meta_size + self.meta_size**2 * j \
                for j in range(self.meta_size)] \
                for i in range(self.meta_size)], []) \
                for k in range(self.meta_size**2)]
        self.element_set = element_set if element_set \
            else set([str(i + 1) for i in range(self.meta_size**2)])
        self.flg_regular = True if (not box_idx_list and not element_set) else False

        self.check_data_and_boxes()

    def check_data_and_boxes(self, data=None, processed=False, box_idx_list=None):
        '''Check the correctness of data(default:None, for self.data) and box_idx_list(default:None, for self.box_idx_list).
        If processed(default:False), we ignore '' in data.
        '''
        data = data if data else self.data
        box_idx_list = box_idx_list if box_idx_list else self.box_idx_list
        assert len(data) == self.meta_size**4, \
            'Length error: The input data\'s length ' + str(len(data)) + ' does not equal to ' +  str(self.meta_size**4) + '.'
        set_data = set(data) - {'.'} if not processed else set(data) - {'.'} - {''}
        assert set_data.issubset(self.element_set), \
            'The input data has some invalid element' + str((set_data - self.element_set))
        assert set(sum(box_idx_list, [])) == set(range(self.meta_size**4)), \
            'The input box_idx_list ' + str(box_idx_list) + ' cannot be combined into the range(' + str(self.meta_size**4) + ').'

    def get_boxid_by_idx(self, idx):
        '''Use the element idx to find the box where it belongs.

        Input:
        - idx(int)

        Output:
        - boxid(int)
        '''
        if self.flg_regular: return int(idx / (self.meta_size**3)) * self.meta_size + int((idx % (self.meta_size**2)) / self.meta_size)
        return int(sum(self.box_idx_list, []).index(idx) / self.meta_size**2)
    
    def display(self, data=None):
        '''Display the current situation of the sudoku.
        
        Output:
        - display_result(str): A string of display result
        '''
        
        display = ''
        template_data = list('.' * (self.meta_size ** 4)) if not (self.flg_regular and self.meta_size < 4) else self.data
        for idx,char in enumerate(template_data):
            if idx % (self.meta_size**4) == 0:
                display += ('+' + '-' * (self.meta_size * 2 - 1)) * self.meta_size + "+\n|" + char
            elif idx % (self.meta_size**3) == 0:
                display += "|\n" + ('+' + '-' * (self.meta_size * 2 - 1)) * self.meta_size + "+\n|" + char
            elif idx % (self.meta_size**2) == 0:
                display += "|\n" + ('|' + ' ' * (self.meta_size * 2 - 1)) * self.meta_size + "|\n|" + char
            elif idx % (self.meta_size) == 0:
                display += '|' + char
            else:
                display += ' ' + char
            idx += 1
        display = display + "|\n" + ('+' + '-' * (self.meta_size * 2 - 1)) * self.meta_size + "+\n"
        if self.flg_regular and self.meta_size < 4 and data is None:
            return display
        # Formatted display
        template = list(display)
        valid_idxes = []
        data = data if data else self.data
        min_font_size = max([len(char) for char in data])
        for idx, i in enumerate(template):
            if i in self.element_set or i == '.':
                valid_idxes.append(idx)
            if idx not in valid_idxes and template[idx] != '\n':
                template[idx] = ' '
        for idx, i in enumerate(valid_idxes):
            template[i] = data[idx] if len(data[idx]) == min_font_size else data[idx] + ' ' * (min_font_size - len(data[idx]))
        # print(''.join(template))
        
        # Determine the margins (' ' / '|' / '-')
        for idx in range(self.meta_size**4):
            box = self.box_idx_list[self.get_boxid_by_idx(idx)]
            # # For debug:
            # print('Num:', str(idx), ' ', idx - self.meta_size**2, idx - self.meta_size**2 < 0, \
            #     idx - self.meta_size**2, idx - self.meta_size**2 not in box, \
            #     idx + self.meta_size**2, idx + self.meta_size**2 >= self.meta_size**4, \
            #     idx % (self.meta_size**2), idx % (self.meta_size**2) == 0, \
            #     idx - 1, idx - 1 not in box, \
            #     idx % (self.meta_size**2), idx % (self.meta_size**2) == self.meta_size**2 - 1, box)

            # upper
            if idx - self.meta_size**2 < 0 or idx - self.meta_size**2 not in box:
                template[valid_idxes[idx] - ((self.meta_size * 2) * self.meta_size + 2)] = '-' * min_font_size
            else:
                template[valid_idxes[idx] - ((self.meta_size * 2) * self.meta_size + 2)] = ' ' * min_font_size
            # lower
            if idx + self.meta_size**2 >= self.meta_size**4:
                template[valid_idxes[idx] + ((self.meta_size * 2) * self.meta_size + 2)] = '-' * min_font_size
            # left
            if idx % (self.meta_size**2) == 0 or idx - 1 not in box:
                template[valid_idxes[idx] - 1] = '|'
            # right
            elif idx % (self.meta_size**2) == self.meta_size**2 - 1:
                template[valid_idxes[idx] + 1] = '|'
        # print(''.join(template))

        # Determine the juctions (' ' / '+' / '|' / '-')
        for idx, item in enumerate(template):
            if item == ' ':
                flg_horizontal = False
                flg_vertical = False
                if idx - ((self.meta_size * 2) * self.meta_size + 2) < 0 or \
                    idx + ((self.meta_size * 2) * self.meta_size + 2) >= len(template) \
                    or template[idx - 1] == '-' * min_font_size or \
                    template[idx + 1] == '-' * min_font_size: flg_horizontal = True
                if idx % ((self.meta_size * 2) * self.meta_size + 2) == 0 or \
                    idx % ((self.meta_size * 2) * self.meta_size + 2) == ((self.meta_size * 2) * self.meta_size) : 
                    flg_vertical = True
                if (idx >= ((self.meta_size * 2) * self.meta_size + 2) and \
                    template[idx - ((self.meta_size * 2) * self.meta_size + 2)] == '|') or \
                (idx < len(template) - ((self.meta_size * 2) * self.meta_size + 2) and \
                    template[idx + ((self.meta_size * 2) * self.meta_size + 2)] == '|'): flg_vertical = True
                if flg_vertical and flg_horizontal: template[idx] = '+'
                elif flg_vertical or flg_horizontal: template[idx] = '|' if flg_vertical else '-'
        return ''.join(template)
    
    