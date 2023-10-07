from cmd_sreen_render import screen_controler
import random
import time
import queue 
import threading
from pynput import keyboard

class game:

    USER_WINNER = 'winner'
    USER_LOSER = 'loser'

    pixel_info = {
                False : '  ',
                'snake_head' : '■■',
                'snake_body' : '⛝⛝',
                'apple' : '©©'
                }
    
    SNAKE_UP = 1
    SNAKE_DOWN = -1
    SNAKE_LEFT = 2
    SNAKE_RIGHT = -2

    def __init__(self, screen_x : int, screen_y : int):

        self.x = screen_x
        self.y = screen_y

        self.screen_controler = screen_controler(
            screen_size_x=screen_x,
            screen_size_y=screen_y,
            pixel_info = self.pixel_info,
            boundry=True
            )
        
        self.availeable_apple_spots = []
        self.apple_spot = None

        self.snake_occupiing_spots = []
        self.snake_head_position = None
        self.snake_direction = None

    def spawn_snake(self, start_tail_pieces : int = 5):

        low_x = round(self.x*0.25)
        high_x = round(self.x*0.75)

        low_y = round(self.y*0.25)
        high_y = round(self.y*0.75)

        head_x = random.randint(low_x, high_x)
        head_y = random.randint(low_y, high_y)

        self.snake_head_position = (head_x, head_y)

        instructions = {'snake_head' : self.snake_head_position, 
                        'snake_body' : []
                        }
        
        directions = [[self.SNAKE_LEFT, self.SNAKE_RIGHT], [self.SNAKE_UP, self.SNAKE_DOWN]]
        snake_body = [x for x in self.snake_head_position]

        for x in range(start_tail_pieces):
            if not x or not x%3:
                one_directionos = [[x for x in y] for y in directions]
                
                if not x%3 and x:
                    one_directionos[direction_idx].pop(inner_idx-1)
                
                direction_idx = random.randint(0, 1)
                inner_idx = random.choice([idx for idx, x in enumerate(one_directionos[direction_idx])])
                random_direction = one_directionos[direction_idx][inner_idx]
                
                if not x:
                    self.snake_direction = one_directionos[direction_idx][inner_idx-1]

            match random_direction:
                case self.SNAKE_LEFT:
                    snake_body = (snake_body[0] -1, snake_body[1])
                case self.SNAKE_RIGHT:
                    snake_body = (snake_body[0] +1, snake_body[1])
                case self.SNAKE_UP:
                    snake_body = (snake_body[0], snake_body[1]-1)
                case self.SNAKE_DOWN:
                    snake_body = (snake_body[0], snake_body[1]+1)
            
            instructions['snake_body'].append(snake_body)

        self.screen_controler.write_to_buffer(instructions)

        self.snake_occupiing_spots = instructions['snake_body']

        self.availeable_apple_spots = []

        for x in range(self.x):
            for y in range(self.y):
                one_cord = (x, y)
                data = self.screen_controler.read_buffer([one_cord])[0]
                if data:
                    continue
                self.availeable_apple_spots.append(one_cord)

    def spanw_apple(self):
        if not self.availeable_apple_spots:
            return self.USER_WINNER
        
        self.apple_spot = random.choice(self.availeable_apple_spots)
        self.screen_controler.write_to_buffer({'apple' : self.apple_spot})

    def move_snake(self, direction : int):

        if not direction + self.snake_direction:
            return
        
        remove_tail = True
        
        self.snake_direction = direction

        self.snake_occupiing_spots.insert(0, (self.snake_head_position[0], self.snake_head_position[1]))

        match self.snake_direction:

            case self.SNAKE_LEFT:
                self.snake_head_position = (self.snake_head_position[0] - 1, self.snake_head_position[1])
            case self.SNAKE_RIGHT:
                self.snake_head_position = (self.snake_head_position[0] + 1, self.snake_head_position[1])
            case self.SNAKE_UP:
                self.snake_head_position = (self.snake_head_position[0], self.snake_head_position[1] -1)
            case self.SNAKE_DOWN:
                self.snake_head_position = (self.snake_head_position[0], self.snake_head_position[1] +1)

        instructions = {
            'snake_head' : self.snake_head_position,
            'snake_body' : self.snake_occupiing_spots[0]
        }

        output = self.screen_controler.read_buffer([self.snake_head_position])[0]
        for x in (
            self.screen_controler.BUFFER_OUT_OF_BOUNDS_LEFT, 
            self.screen_controler.BUFFER_OUT_OF_BOUNDS_RIGHT,
            self.screen_controler.BUFFER_OUT_OF_BOUNDS_BOTTOM,
            self.screen_controler.BUFFER_OUT_OF_BOUNDS_TOP
            ):
            if x == output:
                return self.USER_LOSER
        
        if output == 'apple':
            remove_tail = False

        elif output == 'snake_body':
            return self.USER_LOSER
        
        if remove_tail:
            instructions[False] = self.snake_occupiing_spots.pop(-1)
            self.availeable_apple_spots.append(instructions[False])

        self.screen_controler.write_to_buffer(instructions)

        head_idx = self.availeable_apple_spots.index(self.snake_head_position)

        self.availeable_apple_spots.pop(head_idx)

        if not remove_tail:
            self.spanw_apple()

class game_controler:

    def __init__(self, x : 5, y : 5, start_tail_piece : int = 5):
        self.x, self.y = x, y
        self.snake_game = game(self.x, self.y)
        self.snake_game.spawn_snake(start_tail_pieces=start_tail_piece)
        self.snake_game.spanw_apple()
        self.snake_game.screen_controler.render_image()
        self.queue = queue.Queue()
        self.queue.put(self.snake_game.snake_direction)
        self.repeat_delay = 0.01
        self.key_pressed = None

    def on_key_press(self, key):
        if key == keyboard.Key.left:
            self.key_pressed = self.snake_game.SNAKE_LEFT
        elif key == keyboard.Key.right:
            self.key_pressed = self.snake_game.SNAKE_RIGHT
        elif key == keyboard.Key.up:
            self.key_pressed = self.snake_game.SNAKE_UP
        elif key == keyboard.Key.down:
            self.key_pressed = self.snake_game.SNAKE_DOWN

    def on_key_release(self, key):
        if key in [keyboard.Key.left, keyboard.Key.right, keyboard.Key.up, keyboard.Key.down]:
            self.key_pressed = None

    def key_repeat_thread(self):
        while 1:
            if self.key_pressed:
                while not self.queue.empty():
                    try:
                        cmd = self.queue.get()
                    except queue.Empty:
                        break
                if not self.snake_game.snake_direction + self.key_pressed:
                    self.queue.put(self.snake_game.snake_direction)
                else:
                    self.queue.put(self.key_pressed)

            time.sleep(self.repeat_delay)

    def ganerate_frame(self):
        input('press enter to start')
        while 1:
            direction = self.queue.get()

            while not self.queue.empty():
                try:
                    cmd = self.queue.get()
                except queue.Empty:
                    break

            if direction is self.snake_game.SNAKE_RIGHT or direction is self.snake_game.SNAKE_LEFT:
                amount_to_move = 1
            else:
                amount_to_move = 1

            for x in range(amount_to_move):   
                result = self.snake_game.move_snake(direction)
                self.snake_game.screen_controler.render_image(print_lines_top=[f'snake length: {len(self.snake_game.snake_occupiing_spots)}'])
                if result is self.snake_game.USER_LOSER:
                    print('you lost xd')
                    input()
                if result is self.snake_game.USER_WINNER:
                    print('you won :D')
                    input()
                if amount_to_move == 1:
                    time.sleep(0.1)
                else:
                    time.sleep(0.1/amount_to_move)
            
            self.queue.put(direction)

    def run(self):

        game_thread = threading.Thread(target=self.ganerate_frame)
        key_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        key_listener.start()

        repeat_thread = threading.Thread(target=self.key_repeat_thread)
        repeat_thread.daemon = True
        repeat_thread.start()
        game_thread.start()

        key_listener.join()
        
if __name__ == '__main__':
    snake_game = game_controler(70, 20, start_tail_piece=5)
    snake_game.run()
