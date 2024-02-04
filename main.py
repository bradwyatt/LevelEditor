"""
Propeller Platformer: Level Editor created by Brad Wyatt
"""
import random
import sys
import os
import copy
#import tkinter as tk
#from tkinter.colorchooser import askcolor
#from tkinter.filedialog import asksaveasfilename, askopenfilename
from ast import literal_eval
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, IMAGES, SOUNDS, load_image, load_sound
from ui import ClearButton, InfoButton, RestartButton, GridButton, ColorButton, SaveFileButton, LoadFileButton
from start_objects import StartWall, StartReverseWall, StartDiamonds, StartDoor, StartFlyer, StartSmilyRobot, StartSpring, StartPlayer, StartStickyBlock, StartFallSpikes, StartStandSpikes, RotateButton
from placed_objects import PlacedWall, PlacedReverseWall, PlacedDiamonds, PlacedDoor, PlacedFlyer, PlacedSmilyRobot, PlacedSpring, PlacedStickyBlock, PlacedFallSpikes, PlacedStandSpikes, PlacedPlayer
from play_objects import PlayWall, PlayReverseWall, PlayFlyer, PlayDiamonds, PlayDoor, PlaySmilyRobot, PlayStickyBlock, PlayStandSpikes, PlayFallSpikes, PlaySpring, PlayPlayer

# Initialize pygame
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # pygame.FULLSCREEN for fullSCREEN
GAME_ICON = pygame.image.load("sprites/player_ico.png")
pygame.display.set_icon(GAME_ICON)
pygame.display.set_caption('Level Editor')
clock = pygame.time.Clock()

GRID_SPRITES = pygame.sprite.Group()
START_SPRITES = pygame.sprite.Group()
PLAY_SPRITES = pygame.sprite.Group()
GAME_MODE_SPRITES = pygame.sprite.Group()
PLACED_SPRITES = pygame.sprite.Group()

########################
# GLOBAL CONSTANTS and MUTABLES
# Starting positions of each of the objects
########################
START_POSITIONS = {'player': (10, 4), 'wall': (40, 12), 'reverse_wall': (102, 12),
            'spring': (255, 12), 'flyer': (130, 12), 'smily_robot': (162, 12),
            'door': (195, 2), 'diamonds': (225, 14), 'sticky_block': (70, 12),
            'fall_spikes': (290, 12), 'stand_spikes': (320, 12)}

def create_transparent_surface(width, height):
    """
    Creates a transparent surface of the specified size.
    :param width: Width of the surface.
    :param height: Height of the surface.
    :return: A transparent surface.
    """
    transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    transparent_surface.fill((0, 0, 0, 0))  # Fill with complete transparency
    return transparent_surface

def load_all_assets():
    #Sprites
    IMAGES['spr_blank_box'] = create_transparent_surface(24, 24)  # Assuming 24x24 is the size for blank box
    load_image("sprites/door_closed.png", "spr_door_closed", True)
    load_image("sprites/door_open.png", "spr_door_open", True)
    load_image("sprites/diamond.png", "spr_diamonds", True)
    load_image("sprites/wall.png", "spr_wall", True)
    load_image("sprites/reverse_wall.png", "spr_reverse_wall", True)
    load_image("sprites/flyer.png", "spr_flyer", True)
    load_image("sprites/spring.png", "spr_spring", True)
    load_image("sprites/smily_robot_1.png", "spr_smily_robot", True)
    load_image("sprites/smily_robot_2.png", "spr_smily_robot_2", True)
    load_image("sprites/sticky_block.png", "spr_sticky_block", True)
    load_image("sprites/fall_spikes.png", "spr_fall_spikes", True)
    load_image("sprites/stand_spikes.png", "spr_stand_spikes", True)
    load_image("sprites/player.png", "spr_player", True)
    load_image("sprites/player_propeller.png", "spr_player_propeller", True)
    load_image("sprites/play_button.png", "spr_play_button", True)
    load_image("sprites/stop_button.png", "spr_stop_button", True)
    load_image("sprites/clear.png", "spr_clear_button", True)
    load_image("sprites/info_button.png", "spr_info_button", True)
    load_image("sprites/grid_button.png", "spr_grid_button", True)
    load_image("sprites/restart.png", "spr_restart_button", True)
    load_image("sprites/color_button.png", "spr_color_button", True)
    load_image("sprites/save_file.png", "spr_save_file_button", True)
    load_image("sprites/load_file.png", "spr_load_file_button", True)
    load_image("sprites/rotate.png", "spr_rotate_button", True)
    load_image("sprites/grid.png", "spr_grid", True)
    
    #SOUNDS
    load_sound("sounds/propeller.wav", "snd_propeller")
    SOUNDS["snd_propeller"].set_volume(.15)
    load_sound("sounds/spring.wav", "snd_spring")
    SOUNDS["snd_spring"].set_volume(.15)

def snap_to_grid(pos, screen_width, screen_height):
    best_num_x, best_num_y = 0, 48 # Y is 48 so it doesn't go above the menu
    for x_coord in range(0, screen_width, 24):
        if pos[0]-x_coord <= 24 and pos[0]-x_coord >= 0:
            best_num_x = x_coord
    for y_coord in range(48, screen_height, 24):
        if pos[1]-y_coord <= 24 and pos[1]-y_coord >= 0:
            best_num_y = y_coord
    return (best_num_x, best_num_y)

def remove_placed_object(placed_sprites, mousepos):
    for placed_item_list in (PlacedPlayer.player_list, PlacedWall.wall_list, PlacedFlyer.flyer_list,
                             PlacedSpring.spring_list, PlacedDiamonds.diamonds_list, PlacedReverseWall.reverse_wall_list,
                             PlacedSmilyRobot.smily_robot_list, PlacedDoor.door_list, PlacedStickyBlock.sticky_block_list,
                             PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mousepos):
                placed_sprites.remove(placed_item)
                placed_item_list.remove(placed_item)
    return placed_sprites

def restart_start_objects(start, start_positions):
    start.player.rect.topleft = start_positions['player']
    start.wall.rect.topleft = start_positions['wall']
    start.reverse_wall.rect.topleft = start_positions['reverse_wall']
    start.spring.rect.topleft = start_positions['spring']
    start.flyer.rect.topleft = start_positions['flyer']
    start.smily_robot.rect.topleft = start_positions['smily_robot']
    start.door.rect.topleft = start_positions['door']
    start.diamonds.rect.topleft = start_positions['diamonds']
    start.sticky_block.rect.topleft = start_positions['sticky_block']
    start.fall_spikes.rect.topleft = start_positions['fall_spikes']
    start.fall_spikes.rect.topleft = start_positions['stand_spikes']
    return start

# def get_color():
#     color = askcolor()
#     return [color[0][0], color[0][1], color[0][2]]

# def load_file(PLACED_SPRITES, colorkey):
#     request_file_name = askopenfilename(defaultextension=".lvl")
#     open_file = open(request_file_name, "r")
#     loaded_file = open_file.read()
#     loaded_dict = literal_eval(loaded_file)
            
#     for player in PlayPlayer.player_list:
#         player.destroy()
#     for door in PlayDoor.door_list:
#         door.destroy()
#     for wall in PlayWall.wall_list:
#         wall.destroy()
#     for reverse_wall in PlayReverseWall.reverse_wall_list:
#         reverse_wall.destroy()
#     for flyer in PlayFlyer.flyer_list:
#         flyer.destroy()
#     for smily_robot in PlaySmilyRobot.smily_robot_list:
#         smily_robot.destroy()
#     for spring in PlaySpring.spring_list:
#         spring.destroy()
#     for diamond in PlayDiamonds.diamonds_list:
#         diamond.destroy()
#     for sticky_block in PlayStickyBlock.sticky_block_list:
#         sticky_block.destroy()
#     for fall_spikes in PlayFallSpikes.fall_spikes_list:
#         fall_spikes.destroy()
#     for stand_spikes in PlayStandSpikes.stand_spikes_list:
#         stand_spikes.destroy()
#     open_file.close()
    
#     # Removes all placed lists
#     remove_all_placed()
    
#     print("Removed all sprites. Now creating lists for loaded level.")
    
#     for player_pos in loaded_dict['player']:
#         PlacedPlayer(player_pos, PLACED_SPRITES)
#     for door_pos in loaded_dict['door']:
#         PlacedDoor(door_pos, PLACED_SPRITES)
#     for wall_pos in loaded_dict['wall']:
#         PlacedWall(wall_pos, PLACED_SPRITES)
#     for reverse_wall_pos in loaded_dict['reverse_wall']:
#         PlacedReverseWall(reverse_wall_pos, PLACED_SPRITES)
#     for flyer_pos in loaded_dict['flyer']:
#         PlacedFlyer(flyer_pos, PLACED_SPRITES)
#     for smily_robot_pos in loaded_dict['smily_robot']:
#         PlacedSmilyRobot(smily_robot_pos, PLACED_SPRITES)
#     for spring_pos in loaded_dict['spring']:
#         PlacedSpring(spring_pos, PLACED_SPRITES)
#     for diamond_pos in loaded_dict['diamonds']:
#         PlacedDiamonds(diamond_pos, PLACED_SPRITES)
#     for sticky_block_pos in loaded_dict['sticky_block']:
#         PlacedStickyBlock(sticky_block_pos, PLACED_SPRITES)
#     for fall_spikes_pos in loaded_dict['fall_spikes']:
#         PlacedFallSpikes(fall_spikes_pos, PLACED_SPRITES)
#     for stand_spikes_pos in loaded_dict['stand_spikes']:
#         PlacedStandSpikes(stand_spikes_pos, PLACED_SPRITES)
#     colorkey = loaded_dict['RGB']
    
#     print("File Loaded")
#     return PLACED_SPRITES, colorkey

# def save_file(colorkey):
#     try:
#         if PlacedPlayer.player_list and PlacedDoor.door_list:
#             # default extension is optional, here will add .txt if missing
#             save_file_prompt = asksaveasfilename(defaultextension=".lvl")
#             save_file_name = open(save_file_prompt, "w")
#             if save_file_name is not None:
#                 # Write the file to disk
#                 obj_locations = copy.deepcopy(get_dict_rect_positions())
#                 obj_locations['RGB'] = colorkey
#                 save_file_name.write(str(obj_locations))
#                 save_file_name.close()
#                 print("File Saved Successfully.")
#         else:
#             print("Error! Need player and door to save!")
#     except IOError:
#         print("Save File Error, please restart game and try again.")

class InfoScreen():
    def __init__(self, INFO_SCREEN, screen):
        self.screen = screen
        self.title = INFO_SCREEN
        self.clock = pygame.time.Clock()
        self.menuon = 2
        self.main_loop()

    def main_loop(self):
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
                        break


class StartBlankBox(pygame.sprite.Sprite):
    def __init__(self, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_blank_box"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass
    def flip_start_sprite(self, dragging, pos, images):
        self.rect.topleft = pos
        if dragging.player:
            self.image = images["spr_player"]
        elif dragging.wall:
            self.image = images["spr_wall"]
        elif dragging.diamonds:
            self.image = images["spr_diamonds"]
        elif dragging.door:
            self.image = pygame.transform.smoothscale(images["spr_door_closed"], (24, 40))
        elif dragging.flyer:
            self.image = images["spr_flyer"]
        elif dragging.reverse_wall:
            self.image = images["spr_reverse_wall"]
        elif dragging.smily_robot:
            self.image = images["spr_smily_robot"]
        elif dragging.spring:
            self.image = images["spr_spring"]
        elif dragging.sticky_block:
            self.image = images["spr_sticky_block"]
        elif dragging.fall_spikes:
            self.image = images["spr_fall_spikes"]
        elif dragging.stand_spikes:
            self.image = images["spr_stand_spikes"]
        else:
            self.image = images["spr_blank_box"]

class PlayEditSwitchButton(pygame.sprite.Sprite):
    def __init__(self, pos, GAME_MODE_SPRITES, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_play_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GAME_MODE_SPRITES.add(self)
    def game_mode_button(self, game_mode):
        if game_mode == 0:
            self.image = IMAGES["spr_play_button"]
        elif game_mode == 1:
            self.image = IMAGES["spr_stop_button"]
        return self.image

class MusicPlayer():
    def __init__(self, game_mode):
        if game_mode == 1:
            pygame.mixer.music.load("Sounds/play_music.mp3")
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load("Sounds/editing_mode.wav")
            pygame.mixer.music.play(-1)

class Grid(pygame.sprite.Sprite):
    grid_list = []
    def __init__(self, GRID_SPRITES, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_grid"]
        self.rect = self.image.get_rect()
        GRID_SPRITES.add(self)
        if self.rect.bottom > SCREEN_HEIGHT:
            GRID_SPRITES.remove(self)
        if self.rect.right > SCREEN_WIDTH:
            GRID_SPRITES.remove(self)
        Grid.grid_list.append(self)


class Dragging():
    def __init__(self):
        self.dragging_all_false()
    def dragging_all_false(self):
        self.player = False
        self.wall = False
        self.flyer = False
        self.reverse_wall = False
        self.spring = False
        self.smily_robot = False
        self.door = False
        self.diamonds = False
        self.sticky_block = False
        self.fall_spikes = False
        self.stand_spikes = False
        

class Start():
    def __init__(self):
        self.blank_box = StartBlankBox(IMAGES)
        START_SPRITES.add(self.blank_box)
        self.player = StartPlayer((10, 4), IMAGES)
        START_SPRITES.add(self.player)
        self.wall = StartWall((40, 12), IMAGES)
        START_SPRITES.add(self.wall)
        self.flyer = StartFlyer((130, 12), IMAGES)
        START_SPRITES.add(self.flyer)
        self.reverse_wall = StartReverseWall((102, 12), IMAGES)
        START_SPRITES.add(self.reverse_wall)
        self.spring = StartSpring((255, 12), IMAGES)
        START_SPRITES.add(self.spring)
        self.smily_robot = StartSmilyRobot((162, 12), IMAGES)
        START_SPRITES.add(self.smily_robot)
        self.door = StartDoor((195, 2), IMAGES)
        START_SPRITES.add(self.door)
        self.diamonds = StartDiamonds((225, 14), IMAGES)
        START_SPRITES.add(self.diamonds)
        self.sticky_block = StartStickyBlock((70, 12), IMAGES)
        START_SPRITES.add(self.sticky_block)
        self.fall_spikes = StartFallSpikes((290, 12), IMAGES)
        START_SPRITES.add(self.fall_spikes)
        self.stand_spikes = StartStandSpikes((320, 12), IMAGES)
        START_SPRITES.add(self.stand_spikes)

        
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'player': PlacedPlayer.player_list, 'door': PlacedDoor.door_list, 
                          'wall': PlacedWall.wall_list, 'flyer': PlacedFlyer.flyer_list, 
                          'reverse_wall': PlacedReverseWall.reverse_wall_list,
                          'spring': PlacedSpring.spring_list, 'smily_robot': PlacedSmilyRobot.smily_robot_list,
                          'diamonds': PlacedDiamonds.diamonds_list, 'sticky_block': PlacedStickyBlock.sticky_block_list,
                          'fall_spikes': PlacedFallSpikes.fall_spikes_list, 'stand_spikes': PlacedStandSpikes.stand_spikes_list}
    get_rect_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_rect in item_list:
            item_list_in_name.append(item_rect.rect.topleft)
        get_rect_for_all_obj[item_key] = item_list_in_name
    return get_rect_for_all_obj

def remove_all_placed():
    for spr_list in [PlacedPlayer.player_list, PlacedWall.wall_list, PlacedFlyer.flyer_list,
                     PlacedReverseWall.reverse_wall_list, PlacedSpring.spring_list, PlacedSmilyRobot.smily_robot_list,
                     PlacedDoor.door_list, PlacedDiamonds.diamonds_list, PlacedStickyBlock.sticky_block_list,
                     PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    PlacedPlayer.player_list = []
    PlacedWall.wall_list = []
    PlacedFlyer.flyer_list = []
    PlacedReverseWall.reverse_wall_list = []
    PlacedSpring.spring_list = []
    PlacedSmilyRobot.smily_robot_list = []
    PlacedDoor.door_list = []
    PlacedDiamonds.diamonds_list = []
    PlacedStickyBlock.sticky_block_list = []
    PlacedFallSpikes.fall_spikes_list = []
    PlacedStandSpikes.stand_spikes_list = []

def remove_all_play():
    for spr_list in [PlayPlayer.player_list, PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    PlayPlayer.player_list = []
    PlayWall.wall_list = []
    PlayFlyer.flyer_list = []
    PlayReverseWall.reverse_wall_list = []
    PlaySpring.spring_list = []
    PlaySmilyRobot.smily_robot_list = []
    PlayDoor.door_list = []
    PlayDiamonds.diamonds_list = []
    PlayStickyBlock.sticky_block_list = []
    PlayFallSpikes.fall_spikes_list = []
    PlayStandSpikes.stand_spikes_list = []

def restart_level():
    for spr_list in [PlayPlayer.player_list, PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.restart()

def main():
    #global PLACED_SPRITES
    # Tk box for color
#    ROOT = tk.Tk()
#    ROOT.withdraw()

    MENUON = 1
    load_all_assets()

    COLORKEY = [160, 160, 160]
    
    RUNNING, DEBUG = 0, 1
    state = RUNNING
    debug_message = 0
    
    #Fonts
    FONT_ARIAL = pygame.font.SysFont('Arial', 24)

    
    #Backgrounds
    START_MENU = pygame.image.load("sprites/start_menu.png").convert()
    START_MENU = pygame.transform.scale(START_MENU, (SCREEN_WIDTH, SCREEN_HEIGHT))
    INFO_SCREEN = pygame.image.load("sprites/info_screen.bmp").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))

    #Start (Menu) Objects
    START = Start()
    #Dragging Variables
    DRAGGING = Dragging()
    
    PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), GAME_MODE_SPRITES, IMAGES)
    CLEAR_BUTTON = ClearButton((SCREEN_WIDTH-115, 10), IMAGES)
    START_SPRITES.add(CLEAR_BUTTON)
    INFO_BUTTON = InfoButton((SCREEN_WIDTH-320, 10), IMAGES)
    START_SPRITES.add(INFO_BUTTON)
    GRID_BUTTON = GridButton((SCREEN_WIDTH-150, 10), IMAGES)
    START_SPRITES.add(GRID_BUTTON)
    RESTART_BUTTON = RestartButton((SCREEN_WIDTH-175, 10), PLAY_SPRITES, IMAGES)
    COLOR_BUTTON = ColorButton((SCREEN_WIDTH-195, 10), IMAGES)
    START_SPRITES.add(COLOR_BUTTON)
    SAVE_FILE_BUTTON = SaveFileButton((SCREEN_WIDTH-230, 10), IMAGES)
    START_SPRITES.add(SAVE_FILE_BUTTON)
    LOAD_FILE_BUTTON = LoadFileButton((SCREEN_WIDTH-265, 10), IMAGES)
    START_SPRITES.add(LOAD_FILE_BUTTON)
    ROTATE_BUTTON = RotateButton((SCREEN_WIDTH-590, 7), IMAGES)
    START_SPRITES.add(ROTATE_BUTTON)
    

    #MUSIC_PLAYER = [MusicPlayer()]
    
    EDIT_MODE, PLAY_MODE = 0, 1
    game_mode = EDIT_MODE
    
    # Creating grid on main area
    for i in range(0, SCREEN_WIDTH, 24):
        for j in range(48, SCREEN_HEIGHT, 24):
            grid = Grid(GRID_SPRITES, IMAGES)
            grid.rect.topleft = i, j
    
    while True:
        clock.tick(FPS)
        MOUSEPOS = pygame.mouse.get_pos()
        
        if state == RUNNING and MENUON == 1: # Initiate room
            START.player.rect.topleft = START_POSITIONS['player']
            START.wall.rect.topleft = START_POSITIONS['wall']
            START.flyer.rect.topleft = START_POSITIONS['flyer']
            START.reverse_wall.rect.topleft = START_POSITIONS['reverse_wall']
            START.spring.rect.topleft = START_POSITIONS['spring']
            START.smily_robot.rect.topleft = START_POSITIONS['smily_robot']
            START.door.rect.topleft = START_POSITIONS['door']
            START.diamonds.rect.topleft = START_POSITIONS['diamonds']
            START.sticky_block.rect.topleft = START_POSITIONS['sticky_block']
            START.fall_spikes.rect.topleft = START_POSITIONS['fall_spikes']
            START.stand_spikes.rect.topleft = START_POSITIONS['stand_spikes']


                    
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                        
                #################
                # LEFT CLICK (PRESSED DOWN) at Top of Screen
                #################
                if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[1] < 48): 
                    # DRAG (only for menu and inanimate buttons at top)
                    if game_mode == EDIT_MODE:
                        # BUTTONS
                        if GRID_BUTTON.rect.collidepoint(MOUSEPOS):
                            if GRID_BUTTON.grid_on_var == 1:
                                GRID_BUTTON.grid_on_var = 0
                            else:
                                GRID_BUTTON.grid_on_var = 1
                        # if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                        #     COLORKEY = get_color()
                        # if SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                        #     save_file(COLORKEY)
                        # if LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                        #     PLACED_SPRITES, COLORKEY = load_file(PLACED_SPRITES, COLORKEY)
                        
                        # DRAG
                        # Restarts all drag objects
                        
                        if START.player.rect.collidepoint(MOUSEPOS):
                            # Checks for if there is already a player placed on level
                            if not PlacedPlayer.player_list:
                                DRAGGING.dragging_all_false()
                                START = restart_start_objects(START, START_POSITIONS)
                                DRAGGING.player = True
                                START.blank_box.flip_start_sprite(DRAGGING, START.player.rect.topleft, IMAGES)
                            else:
                                print("Error: Too many players")
                        elif START.door.rect.collidepoint(MOUSEPOS):
                            if not PlacedDoor.door_list:
                                DRAGGING.dragging_all_false()
                                START = restart_start_objects(START, START_POSITIONS)
                                DRAGGING.door = True
                                START.blank_box.flip_start_sprite(DRAGGING, START.door.rect.topleft, IMAGES)
                            else:
                                print("Error: Only one exit allowed")
                        elif START.wall.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.wall = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.wall.rect.topleft, IMAGES)
                        elif START.flyer.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.flyer = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.flyer.rect.topleft, IMAGES)
                        elif START.reverse_wall.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.reverse_wall = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.reverse_wall.rect.topleft, IMAGES)
                        elif START.spring.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.spring = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.spring.rect.topleft, IMAGES)
                        elif START.smily_robot.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.smily_robot = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.smily_robot.rect.topleft, IMAGES)
                        elif START.diamonds.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.diamonds = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.diamonds.rect.topleft, IMAGES)
                        elif START.sticky_block.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.sticky_block = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.sticky_block.rect.topleft, IMAGES)
                        elif START.fall_spikes.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.fall_spikes = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.fall_spikes.rect.topleft, IMAGES)
                        elif START.stand_spikes.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START, START_POSITIONS)
                            DRAGGING.stand_spikes = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.stand_spikes.rect.topleft, IMAGES)
                            
                #################
                # LEFT CLICK (PRESSED DOWN)
                #################
                elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                    # Place object on location of mouse release
                    if DRAGGING.player:
                        PlacedPlayer(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.door:
                        PlacedDoor(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.wall:
                        PlacedWall(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.flyer:
                        PlacedFlyer(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.reverse_wall:
                        PlacedReverseWall(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.smily_robot:
                        PlacedSmilyRobot(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.spring:
                        PlacedSpring(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.diamonds:
                        PlacedDiamonds(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.sticky_block:
                        PlacedStickyBlock(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.fall_spikes:
                        PlacedFallSpikes(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                    elif DRAGGING.stand_spikes:
                        PlacedStandSpikes(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES, IMAGES)
                        
                #################
                # CLICK (RELEASE)
                #################           
                if game_mode == EDIT_MODE:
                # Right click on obj, destroy
                    if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                        DRAGGING.dragging_all_false()
                        START = restart_start_objects(START, START_POSITIONS)
                        remove_placed_object(PLACED_SPRITES, MOUSEPOS)
                if event.type == MOUSEBUTTONUP:            
                    #################
                    # PLAY BUTTON
                    #################
                    if(PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == EDIT_MODE):
                        # Makes sure there is at least one player to play game
                        if PlacedPlayer.player_list:
                            # Makes clicking play again unclickable
                            game_mode = PLAY_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            print("Play Mode Activated")
                            #MUSIC_PLAYER = [MusicPlayer()]
                            for placed_player in PlacedPlayer.player_list:
                                PlayPlayer(placed_player.rect.topleft, PLAY_SPRITES, IMAGES, SOUNDS)
                            for placed_door in PlacedDoor.door_list:
                                PlayDoor(placed_door.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_wall in PlacedWall.wall_list:
                                PlayWall(placed_wall.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_flyer in PlacedFlyer.flyer_list:
                                PlayFlyer(placed_flyer.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_reverse_wall in PlacedReverseWall.reverse_wall_list:
                                PlayReverseWall(placed_reverse_wall.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_smily_robot in PlacedSmilyRobot.smily_robot_list:
                                PlaySmilyRobot(placed_smily_robot.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_spring_list in PlacedSpring.spring_list:
                                PlaySpring(placed_spring_list.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_diamonds_list in PlacedDiamonds.diamonds_list:
                                PlayDiamonds(placed_diamonds_list.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_sticky_block_list in PlacedStickyBlock.sticky_block_list:
                                PlayStickyBlock(placed_sticky_block_list.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_fall_spikes_list in PlacedFallSpikes.fall_spikes_list:
                                PlayFallSpikes(placed_fall_spikes_list.rect.topleft, PLAY_SPRITES, IMAGES)
                            for placed_stand_spikes_list in PlacedStandSpikes.stand_spikes_list:
                                PlayStandSpikes(placed_stand_spikes_list.rect.topleft, PLAY_SPRITES, IMAGES)
                        else:
                            print("You need a character!")
                    #################
                    # LEFT CLICK (RELEASE) STOP BUTTON
                    #################
                    elif(PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == PLAY_MODE):
                        # Makes sure you are not in editing mode to enter editing mode
                        if game_mode == PLAY_MODE:
                            print("Editing Mode Activated")
                            PlayPlayer.player_list[0].death_count = 0
                            game_mode = EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            remove_all_play()
                            #MUSIC_PLAYER = []
                            #MUSIC_PLAYER = [MusicPlayer()]
                    if RESTART_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_mode == PLAY_MODE:
                            restart_level()
                    if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                        MENUON = 2
                    if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_mode == EDIT_MODE: #Editing mode
                            START = restart_start_objects(START, START_POSITIONS)
                            # REMOVE ALL SPRITES
                            remove_all_placed()
                    if ROTATE_BUTTON.rect.collidepoint(MOUSEPOS):
                        START.stand_spikes.rotate -= 90
                        
                #################
                # KEYBOARD EVENTS (PLAYER)
                #################
                if game_mode == PLAY_MODE:
                    if event.type == pygame.KEYUP:
                        if event.key == K_LEFT and PlayPlayer.player_list[0].speed_x < 0:
                            PlayPlayer.player_list[0].stop()
                        if event.key == pygame.K_RIGHT and PlayPlayer.player_list[0].speed_x > 0:
                            PlayPlayer.player_list[0].stop()
                    if event.type == KEYDOWN:
                        if event.key == pygame.K_UP:
                            if PlayPlayer.player_list[0].jumps_left > 0:
                                PlayPlayer.player_list[0].jump()
                                
            ##################
            # ALL EDIT ACTIONS
            ##################
            # Replace start sprite with blank box in top menu
            if game_mode == EDIT_MODE:
                if DRAGGING.player and not PlacedPlayer.player_list:
                    START.blank_box.rect.topleft = START_POSITIONS['player'] # Replaces in Menu
                    START.player.rect.topleft = (MOUSEPOS[0]-(START.player.image.get_width()/2),
                                                 MOUSEPOS[1]-(START.player.image.get_height()/3))
                else:
                    DRAGGING.player = False
                    START.player.rect.topleft = START_POSITIONS['player']
                if DRAGGING.wall:
                    START.blank_box.rect.topleft = START_POSITIONS['wall'] # Replaces in Menu
                    START.wall.rect.topleft = (MOUSEPOS[0]-(START.wall.image.get_width()/2),
                                               MOUSEPOS[1]-(START.wall.image.get_height()/2))
                else:
                    START.wall.rect.topleft = START_POSITIONS['wall']
                if DRAGGING.reverse_wall:
                    START.blank_box.rect.topleft = START_POSITIONS['reverse_wall'] # Replaces in Menu
                    START.reverse_wall.rect.topleft = (MOUSEPOS[0]-(START.reverse_wall.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.reverse_wall.image.get_height()/2))
                else:
                    START.reverse_wall.rect.topleft = START_POSITIONS['reverse_wall']
                if DRAGGING.diamonds:
                    START.blank_box.rect.topleft = START_POSITIONS['diamonds'] # Replaces in Menu
                    START.diamonds.rect.topleft = (MOUSEPOS[0]-(START.diamonds.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.diamonds.image.get_height()/2))
                else:
                    START.diamonds.rect.topleft = START_POSITIONS['diamonds']
                if DRAGGING.door and not PlacedDoor.door_list:
                    START.blank_box.rect.topleft = START_POSITIONS['door'] # Replaces in Menu
                    START.door.rect.topleft = (MOUSEPOS[0]-(START.door.image.get_width()/2),
                                               MOUSEPOS[1]-(START.door.image.get_height()/4))
                    START.door.image = IMAGES["spr_door_closed"]
                else:
                    START.door.rect.topleft = START_POSITIONS['door']
                    START.door.image = pygame.transform.smoothscale(IMAGES["spr_door_closed"], (24, 40))
                if DRAGGING.flyer:
                    START.blank_box.rect.topleft = START_POSITIONS['flyer'] # Replaces in Menu
                    START.flyer.rect.topleft = (MOUSEPOS[0]-(START.flyer.image.get_width()/2),
                                                MOUSEPOS[1]-(START.flyer.image.get_height()/2))
                else:
                    START.flyer.rect.topleft = START_POSITIONS['flyer']
                if DRAGGING.smily_robot:
                    START.blank_box.rect.topleft = START_POSITIONS['smily_robot'] # Replaces in Menu
                    START.smily_robot.rect.topleft = (MOUSEPOS[0]-(START.smily_robot.image.get_width()/2),
                                                      MOUSEPOS[1]-(START.smily_robot.image.get_height()/2))
                else:
                    START.smily_robot.rect.topleft = START_POSITIONS['smily_robot']
                if DRAGGING.spring:
                    START.blank_box.rect.topleft = START_POSITIONS['spring'] # Replaces in Menu
                    START.spring.rect.topleft = (MOUSEPOS[0]-(START.spring.image.get_width()/2),
                                                 MOUSEPOS[1]-(START.spring.image.get_height()/2))
                else:
                    START.spring.rect.topleft = START_POSITIONS['spring']
                if DRAGGING.sticky_block:
                    START.blank_box.rect.topleft = START_POSITIONS['sticky_block'] # Replaces in Menu
                    START.sticky_block.rect.topleft = (MOUSEPOS[0]-(START.sticky_block.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.sticky_block.image.get_height()/2))
                else:
                    START.sticky_block.rect.topleft = START_POSITIONS['sticky_block']
                if DRAGGING.fall_spikes:
                    START.blank_box.rect.topleft = START_POSITIONS['fall_spikes'] # Replaces in Menu
                    START.fall_spikes.rect.topleft = (MOUSEPOS[0]-(START.fall_spikes.image.get_width()/2),
                                                      MOUSEPOS[1]-(START.fall_spikes.image.get_height()/2))
                else:
                    START.fall_spikes.rect.topleft = START_POSITIONS['fall_spikes']
                if START.stand_spikes.rotate == 0:
                    START.stand_spikes.image = IMAGES["spr_stand_spikes"]
                else:
                    START.stand_spikes.image = pygame.transform.rotate(IMAGES["spr_stand_spikes"], START.stand_spikes.rotate)
                if DRAGGING.stand_spikes:
                    START.blank_box.rect.topleft = START_POSITIONS['stand_spikes'] # Replaces in Menu
                    START.stand_spikes.rect.topleft = (MOUSEPOS[0]-(START.stand_spikes.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.stand_spikes.image.get_height()/2))
                else:
                    START.stand_spikes.rect.topleft = START_POSITIONS['stand_spikes']
                    
            ##################
            # IN-GAME ACTIONS
            ##################
            if game_mode == PLAY_MODE:
                
                # Avoid player going off screen
                KEYS_PRESSED = pygame.key.get_pressed()
                if KEYS_PRESSED[K_LEFT]:
                    PlayPlayer.player_list[0].last_pressed_r = 0
                    if PlayPlayer.player_list[0].rect.left > 0:
                        PlayPlayer.player_list[0].go_left()
                    else:
                        PlayPlayer.player_list[0].stop()
                if KEYS_PRESSED[K_RIGHT]:
                    PlayPlayer.player_list[0].last_pressed_r = 1
                    if PlayPlayer.player_list[0].rect.right < SCREEN_WIDTH:
                        PlayPlayer.player_list[0].go_right()
                    else:
                        PlayPlayer.player_list[0].stop()
                # Dead
                if PlayPlayer.player_list[0].rect.top > SCREEN_HEIGHT and PlayPlayer.player_list[0].speed_y >= 0:
                    restart_level()
                # Spikes fall when player goes underneath
                if PlayFallSpikes.fall_spikes_list:
                    for fall_spike in PlayFallSpikes.fall_spikes_list:
                        if(PlayPlayer.player_list[0].rect.right > fall_spike.rect.left and
                           PlayPlayer.player_list[0].rect.left < fall_spike.rect.right and
                           PlayPlayer.player_list[0].rect.top > fall_spike.rect.bottom):
                            fall_spike.fall_var = 1
                        if fall_spike.fall_var == 1:
                            fall_spike.rect.top = fall_spike.rect.top + 5
                # Player wins when he captures all jewels and enters door
                if PlayDoor.door_list:
                    PlayDoor.door_list[0].image = PlayDoor.door_list[0].open_or_close(PlayPlayer.player_list[0].score, PlayDiamonds.diamonds_list)
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], PlayDoor.door_list[0]):
                        if PlayPlayer.player_list[0].score == len(PlayDiamonds.diamonds_list):
                            print("You Win!")
                            PlayPlayer.player_list[0].death_count = 0
                            game_mode = EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            #music_player = [MusicPlayer()]
                            PlayPlayer.player_list[0].rect.topleft = PlacedPlayer.player_list[0].rect.topleft
                            for i in range(0, len(PlacedSmilyRobot.smily_robot_list)):
                                PlaySmilyRobot.smily_robot_list[i].rect.topleft = PlacedSmilyRobot.smily_robot_list[i].rect.topleft
                                PlaySmilyRobot.smily_robot_list[i].speed_y = 0
                            for i in range(0, len(PlacedFlyer.flyer_list)):
                                PlayFlyer.flyer_list[i].rect.topleft = PlacedFlyer.flyer_list[i].rect.topleft
                            for play_diamonds in PlayDiamonds.diamonds_list:
                                play_diamonds.image = IMAGES["spr_diamonds"]
                            for i in range(0, len(PlacedFallSpikes.fall_spikes_list)):
                                PlayFallSpikes.fall_spikes_list[i].rect.topleft = PlacedFallSpikes.fall_spikes_list[i].rect.topleft
                                PlayFallSpikes.fall_spikes_list[i].fall_var = 0
                            

                        
                #####################
                # COLLISIONS
                #####################
                for play_smily_robot in PlaySmilyRobot.smily_robot_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_smily_robot.rect):
                        if(PlayPlayer.player_list[0].rect.bottom <= play_smily_robot.rect.top + 10 and PlayPlayer.player_list[0].speed_y >= 0):
                            play_smily_robot.rect.topleft = PlaySmilyRobot.OUT_OF_PLAY_TOPLEFT
                            PlayPlayer.player_list[0].propeller = 0
                            PlayPlayer.player_list[0].speed_y = -4
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif(PlayPlayer.player_list[0].rect.right-play_smily_robot.rect.left <= 10 and
                             PlayPlayer.player_list[0].rect.bottom > play_smily_robot.rect.top + 10):
                            restart_level()
                        elif(PlayPlayer.player_list[0].rect.left-play_smily_robot.rect.right <= 10 and
                             PlayPlayer.player_list[0].rect.bottom > play_smily_robot.rect.top + 10):
                            restart_level()
                for play_flyer in PlayFlyer.flyer_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_flyer.rect):
                        restart_level()
                for play_fall_spikes in PlayFallSpikes.fall_spikes_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_fall_spikes.rect):
                        restart_level()
                for play_stand_spikes in PlayStandSpikes.stand_spikes_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_stand_spikes.rect):
                        restart_level()
                for play_diamonds in PlayDiamonds.diamonds_list:
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], play_diamonds):
                        PlayPlayer.player_list[0].score += 1
                        play_diamonds.image = IMAGES["spr_blank_box"]
                for spring in PlaySpring.spring_list:
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], spring):
                        if PlayPlayer.player_list[0].rect.bottom <= spring.rect.top+20 and PlayPlayer.player_list[0].speed_y >= 10: #big jumps
                            SOUNDS["snd_spring"].play()
                            PlayPlayer.player_list[0].propeller = 0 
                            PlayPlayer.player_list[0].rect.bottom = spring.rect.top
                            PlayPlayer.player_list[0].speed_y = -10
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif PlayPlayer.player_list[0].rect.bottom <= spring.rect.top+10 and PlayPlayer.player_list[0].speed_y >= 0:
                            SOUNDS["snd_spring"].play()
                            PlayPlayer.player_list[0].propeller = 0 #Fixes propeller bug
                            PlayPlayer.player_list[0].rect.bottom = spring.rect.top
                            PlayPlayer.player_list[0].speed_y = -10
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif PlayPlayer.player_list[0].speed_x > 0:
                            PlayPlayer.player_list[0].rect.right = spring.rect.left
                        elif PlayPlayer.player_list[0].speed_x < 0:
                            PlayPlayer.player_list[0].rect.left = spring.rect.right
                        elif PlayPlayer.player_list[0].speed_y < 0:
                            PlayPlayer.player_list[0].speed_y = 0
                            PlayPlayer.player_list[0].propeller = 0
                            PlayPlayer.player_list[0].rect.top = spring.rect.bottom #Below the wall
            #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
            
            SCREEN.fill(COLORKEY)

            #Update all sprites
            START_SPRITES.update()
            PLACED_SPRITES.update()
            PLAY_SPRITES.update()
            GAME_MODE_SPRITES.draw(SCREEN)
            if game_mode == EDIT_MODE: #Only draw placed sprites in editing mode
                if GRID_BUTTON.grid_on_var == 1:
                    GRID_SPRITES.draw(SCREEN)
                START_SPRITES.draw(SCREEN)
                PLACED_SPRITES.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("", 1, (0, 0, 0))
            elif game_mode == PLAY_MODE: #Only draw play sprites in play mode
                PLAY_SPRITES.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("Deaths: " + str(PlayPlayer.player_list[0].death_count), 1, (0, 0, 0))
            SCREEN.blit(DEATH_COUNT_TEXT, ((SCREEN_WIDTH/2-50), 5))

            pygame.display.update()
        elif MENUON == 2: # Info SCREEN in a WHILE loop
            InfoScreen(INFO_SCREEN, SCREEN)
            MENUON = 1
        elif state == DEBUG:
            if debug_message == 1:
                print("Entering debug mode")
                debug_message = 0
                # USE BREAKPOINT HERE
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        state = RUNNING
        
if __name__ == "__main__":
    main()