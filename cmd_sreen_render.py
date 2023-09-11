import os
import time

class IncorectScreenInstructionFormat(Exception):
    def __init__(self, message='the inscturions in the write_to_buffer method must be a dict'):
        super.__init__(message)

class screen_controler:

    OK = 10
    OWERWRITE_ALLTERT = -5
    INDEX_OUT_OF_BOUNDS = -2
    BALL_INDEX_OUT_OF_BOUNDS = -3

    BUFFER_OUT_OF_BOUNDS_LEFT = 'OTB_LEFT'
    BUFFER_OUT_OF_BOUNDS_RIGHT = 'OTB_RIGHT'
    BUFFER_OUT_OF_BOUNDS_TOP = 'OTB_TOP'
    BUFFER_OUT_OF_BOUNDS_BOTTOM = 'OTB_BOTTOM'

    ALL_OWERWRITE = 5

    def __init__(
            self, 
            screen_size_x : int, 
            screen_size_y : int, 
            pixel_info: dict|None = None,
            pixel_spacing : int = 0,
            boundry : bool = False) -> None:

        self.screen_x = screen_size_x
        self.screen_y = screen_size_y

        if not pixel_info:
            self.pixel_value_options = {'on' : '#', False : ' '}
        else:
            self.pixel_value_options = pixel_info

        self.pixel_spacing = pixel_spacing

        self.boundry = boundry

        self.screen_info_matrix = [[False for x in range(self.screen_x)] for y in range(self.screen_y)]

    def clear_screen(self) -> None:
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix-based systems (Linux, macOS)
            os.system('clear')

    def render_image(
            self, 
            print_lines_bottom : None|list = None, 
            print_lines_top : None|list = None
            ) -> None:

        if print_lines_bottom:
            if not isinstance(print_lines_bottom, list):
                print_lines_bottom = [print_lines_bottom]
            self.one_screen += '\n'
                
            for x in print_lines_bottom:
                self.one_screen += f'{x}\n'
            print(self.one_screen)
            return
        
        if print_lines_top:
            if not isinstance(print_lines_top, list):
                print_lines_top = [print_lines_top]

            top_line = ''
            
            for x in print_lines_top:
                top_line += f'{x}\n'

            self.one_screen = top_line
        else:
            self.one_screen = ''

        if self.boundry:
            one_boundry = 'X' + ''.join('-' for x in range(self.screen_x + ((self.screen_x-1)*self.pixel_spacing))) + 'X'
            self.one_screen += f'{one_boundry}\n'

        for line in self.screen_info_matrix:
            row = ''
            for idx, pixel_value in enumerate(line):
                try:
                    one_character = self.pixel_value_options[pixel_value]
                except:
                    one_character = pixel_value

                if idx+1 == len(line):
                    row += one_character
                    continue
                    
                row += one_character + ''.join(' ' for x in range(self.pixel_spacing))

            if self.boundry:
                row = f'|{row}|'

            self.one_screen += f'{row}\n'

        if self.boundry:
           self.one_screen += one_boundry

        self.clear_screen()
        print(self.one_screen)

        return self.OK

    def read_buffer(self, instructions : list|None = None) -> list:

        if not instructions:
            instructions = []
            for x in range(self.screen_x):
                for y in range(self.screen_y):
                    instructions.append([x, y])

        return_data = [None for x in instructions]

        for idx, cords in enumerate(instructions):

            x, y = cords

            if x+1 >= self.screen_x:
                return_data[idx] = self.BUFFER_OUT_OF_BOUNDS_RIGHT
            elif 0 > x:
                return_data[idx] = self.BUFFER_OUT_OF_BOUNDS_LEFT
            if y+1 >= self.screen_y:
                return_data[idx] = self.BUFFER_OUT_OF_BOUNDS_BOTTOM
            elif 0 > y:
                return_data[idx] = self.BUFFER_OUT_OF_BOUNDS_TOP

            if not return_data[idx]:
                try:
                    return_data[idx] = self.screen_info_matrix[y][x]
                except:
                    pass

        return return_data
    
    def check_validity_of_pixel_cords(self, cord_list : list):

        validity = []

        for cord in cord_list:

            if (
                cord[0] > 0 and cord[0] < self.screen_x
                ) and (
                cord[1] > 0 and cord[1] < self.screen_y
            ):
                validity.append(True)
                continue

            validity.append(False)

        return validity
    
    def convert_possition_to_cords(self, posstions : int|list) -> list:
        if isinstance(posstions, int):
            posstions = [posstions]

        possition_list = []
        
        for possition in posstions:
            x = possition%self.screen_x - 1
            y = int((possition-1-x)/self.screen_y)
            possition_list.append([x+1, y])

        return possition_list
    
    def write_to_buffer(self, instrucrions : dict) -> int:

        if not isinstance(instrucrions, dict):
            raise IncorectScreenInstructionFormat()
        
        for pixel_value in instrucrions:
            cords = instrucrions[pixel_value]

            if not isinstance(cords[0], tuple):
                cords = [cords]

            try:
                for cord in cords:
                     self.screen_info_matrix[cord[1]][cord[0]]
            except Exception as e:
                return self.INDEX_OUT_OF_BOUNDS, e
            
            for cord in cords:
                self.screen_info_matrix[cord[1]][cord[0]] = pixel_value

        return self.OK
        