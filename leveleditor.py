"""
Propeller Game Level Editor Engine created by Brad Wyatt
"""
import random
import sys
import os
import copy
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename, askopenfilename
from ast import literal_eval
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)

# Tk box for color
ROOT = tk.Tk()
ROOT.withdraw()

MENUON = 0
RUNNING = True # Flags game as on
SCREEN = None
SCREENWIDTH, SCREENHEIGHT = 936, 650
COLORKEY = [160, 160, 160]

# Starting positions of each of the objects
STARTPOS = {'player': (10, 4), 'wall': (40, 12), 'reverse_wall': (102, 12),
            'spring': (255, 12), 'flyer': (130, 12), 'smily_robot': (162, 12),
            'door': (195, 2), 'diamonds': (225, 14), 'sticky_block': (70, 12),
            'fall_spikes': (290, 12), 'stand_spikes': (320, 12)}

# Grouping Images and Sounds
IMAGES = {}
SOUNDS = {}
GRID_SPRITES = pygame.sprite.Group()
PLAYER_SPRITES = pygame.sprite.Group()
START_SPRITES = pygame.sprite.Group()
PLACED_SPRITES = pygame.sprite.Group()
PLAY_SPRITES = pygame.sprite.Group()
CLOCK = pygame.time.Clock()

# Below function from stackoverflow used for adjusting 
# python image loading to correct directory
def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] # feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0, appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print('Please run from an OS console.')
        import time
        time.sleep(10)
        sys.exit(1)
adjust_to_correct_appdir()

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    SOUNDS[name] = sound

def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    IMAGES[name] = new_image

def snap_to_grid(pos):
    best_num_x, best_num_y = 0, 48 # Y is 48 so it doesn't go above the menu
    for x_coord in range(0, SCREENWIDTH, 24):
        if pos[0]-x_coord <= 24 and pos[0]-x_coord >= 0:
            best_num_x = x_coord
    for y_coord in range(48, SCREENHEIGHT, 24):
        if pos[1]-y_coord <= 24 and pos[1]-y_coord >= 0:
            best_num_y = y_coord
    return (best_num_x, best_num_y)

def remove_object():
    for placed_item_list in (PLACED.player_list, PLACED.wall_list, PLACED.flyer_list,
                             PLACED.spring_list, PLACED.diamonds_list, PLACED.reverse_wall_list,
                             PLACED.smily_robot_list, PLACED.door_list, PLACED.sticky_block_list,
                             PLACED.fall_spikes_list, PLACED.stand_spikes_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(MOUSEPOS):
                PLACED_SPRITES.remove(placed_item)
                placed_item_list.remove(placed_item)

def dragging_function():
    DRAGGING.dragging_none()
    START.player.rect.topleft = STARTPOS['player']
    START.wall.rect.topleft = STARTPOS['wall']
    START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']
    START.spring.rect.topleft = STARTPOS['spring']
    START.flyer.rect.topleft = STARTPOS['flyer']
    START.smily_robot.rect.topleft = STARTPOS['smily_robot']
    START.door.rect.topleft = STARTPOS['door']
    START.diamonds.rect.topleft = STARTPOS['diamonds']
    START.sticky_block.rect.topleft = STARTPOS['sticky_block']
    START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']
    START.fall_spikes.rect.topleft = STARTPOS['stand_spikes']

def get_color():
    color = askcolor()
    COLORKEY[0] = color[0][0]
    COLORKEY[1] = color[0][1]
    COLORKEY[2] = color[0][2]

def create_placed_objects(placed_class, object_coord, placed_length):
    placed_list = []
    if placed_length >= 1:
        for instance_coord in object_coord:
            placedobj = placed_class()
            placedobj.rect.topleft = snap_to_grid(instance_coord)
            PLACED_SPRITES.add(placedobj)
            placed_list.append(placedobj)
        return placed_list
    return []

def load_file(colorkey=[160, 160, 160]):
    try:
        request_file_name = askopenfilename(defaultextension=".lvl")
        open_file = open(request_file_name, "r")
        loaded_file = open_file.read()
        loaded_dict = literal_eval(loaded_file)
        # Remove sprites on current level
        def remove_all_sprites(placelist):
            for placed_obj in placelist:
                PLACED_SPRITES.remove(placed_obj)
                
        remove_all_sprites(PLACED.player_list)
        remove_all_sprites(PLACED.door_list)
        remove_all_sprites(PLACED.wall_list)
        remove_all_sprites(PLACED.flyer_list)
        remove_all_sprites(PLACED.reverse_wall_list)
        remove_all_sprites(PLACED.spring_list)
        remove_all_sprites(PLACED.smily_robot_list)
        remove_all_sprites(PLACED.diamonds_list)
        remove_all_sprites(PLACED.sticky_block_list)
        remove_all_sprites(PLACED.fall_spikes_list)
        remove_all_sprites(PLACED.stand_spikes_list)
        open_file.close()
        
        # Removes all placed lists
        PLACED.remove_all()
        
        print("Removed all sprites. Now creating lists for loaded level.")
        
        PLACED.player_list = create_placed_objects(PlacedPlayer, loaded_dict['player'], len(loaded_dict['player']))
        PLACED.door_list = create_placed_objects(PlacedDoor, loaded_dict['door'], len(loaded_dict['door']))
        PLACED.wall_list = create_placed_objects(PlacedWall, loaded_dict['wall'], len(loaded_dict['wall']))
        PLACED.flyer_list = create_placed_objects(PlacedFlyer, loaded_dict['flyer'], len(loaded_dict['flyer']))
        PLACED.reverse_wall_list = create_placed_objects(PlacedReverseWall, loaded_dict['reverse_wall'], len(loaded_dict['reverse_wall']))
        PLACED.spring_list = create_placed_objects(PlacedSpring, loaded_dict['spring'], len(loaded_dict['spring']))
        PLACED.smily_robot_list = create_placed_objects(PlacedSmilyRobot, loaded_dict['smily_robot'], len(loaded_dict['smily_robot']))
        PLACED.diamonds_list = create_placed_objects(PlacedDiamonds, loaded_dict['diamonds'], len(loaded_dict['diamonds']))
        PLACED.sticky_block_list = create_placed_objects(PlacedStickyBlock, loaded_dict['sticky_block'], len(loaded_dict['sticky_block']))
        PLACED.fall_spikes_list = create_placed_objects(PlacedFallSpikes, loaded_dict['fall_spikes'], len(loaded_dict['fall_spikes']))
        PLACED.stand_spikes_list = create_placed_objects(PlacedStandSpikes, loaded_dict['stand_spikes'], len(loaded_dict['stand_spikes']))
        PLACED.refresh_total_placed_list()
        colorkey = loaded_dict['RGB']
        
        print("File Loaded")
        
        return colorkey
    except IOError:
        #Error reading file
        print("IOError")
        return colorkey
    except ValueError:
        #There's a file there, but we don't understand the number.
        print("ValueError")
        return colorkey
    except TypeError:
        return colorkey

def save_file(colorkey):
    try:
        if PLACED.player_list and PLACED.door_list:
            # default extension is optional, here will add .txt if missing
            save_file_prompt = asksaveasfilename(defaultextension=".lvl")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                obj_locations = copy.deepcopy(PLACED.get_dict_rect_positions())
                obj_locations['RGB'] = colorkey
                save_file_name.write(str(obj_locations))
                save_file_name.close()
                print("File Saved Successfully.")
        else:
            print("Error! Need player and door to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")



class InfoScreen():
    def __init__(self, screen):
        self.screen = screen
        self.title = INFO_SCREEN
        self.clock = pygame.time.Clock()
        self.menuon = 2
        self.main_loop(self)

    def main_loop(self, screen):
        while self.menuon == 2:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            info_events = pygame.event.get()
            pygame.display.flip()
            for info_event in info_events:
                if info_event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if info_event.type == KEYDOWN:
                    if info_event.key == K_ESCAPE:
                        self.menuon = 1
                        return self.menuon

class StartBlankBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.player:
            self.image = IMAGES["SPR_PLAYER"]
        elif DRAGGING.wall:
            self.image = IMAGES["SPR_WALL"]
        elif DRAGGING.diamonds:
            self.image = IMAGES["SPR_DIAMONDS"]
        elif DRAGGING.door:
            self.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR"], (24, 40))
        elif DRAGGING.flyer:
            self.image = IMAGES["SPR_FLYER"]
        elif DRAGGING.reverse_wall:
            self.image = IMAGES["SPR_REVERSE_WALL"]
        elif DRAGGING.smily_robot:
            self.image = IMAGES["SPR_SMILYROBOT"]
        elif DRAGGING.spring:
            self.image = IMAGES["SPR_SPRING"]
        elif DRAGGING.sticky_block:
            self.image = IMAGES["SPR_STICKYBLOCK"]
        elif DRAGGING.fall_spikes:
            self.image = IMAGES["SPR_FALLSPIKES"]
        elif DRAGGING.stand_spikes:
            self.image = pygame.transform.rotate(IMAGES["SPR_STANDSPIKES"],
                                                 START.stand_spikes.rotate)
        else:
            self.image = IMAGES["SPR_BLANKBOX"]

class StartWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.wall:
            START.blank_box.rect.topleft = STARTPOS['wall'] # Replaces in Menu
            START.wall.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                       MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.wall.rect.topleft = STARTPOS['wall']

class StartReverseWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_REVERSE_WALL"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.reverse_wall:
            START.blank_box.rect.topleft = STARTPOS['reverse_wall'] # Replaces in Menu
            START.reverse_wall.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                               MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']

class StartDiamonds(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.diamonds:
            START.blank_box.rect.topleft = STARTPOS['diamonds'] # Replaces in Menu
            START.diamonds.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                           MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.diamonds.rect.topleft = STARTPOS['diamonds']

class StartDoor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR"], (24, 40))
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.door and not PLACED.door_list:
            START.blank_box.rect.topleft = STARTPOS['door'] # Replaces in Menu
            START.door.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                       MOUSEPOS[1]-(self.image.get_height()/4))
            self.image = IMAGES["SPR_DOOR"]
        else:
            START.door.rect.topleft = STARTPOS['door']
            self.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR"], (24, 40))

class StartFlyer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.flyer:
            START.blank_box.rect.topleft = STARTPOS['flyer'] # Replaces in Menu
            START.flyer.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                        MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.flyer.rect.topleft = STARTPOS['flyer']

class StartSmilyRobot(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.smily_robot:
            START.blank_box.rect.topleft = STARTPOS['smily_robot'] # Replaces in Menu
            START.smily_robot.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                              MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.smily_robot.rect.topleft = STARTPOS['smily_robot']

class StartSpring(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.spring:
            START.blank_box.rect.topleft = STARTPOS['spring'] # Replaces in Menu
            START.spring.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                         MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.spring.rect.topleft = STARTPOS['spring']

class StartPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.player and not PLACED.player_list:
            START.blank_box.rect.topleft = STARTPOS['player'] # Replaces in Menu
            START.player.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                         MOUSEPOS[1]-(self.image.get_height()/3))
        else:
            START.player.rect.topleft = STARTPOS['player']

class StartStickyBlock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.sticky_block:
            START.blank_box.rect.topleft = STARTPOS['sticky_block'] # Replaces in Menu
            START.sticky_block.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                               MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.sticky_block.rect.topleft = STARTPOS['sticky_block']

class StartFallSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        if DRAGGING.fall_spikes:
            START.blank_box.rect.topleft = STARTPOS['fall_spikes'] # Replaces in Menu
            START.fall_spikes.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                              MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']

class StartStandSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
        self.rotate = 0
    def update(self):
        if self.rotate == 0:
            self.image = IMAGES["SPR_STANDSPIKES"]
        else:
            self.image = pygame.transform.rotate(IMAGES["SPR_STANDSPIKES"], self.rotate)
        if DRAGGING.stand_spikes:
            START.blank_box.rect.topleft = STARTPOS['stand_spikes'] # Replaces in Menu
            START.stand_spikes.rect.topleft = (MOUSEPOS[0]-(self.image.get_width()/2),
                                               MOUSEPOS[1]-(self.image.get_height()/2))
        else:
            START.stand_spikes.rect.topleft = STARTPOS['stand_spikes']

class PlacedWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedReverseWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_REVERSE_WALL"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayReverseWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedDiamonds(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayDiamonds(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedDoor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DOOR"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayDoor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DOOR"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)
        elif PLAY_SWITCH_BUTTON.play_switch:
            if PLAY.player_list[0].score == len(PLAY.diamonds_list):
                PLAY.door_list[0].image = IMAGES["SPR_DOOR_OPEN"]
            elif PLAY.player_list[0].score != len(PLAY.diamonds_list):
                PLAY.door_list[0].image = IMAGES["SPR_DOOR"]

class PlacedFlyer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayFlyer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.right_or_left = random.choice([-2, 2])
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch:
            self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
            for wall in PLAY.wall_list:
                if self.rect.colliderect(wall.rect):
                    self.right_or_left = self.right_or_left*-1
            for reverse_wall in PLAY.reverse_wall_list:
                if self.rect.colliderect(reverse_wall.rect):
                    self.right_or_left = self.right_or_left*-1
            if self.rect.right > SCREENWIDTH or self.rect.left < 0:
                self.right_or_left = self.right_or_left*-1
            self.sprite_direction()
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)
    def sprite_direction(self):
        if self.right_or_left == 2:
            self.image = IMAGES["SPR_FLYER"]
        elif self.right_or_left == -2:
            self.image = pygame.transform.flip(IMAGES["SPR_FLYER"], 1, 0)

class PlacedSmilyRobot(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlaySmilyRobot(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.right_or_left = random.choice([-2, 2])
        self.animatetimer = 0
        self.speed_y = 0
        self.jumps_left = 1
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch:
            if self.rect.topleft != (0, -100): # This is its out of play location
                self.animate()
                self.calc_grav()
                self.wall_hit_list = pygame.sprite.spritecollide(self, PLAY.wall_list, False)
                for wall in self.wall_hit_list:
                    if(self.rect.right-wall.rect.left < 5 and
                       self.right_or_left == 2): # Robot moves right and collides into wall
                        self.rect.right = wall.rect.left
                        self.right_or_left = -2
                    elif(wall.rect.right-self.rect.left < 5 and
                         self.right_or_left == -2): # Robot moves left and collides into wall
                        self.rect.left = wall.rect.right
                        self.right_or_left = 2
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PLAY.sticky_block_list,
                                                                   False)
                for stickyblock in self.stickyblock_hit_list:
                    if(self.rect.right-stickyblock.rect.left < 5 and
                       self.right_or_left == 2): # Robot moves right and collides into wall
                        self.rect.right = stickyblock.rect.left
                        self.right_or_left = -2
                    elif(stickyblock.rect.right-self.rect.left < 5 and
                         self.right_or_left == -2): # Robot moves left and collides into wall
                        self.rect.left = stickyblock.rect.right
                        self.right_or_left = 2
                self.rect.y += self.speed_y
                self.wall_hit_list = pygame.sprite.spritecollide(self, PLAY.wall_list, False)
                for wall in self.wall_hit_list:
                    # Reset our position based on the top/bottom of the object.
                    if self.speed_y > 0:
                        self.rect.bottom = wall.rect.top # On top of the wall
                    elif self.speed_y < 0:
                        self.rect.top = wall.rect.bottom # Below the wall
                    # Stop our vertical movement
                    self.speed_y = 0
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PLAY.sticky_block_list,
                                                                   False)
                for stickyblock in self.stickyblock_hit_list:
                    # Reset our position based on the top/bottom of the object.
                    if self.speed_y > 0:
                        self.rect.bottom = stickyblock.rect.top # On top of the wall
                    elif self.speed_y < 0:
                        self.rect.top = stickyblock.rect.bottom # Below the wall
                    # Stop our vertical movement
                    self.speed_y = 0
                self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
                for reverse_wall in PLAY.reverse_wall_list:
                    if self.rect.colliderect(reverse_wall.rect):
                        self.right_or_left *= -1
                self.wall_hit_list = pygame.sprite.spritecollide(self, PLAY.wall_list, False)
                for wall in self.wall_hit_list:
                    if self.speed_y > 0:
                        self.rect.bottom = wall.rect.top # On top of the wall
                        self.jumps_left = 2
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PLAY.sticky_block_list,
                                                                   False)
                for stickyblock in self.stickyblock_hit_list:
                    if self.speed_y > 0:
                        self.rect.bottom = stickyblock.rect.top # On top of the wall
                        self.jumps_left = 2
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)
    def animate(self):
        # Two different pictures to animate that makes it look like it's moving
        self.animatetimer += 1
        if self.animatetimer > 5:
            self.image = IMAGES["SPR_SMILYROBOT2"]
        if self.animatetimer > 10:
            self.image = IMAGES["SPR_SMILYROBOT"]
            self.animatetimer = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .25

class PlacedSpring(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlaySpring(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedStickyBlock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayStickyBlock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedFallSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlacedStandSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass

class PlayFallSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.fall_var = 0
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)
        elif PLAY_SWITCH_BUTTON.play_switch is not None:
            if(PLAY.player_list[0].rect.right > self.rect.left and
               PLAY.player_list[0].rect.left < self.rect.right and
               PLAY.player_list[0].rect.top > self.rect.bottom):
                self.fall_var = 1
            if self.fall_var == 1:
                self.rect.top = self.rect.top + 5

class PlayStandSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.fall_var = 0
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAY_SPRITES.remove(self)

class PlacedPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
    def update(self):
        pass
    def move_to_coord(self, coord):
        self.rect.topleft = coord
        

class PlayPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        self.rect.topleft = PLACED.player_list[0].rect.topleft
        PLAYER_SPRITES.add(self)
        self.speed_x, self.speed_y = 0, 0
        self.jumps_left = 1
        self.propeller, self.playerproptimer = 0, 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count = 0
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
    def update(self):
        if PLAY_SWITCH_BUTTON.play_switch is None:
            PLAYER_SPRITES.remove(self)
        self.calc_grav()
        self.rect.x += self.speed_x
        self.wall_hit_list = pygame.sprite.spritecollide(self, PLAY.wall_list, False)
        for wall in self.wall_hit_list:
            if self.speed_x > 0: #player moves right and collides into wall
                self.rect.right = wall.rect.left
            elif self.speed_x < 0: #player moves left and collides into wall
                self.rect.left = wall.rect.right
        self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PLAY.sticky_block_list, False)
        for stickyblock in self.stickyblock_hit_list:
            if self.speed_x > 0: #player moves right and collides into wall
                self.rect.right = stickyblock.rect.left
            elif self.speed_x < 0: #player moves left and collides into wall
                self.rect.left = stickyblock.rect.right
        self.rect.y += self.speed_y
        # Check and see if we hit anything
        self.wall_hit_list = pygame.sprite.spritecollide(self, PLAY.wall_list, False)
        for wall in self.wall_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speed_y > 0:
                self.rect.bottom = wall.rect.top #On top of the wall
                self.jumps_left = 2
            elif self.speed_y < 0:
                self.rect.top = wall.rect.bottom #Below the wall
            # Stop our vertical movement
            self.speed_y = 0
            self.propeller = 0
        self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PLAY.sticky_block_list, False)
        for stickyblock in self.stickyblock_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speed_y > 0:
                self.rect.bottom = stickyblock.rect.top #On top
                self.jumps_left = 2
            elif self.speed_y < 0:
                self.rect.top = stickyblock.rect.bottom #Below
            # Stop our vertical movement
            self.speed_y = 0
            self.propeller = 0
        for spring in PLAY.spring_list:
            if pygame.sprite.collide_mask(self, spring):
                if self.rect.bottom <= spring.rect.top+20 and self.speed_y >= 10: #big jumps
                    SOUNDS["SND_SPRING"].play()
                    self.propeller = 0 #Fixes propeller bug
                    self.rect.bottom = spring.rect.top
                    self.speed_y = -10
                    self.jumps_left = 1 #Allows propeller in air
                elif self.rect.bottom <= spring.rect.top+10 and self.speed_y >= 0:
                    SOUNDS["SND_SPRING"].play()
                    self.propeller = 0 #Fixes propeller bug
                    self.rect.bottom = spring.rect.top
                    self.speed_y = -10
                    self.jumps_left = 1 #Allows propeller in air
                elif self.speed_x > 0:
                    self.rect.right = spring.rect.left
                elif self.speed_x < 0:
                    self.rect.left = spring.rect.right
                elif self.speed_y < 0:
                    self.speed_y = 0
                    self.propeller = 0
                    self.rect.top = spring.rect.bottom #Below the wall
        self.animate_images()
        if self.rect.top > SCREENHEIGHT and self.speed_y >= 0:
            self.char_restart_level()
        self.enemy_collisions()
        if PLAY.door_list:
            if pygame.sprite.collide_mask(self, PLAY.door_list[0]):
                if self.score == len(PLAY.diamonds_list):
                    print("You Win!")
                    self.death_count = 0
                    PLAY_SWITCH_BUTTON.play_switch = None
                    #music_player = [MusicPlayer()]
                    self.rect.topleft = PLACED.player_list[0].rect.topleft
                    for i in range(0, len(PLACED.smily_robot_list)):
                        PLAY.smily_robot_list[i].rect.topleft = PLACED.smily_robot_list[i].rect.topleft
                        PLAY.smily_robot_list[i].speed_y = 0
                    for i in range(0, len(PLACED.flyer_list)):
                        PLAY.flyer_list[i].rect.topleft = PLACED.flyer_list[i].rect.topleft
                    for play_diamonds in PLAY.diamonds_list:
                        play_diamonds.image = IMAGES["SPR_DIAMONDS"]
                    for i in range(0, len(PLACED.fall_spikes_list)):
                        PLAY.fall_spikes_list[i].rect.topleft = PLACED.fall_spikes_list[i].rect.topleft
                        PLAY.fall_spikes_list[i].fall_var = 0
                    #All Play objects removed
                    PLAY.play_none()
    def go_left(self):
        self.speed_x = -4
    def go_right(self):
        self.speed_x = 4
    def stop(self):
        self.speed_x = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        elif self.propeller == 1:
            self.speed_y += .01
            if self.speed_y >= -2:
                SOUNDS["SND_PROPELLER"].play()
            if self.speed_y > -1.5:
                self.propeller = 0
                self.speed_y += .25
        else:
            SOUNDS["SND_PROPELLER"].stop()
            self.speed_y += .25
    def jump(self):
        # For moving platforms that go up and down...
        self.speed_y += 2
        self.speed_y -= 2
        # If there is a platform below you, you are able to jump
        if self.wall_hit_list and self.jumps_left == 2: #Big First Jump
            self.speed_y = -7
            self.jumps_left = 1
        elif self.stickyblock_hit_list and self.jumps_left >= 1: #Sticky --> No Jump
            self.jumps_left = 0
        elif not self.wall_hit_list and self.jumps_left >= 1: #Double Jump when not on platform
            self.speed_y = -2
            self.propeller = 1
            self.jumps_left = 0
        elif not self.wall_hit_list: #If Player is not on top of wall, he only has propeller left
            if self.jumps_left == 2:
                self.jumps_left = 1
    def animate_images(self):
        if self.propeller == 1:
            self.playerproptimer += 1
            if self.last_pressed_r == 1:
                if self.playerproptimer > 1:
                    self.image = IMAGES["SPR_PLAYER_PROP"]
                if self.playerproptimer > 3:
                    self.image = IMAGES["SPR_PLAYER"]
                    self.playerproptimer = 0
            if self.last_pressed_r == 0:
                if self.playerproptimer > 1:
                    self.image = pygame.transform.flip(IMAGES["SPR_PLAYER_PROP"], 1, 0)
                if self.playerproptimer > 3:
                    self.image = pygame.transform.flip(IMAGES["SPR_PLAYER"], 1, 0)
                    self.playerproptimer = 0
        else:
            if self.last_pressed_r == 1:
                self.image = IMAGES["SPR_PLAYER"]
            else:
                self.image = pygame.transform.flip(IMAGES["SPR_PLAYER"], 1, 0)
    def enemy_collisions(self):
        for play_smily_robot in PLAY.smily_robot_list:
            if self.rect.colliderect(play_smily_robot.rect):
                if(self.rect.bottom <= play_smily_robot.rect.top + 10 and self.speed_y >= 0):
                    play_smily_robot.rect.topleft = (0, -100)
                    self.propeller = 0 #Fixes propeller bug
                    self.speed_y = -4
                    self.jumps_left = 1 #Allows propeller in air
                elif(self.rect.right-play_smily_robot.rect.left <= 10 and
                     self.rect.bottom > play_smily_robot.rect.top + 10):
                    self.char_restart_level()
                elif(self.rect.left-play_smily_robot.rect.right <= 10 and
                     self.rect.bottom > play_smily_robot.rect.top + 10):
                    self.char_restart_level()
        for play_flyer in PLAY.flyer_list:
            if self.rect.colliderect(play_flyer.rect):
                self.char_restart_level()
        for play_fall_spikes in PLAY.fall_spikes_list:
            if self.rect.colliderect(play_fall_spikes.rect):
                self.char_restart_level()
        for play_stand_spikes in PLAY.stand_spikes_list:
            if self.rect.colliderect(play_stand_spikes.rect):
                self.char_restart_level()
        for play_diamonds in PLAY.diamonds_list:
            if pygame.sprite.collide_mask(self, play_diamonds):
                self.score += 1
                play_diamonds.image = IMAGES["SPR_BLANKBOX"]
    def char_restart_level(self):
        # Game Reset
        self.jumps_left = 1
        self.speed_y = 0
        self.propeller = 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count += 1
        #Reset Locations
        self.rect.topleft = PLACED.player_list[0].rect.topleft
        for i in range(0, len(PLACED.smily_robot_list)):
            PLAY.smily_robot_list[i].rect.topleft = PLACED.smily_robot_list[i].rect.topleft
            PLAY.smily_robot_list[i].speed_y = 0
            PLAY.smily_robot_list[i].right_or_left = random.choice([-2, 2])
        for i in range(0, len(PLACED.flyer_list)):
            PLAY.flyer_list[i].rect.topleft = PLACED.flyer_list[i].rect.topleft
            PLAY.flyer_list[i].right_or_left = random.choice([-2, 2])
        for play_diamonds in PLAY.diamonds_list:
            play_diamonds.image = IMAGES["SPR_DIAMONDS"]
        for i in range(0, len(PLACED.fall_spikes_list)):
            PLAY.fall_spikes_list[i].rect.topleft = PLACED.fall_spikes_list[i].rect.topleft
            PLAY.fall_spikes_list[i].fall_var = 0

class PlaySwitchButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAY_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self) #Play button only available when NOT in-play
        self.play_switch = None
    def update(self):
        if self.play_switch is None:
            PLAY_SPRITES.remove(self)
            self.image = IMAGES["SPR_PLAY_BUTTON"]
            START_SPRITES.add(self)
        elif self.play_switch is not None:
            START_SPRITES.remove(self)
            self.image = IMAGES["SPR_STOP_BUTTON"]
            PLAY_SPRITES.add(self)

class MusicPlayer():
    def __init__(self):
        if PLAY_SWITCH_BUTTON.play_switch:
            pygame.mixer.music.load("sounds/playmusic.mp3")
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load("sounds/editingmode.wav")
            pygame.mixer.music.play(-1)

class Grid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID"]
        self.rect = self.image.get_rect()
        GRID_SPRITES.add(self)
    def update(self):
        if self.rect.bottom > SCREENHEIGHT:
            START_SPRITES.remove(self)
        if self.rect.right > SCREENWIDTH:
            START_SPRITES.remove(self)

class ClearButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_CLEAR_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class InfoButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_INFO_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class RestartButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_RESTART_BUTTON"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        pass

class GridButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
        self.grid_on_var = 1
    def update(self):
        pass

class ColorButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_COLOR_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class RotateButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_ROTATE_BUTTON"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass

class Dragging():
    def __init__(self):
        self.player = None
        self.wall = None
        self.flyer = None
        self.reverse_wall = None
        self.spring = None
        self.smily_robot = None
        self.door = None
        self.diamonds = None
        self.sticky_block = None
        self.fall_spikes = None
        self.stand_spikes = None
    def dragging_none(self):
        self.player = None
        self.wall = None
        self.flyer = None
        self.reverse_wall = None
        self.spring = None
        self.smily_robot = None
        self.door = None
        self.diamonds = None
        self.sticky_block = None
        self.fall_spikes = None
        self.stand_spikes = None

class Start():
    def __init__(self):
        self.blank_box = StartBlankBox()
        self.player = StartPlayer()
        self.wall = StartWall()
        self.flyer = StartFlyer()
        self.reverse_wall = StartReverseWall()
        self.spring = StartSpring()
        self.smily_robot = StartSmilyRobot()
        self.door = StartDoor()
        self.diamonds = StartDiamonds()
        self.sticky_block = StartStickyBlock()
        self.fall_spikes = StartFallSpikes()
        self.stand_spikes = StartStandSpikes()

class Placed():
    def __init__(self):
        self.player_list = []
        self.wall_list = []
        self.flyer_list = []
        self.reverse_wall_list = []
        self.spring_list = []
        self.smily_robot_list = []
        self.door_list = []
        self.diamonds_list = []
        self.sticky_block_list = []
        self.fall_spikes_list = []
        self.stand_spikes_list = []
        self.get_rect_for_all_obj = {}
        self.total_placed_list = self.refresh_total_placed_list()
        
    # Returns the tuples of each objects' positions within all classes
    def get_dict_rect_positions(self):
        self.get_rect_for_all_obj = dict.fromkeys(self.total_placed_list, list)
        for item_key, item_list in self.total_placed_list.items():
            item_list_in_name = []
            for item_rect in item_list:
                item_list_in_name.append(item_rect.rect.topleft)
            self.get_rect_for_all_obj[item_key] = item_list_in_name
        return self.get_rect_for_all_obj
    def refresh_total_placed_list(self):
        self.total_placed_list = {'player': self.player_list, 'door': self.door_list, 
                                  'wall': self.wall_list, 'flyer': self.flyer_list, 
                                  'reverse_wall': self.reverse_wall_list,
                                  'spring': self.spring_list, 'smily_robot': self.smily_robot_list,
                                  'diamonds': self.diamonds_list, 'sticky_block': self.sticky_block_list,
                                  'fall_spikes': self.fall_spikes_list, 'stand_spikes': self.stand_spikes_list}
        return self.total_placed_list
    def remove_all(self):
        for spr_list in [self.player_list, self.wall_list, self.flyer_list,
                         self.reverse_wall_list, self.spring_list, self.smily_robot_list,
                         self.door_list, self.diamonds_list, self.sticky_block_list,
                         self.fall_spikes_list, self.stand_spikes_list]:
            for obj in spr_list:
                obj.kill()
        self.player_list = []
        self.wall_list = []
        self.flyer_list = []
        self.reverse_wall_list = []
        self.spring_list = []
        self.smily_robot_list = []
        self.door_list = []
        self.diamonds_list = []
        self.sticky_block_list = []
        self.fall_spikes_list = []
        self.stand_spikes_list = []
        self.total_placed_list = self.refresh_total_placed_list()

        


class Play():
    def __init__(self):
        self.player_list = []
        self.wall_list = []
        self.flyer_list = []
        self.reverse_wall_list = []
        self.spring_list = []
        self.smily_robot_list = []
        self.door_list = []
        self.diamonds_list = []
        self.sticky_block_list = []
        self.fall_spikes_list = []
        self.stand_spikes_list = []
    def play_none(self):
        self.player_list = []
        self.wall_list = []
        self.flyer_list = []
        self.reverse_wall_list = []
        self.spring_list = []
        self.smily_robot_list = []
        self.door_list = []
        self.diamonds_list = []
        self.sticky_block_list = []
        self.fall_spikes_list = []
        self.stand_spikes_list = []

class Room():
    def __init__(self):
        #Start Objects
        START.player.rect.topleft = STARTPOS['player']
        START.wall.rect.topleft = STARTPOS['wall']
        START.flyer.rect.topleft = STARTPOS['flyer']
        START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']
        START.spring.rect.topleft = STARTPOS['spring']
        START.smily_robot.rect.topleft = STARTPOS['smily_robot']
        START.door.rect.topleft = STARTPOS['door']
        START.diamonds.rect.topleft = STARTPOS['diamonds']
        START.sticky_block.rect.topleft = STARTPOS['sticky_block']
        START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']
        START.stand_spikes.rect.topleft = STARTPOS['stand_spikes']
        #Play and Stop Buttons
        PLAY_SWITCH_BUTTON.rect.topleft = (SCREENWIDTH-50, 8)
        CLEAR_BUTTON.rect.topleft = (SCREENWIDTH-115, 10)
        GRID_BUTTON.rect.topleft = (SCREENWIDTH-150, 10)
        RESTART_BUTTON.rect.topleft = (SCREENWIDTH-175, 10)
        COLOR_BUTTON.rect.topleft = (SCREENWIDTH-195, 10)
        SAVE_FILE_BUTTON.rect.topleft = (SCREENWIDTH-230, 10)
        LOAD_FILE_BUTTON.rect.topleft = (SCREENWIDTH-265, 10)
        INFO_BUTTON.rect.topleft = (SCREENWIDTH-320, 10)
        ROTATE_BUTTON.rect.topleft = (SCREENWIDTH-590, 7)
        for i in range(0, SCREENWIDTH, 24):
            for j in range(48, SCREENHEIGHT, 24):
                grid = Grid()
                grid.rect.topleft = i, j



#Init
pygame.init()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #, pygame.FULLSCREEN for fullSCREEN
#Fonts
FONT_ARIAL = pygame.font.SysFont('Arial', 24)
#Sprites
load_image("sprites/blankbox.png", "SPR_BLANKBOX", True, False)
load_image("sprites/doorclosed.png", "SPR_DOOR", True, True)
load_image("sprites/dooropen.png", "SPR_DOOR_OPEN", True, True)
load_image("sprites/diamond.png", "SPR_DIAMONDS", True, True)
load_image("sprites/Wall.png", "SPR_WALL", True, True)
load_image("sprites/reversewall.png", "SPR_REVERSE_WALL", True, True)
load_image("sprites/flyer.png", "SPR_FLYER", True, True)
load_image("sprites/spring.png", "SPR_SPRING", True, True)
load_image("sprites/smilyrobot1.png", "SPR_SMILYROBOT", True, True)
load_image("sprites/smilyrobot2.png", "SPR_SMILYROBOT2", True, True)
load_image("sprites/stickyblock.png", "SPR_STICKYBLOCK", True, True)
load_image("sprites/fallspikes.png", "SPR_FALLSPIKES", True, True)
load_image("sprites/standspikes.png", "SPR_STANDSPIKES", True, True)
load_image("sprites/player.png", "SPR_PLAYER", True, True)
load_image("sprites/playerprop.png", "SPR_PLAYER_PROP", True, True)
load_image("sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
load_image("sprites/stopbutton.png", "SPR_STOP_BUTTON", True, True)
load_image("sprites/clear.png", "SPR_CLEAR_BUTTON", True, True)
load_image("sprites/infobutton.png", "SPR_INFO_BUTTON", True, True)
load_image("sprites/gridbutton.png", "SPR_GRID_BUTTON", True, True)
load_image("sprites/restart.png", "SPR_RESTART_BUTTON", True, True)
load_image("sprites/colorbutton.png", "SPR_COLOR_BUTTON", True, True)
load_image("sprites/savefile.png", "SPR_SAVE_FILE_BUTTON", True, True)
load_image("sprites/loadfile.png", "SPR_LOAD_FILE_BUTTON", True, True)
load_image("sprites/rotate.png", "SPR_ROTATE_BUTTON", True, True)
load_image("sprites/grid.png", "SPR_GRID", True, True)

#Backgrounds
START_MENU = pygame.image.load("sprites/startmenu.png").convert()
START_MENU = pygame.transform.scale(START_MENU, (SCREENWIDTH, SCREENHEIGHT))
INFO_SCREEN = pygame.image.load("sprites/infoSCREEN.bmp").convert()
INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREENWIDTH, SCREENHEIGHT))

#Start (Menu) Objects
START = Start()
#Placed Lists
PLACED = Placed()
#List of Play Objects (Start out empty until placed somewhere and play_switch is not None)
PLAY = Play()
#Dragging Variables
DRAGGING = Dragging()
#Play and Stop Buttons

PLAY_SWITCH_BUTTON = PlaySwitchButton()
CLEAR_BUTTON = ClearButton()
INFO_BUTTON = InfoButton()
GRID_BUTTON = GridButton()
RESTART_BUTTON = RestartButton()
COLOR_BUTTON = ColorButton()
SAVE_FILE_BUTTON = SaveFileButton()
LOAD_FILE_BUTTON = LoadFileButton()
ROTATE_BUTTON = RotateButton()

#window
GAME_ICON = pygame.image.load("sprites/playerico.png")
pygame.display.set_icon(GAME_ICON)
pygame.display.set_caption('Level Editor')
#sounds
load_sound("sounds/propeller.wav", "SND_PROPELLER")
SOUNDS["SND_PROPELLER"].set_volume(.15)
load_sound("sounds/spring.wav", "SND_SPRING")
SOUNDS["SND_SPRING"].set_volume(.15)
#MUSIC_PLAYER = [MusicPlayer()]
#Main
while RUNNING:
    CLOCK.tick(60)
    MOUSEPOS = pygame.mouse.get_pos()
    
    if MENUON == 0: # Initiate room
        ROOM = Room()
        MENUON = 1 # No initiation
    if MENUON == 2: # Info SCREEN
        MENUON = InfoScreen(SCREEN)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                MENUON = 1 #Getting out of menus
        if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
           MOUSEPOS[1] < 48): #DRAG (only for menu and inanimate buttons at top)
            if PLAY_SWITCH_BUTTON.play_switch is None: #Checks if in Editing Mode
                #BUTTONS
                if GRID_BUTTON.rect.collidepoint(MOUSEPOS):
                    if GRID_BUTTON.grid_on_var == 1:
                        GRID_BUTTON.grid_on_var = 0
                    else:
                        GRID_BUTTON.grid_on_var = 1
                if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                    get_color()
                if SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                    save_file(COLORKEY)
                if LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                    COLORKEY = load_file(COLORKEY)
                #DRAG OBJECTS
                if START.player.rect.collidepoint(MOUSEPOS): #Try to drag player from menu
                    #Checks for if there is already a player placed on level
                    if not PLACED.player_list:
                        dragging_function()
                        DRAGGING.player = not None
                    else:
                        print("Error: Too many players")
                elif START.door.rect.collidepoint(MOUSEPOS):
                    if not PLACED.door_list:
                        dragging_function()
                        DRAGGING.door = not None
                    else:
                        print("Error: Only one exit allowed")
                elif START.wall.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.wall = not None
                elif START.flyer.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.flyer = not None
                elif START.reverse_wall.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.reverse_wall = not None
                elif START.spring.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.spring = not None
                elif START.smily_robot.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.smily_robot = not None
                elif START.diamonds.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.diamonds = not None
                elif START.sticky_block.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.sticky_block = not None
                elif START.fall_spikes.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.fall_spikes = not None
                elif START.stand_spikes.rect.collidepoint(MOUSEPOS):
                    dragging_function()
                    DRAGGING.stand_spikes = not None
        elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            #placedObject placed on location of mouse release
            def drag_to_placed(drag, placed_class, placed_list):
                if pygame.mouse.get_pressed()[0] and drag is not None:
                    remove_object() #Remove what is already there
                    placedobj = placed_class()
                    placedobj.rect.topleft = snap_to_grid(MOUSEPOS)
                    if placed_list is PLACED.stand_spikes_list:
                        placedobj.image = START.stand_spikes.image
                    PLACED_SPRITES.add(placedobj)
                    placed_list.append(placedobj)
            if not PLACED.player_list:
                drag_to_placed(DRAGGING.player, PlacedPlayer, PLACED.player_list)
            if not PLACED.door_list:
                drag_to_placed(DRAGGING.door, PlacedDoor, PLACED.door_list)
            drag_to_placed(DRAGGING.wall, PlacedWall, PLACED.wall_list)
            drag_to_placed(DRAGGING.flyer, PlacedFlyer, PLACED.flyer_list)
            drag_to_placed(DRAGGING.reverse_wall, PlacedReverseWall, PLACED.reverse_wall_list)
            drag_to_placed(DRAGGING.spring, PlacedSpring, PLACED.spring_list)
            drag_to_placed(DRAGGING.smily_robot, PlacedSmilyRobot, PLACED.smily_robot_list)
            drag_to_placed(DRAGGING.diamonds, PlacedDiamonds, PLACED.diamonds_list)
            drag_to_placed(DRAGGING.sticky_block, PlacedStickyBlock, PLACED.sticky_block_list)
            drag_to_placed(DRAGGING.fall_spikes, PlacedFallSpikes, PLACED.fall_spikes_list)
            drag_to_placed(DRAGGING.stand_spikes, PlacedStandSpikes, PLACED.stand_spikes_list)
        if event.type == MOUSEBUTTONUP: # Release Drag
            if(PLAY_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and
               # LEFT CLICK PLAY BUTTON
               PLAY_SWITCH_BUTTON.play_switch is None):
                # Makes sure there is at least one player to play game
                if PLACED.player_list:
                    # Makes clicking play again unclickable
                    if PLAY_SWITCH_BUTTON.play_switch is None:
                        print("Play Mode Activated")
                        PLAY_SWITCH_BUTTON.play_switch = not None
                        #MUSIC_PLAYER = [MusicPlayer()]
                        def placed_to_play(placed_list, play_list, play_class):
                            if placed_list is not None:
                                for i, placed_obj in enumerate(placed_list):
                                    # Adds to list same amount of PlayWalls as PlaceWalls
                                    play_list.append(play_class())
                                    # Each PlayWall in respective PlacedWall location
                                    play_list[i].rect.topleft = placed_obj.rect.topleft
                                    # Change play list image only for rotated spikes
                                    if play_list is PLAY.stand_spikes_list:
                                        play_list[i].image = placed_obj.image
                        placed_to_play(PLACED.player_list, PLAY.player_list, PlayPlayer)
                        placed_to_play(PLACED.door_list, PLAY.door_list, PlayDoor)
                        placed_to_play(PLACED.wall_list, PLAY.wall_list, PlayWall)
                        placed_to_play(PLACED.flyer_list, PLAY.flyer_list, PlayFlyer)
                        placed_to_play(PLACED.reverse_wall_list, PLAY.reverse_wall_list,
                                       PlayReverseWall)
                        placed_to_play(PLACED.spring_list, PLAY.spring_list, PlaySpring)
                        placed_to_play(PLACED.smily_robot_list, PLAY.smily_robot_list,
                                       PlaySmilyRobot)
                        placed_to_play(PLACED.diamonds_list, PLAY.diamonds_list, PlayDiamonds)
                        placed_to_play(PLACED.sticky_block_list, PLAY.sticky_block_list,
                                       PlayStickyBlock)
                        placed_to_play(PLACED.fall_spikes_list, PLAY.fall_spikes_list,
                                       PlayFallSpikes)
                        placed_to_play(PLACED.stand_spikes_list, PLAY.stand_spikes_list,
                                       PlayStandSpikes)
                else:
                    print("You need a character!")
            # LEFT CLICK STOP BUTTON
            elif(PLAY_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and
                 PLAY_SWITCH_BUTTON.play_switch is not None):
                # Makes sure you are not in editing mode to enter editing mode
                if PLAY_SWITCH_BUTTON.play_switch is not None:
                    print("Editing Mode Activated")
                    PLAY.player_list[0].death_count = 0
                    PLAY_SWITCH_BUTTON.play_switch = None
                    #MUSIC_PLAYER = []
                    #MUSIC_PLAYER = [MusicPlayer()]
                    # All Play objects removed
                    PLAY.play_none()
            if RESTART_BUTTON.rect.collidepoint(MOUSEPOS):
                if PLAY_SWITCH_BUTTON.play_switch is not None:
                    PLAY.player_list[0].char_restart_level()
                    PLAY.player_list[0].death_count += 1
            if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                MENUON = 2
            if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                if PLAY_SWITCH_BUTTON.play_switch is None: #Editing mode
                    dragging_function()
                    # REMOVE ALL SPRITES
                    PLACED.remove_all()
            if ROTATE_BUTTON.rect.collidepoint(MOUSEPOS):
                START.stand_spikes.rotate -= 90
        if(event.type == MOUSEBUTTONDOWN and
           pygame.mouse.get_pressed()[2]): #Right click on obj, destroy
            if PLAY_SWITCH_BUTTON.play_switch is None: #Editing mode
                dragging_function()
                remove_object()
    # PLAYER MOVEMENTS
        if PLAY_SWITCH_BUTTON.play_switch is not None:
            if event.type == KEYUP:
                if event.key == pygame.K_LEFT and PLAY.player_list[0].speed_x < 0:
                    PLAY.player_list[0].stop()
                if event.key == pygame.K_RIGHT and PLAY.player_list[0].speed_x > 0:
                    PLAY.player_list[0].stop()
            if event.type == KEYDOWN:
                if event.key == pygame.K_UP:
                    if PLAY.player_list[0].jumps_left > 0:
                        PLAY.player_list[0].jump()
    # ALL GAME ACTIONS
    if PLAY_SWITCH_BUTTON.play_switch is not None:
        KEYS_PRESSED = pygame.key.get_pressed()
        if KEYS_PRESSED[K_LEFT]:
            PLAY.player_list[0].last_pressed_r = 0
            if PLAY.player_list[0].rect.left > 0:
                PLAY.player_list[0].go_left()
            else:
                PLAY.player_list[0].stop()
        if KEYS_PRESSED[K_RIGHT]:
            PLAY.player_list[0].last_pressed_r = 1
            if PLAY.player_list[0].rect.right < SCREENWIDTH:
                PLAY.player_list[0].go_right()
            else:
                PLAY.player_list[0].stop()
    #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
    
    SCREEN.fill(COLORKEY)
    
    #Update all sprites
    GRID_SPRITES.update()
    START_SPRITES.update()
    PLACED_SPRITES.update()
    PLAY_SPRITES.update()
    PLAYER_SPRITES.update()
    
    if PLAY_SWITCH_BUTTON.play_switch is None: #Only draw placed sprites in editing mode
        if GRID_BUTTON.grid_on_var == 1:
            GRID_SPRITES.draw(SCREEN)
        START_SPRITES.draw(SCREEN)
        PLACED_SPRITES.draw(SCREEN)
    elif PLAY_SWITCH_BUTTON.play_switch is not None: #Only draw play sprites in play mode
        PLAY_SPRITES.draw(SCREEN)
        PLAYER_SPRITES.draw(SCREEN)
    if PLAY_SWITCH_BUTTON.play_switch:
        DEATH_COUNT_TEXT = FONT_ARIAL.render("Deaths: " + str(PLAY.player_list[0].death_count), 1, (0, 0, 0))
    elif PLAY_SWITCH_BUTTON.play_switch is None:
        DEATH_COUNT_TEXT = FONT_ARIAL.render("", 1, (0, 0, 0))
    SCREEN.blit(DEATH_COUNT_TEXT, ((SCREENWIDTH/2-50), 5))
    
    pygame.display.flip()
    pygame.display.update()
