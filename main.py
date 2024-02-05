"""
Propeller Platformer: Level Editor created by Brad Wyatt
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
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, IMAGES, SOUNDS, MOBILE_ACCESSIBILITY_MODE, load_image, load_sound
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

def snap_to_grid(pos, screen_width, screen_height, grid_spacing, top_ui_boundary_y_height):
    """
    Adjusts a given position to the top-left corner of the nearest grid cell.
    
    :param pos: A tuple (x, y) representing the position to adjust.
    :param screen_width: Width of the screen or canvas.
    :param screen_height: Height of the screen or canvas.
    :param grid_spacing: The size of each grid cell.
    :param top_ui_boundary_y_height: The Y-coordinate from where the grid starts.
    :return: A tuple (adjusted_x, adjusted_y) representing the adjusted position.
    """
    # Calculate column and row in the grid based on the position
    col = pos[0] // grid_spacing
    row = max(0, (pos[1] - top_ui_boundary_y_height) // grid_spacing)

    # Calculate the adjusted position
    adjusted_x = col * grid_spacing
    adjusted_y = row * grid_spacing + top_ui_boundary_y_height

    return adjusted_x, adjusted_y

def remove_placed_object(placed_sprites, mouse_pos, game_state):
    # Iterate over all lists except the player list, which is handled separately now.
    for placed_item_list in (PlacedWall.wall_list, PlacedFlyer.flyer_list,
                             PlacedSpring.spring_list, PlacedDiamonds.diamonds_list, PlacedReverseWall.reverse_wall_list,
                             PlacedSmilyRobot.smily_robot_list, PlacedDoor.door_list, PlacedStickyBlock.sticky_block_list,
                             PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mouse_pos):
                placed_sprites.remove(placed_item)
                placed_item_list.remove(placed_item)

    # Check if the placed player exists and if the mouse position collides with it.
    if game_state.placed_player and game_state.placed_player.rect.collidepoint(mouse_pos):
        placed_sprites.remove(game_state.placed_player)
        game_state.placed_player = None  # Directly set the player to None since it's no longer a list.

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

def get_color():
    color = askcolor()
    return [color[0][0], color[0][1], color[0][2]]

def load_file(PLACED_SPRITES, colorkey, game_state):
    request_file_name = askopenfilename(defaultextension=".lvl")
    open_file = open(request_file_name, "r")
    loaded_file = open_file.read()
    loaded_dict = literal_eval(loaded_file)
            
    game_state.play_player.destroy()
    for door in PlayDoor.door_list:
        door.destroy()
    for wall in PlayWall.wall_list:
        wall.destroy()
    for reverse_wall in PlayReverseWall.reverse_wall_list:
        reverse_wall.destroy()
    for flyer in PlayFlyer.flyer_list:
        flyer.destroy()
    for smily_robot in PlaySmilyRobot.smily_robot_list:
        smily_robot.destroy()
    for spring in PlaySpring.spring_list:
        spring.destroy()
    for diamond in PlayDiamonds.diamonds_list:
        diamond.destroy()
    for sticky_block in PlayStickyBlock.sticky_block_list:
        sticky_block.destroy()
    for fall_spikes in PlayFallSpikes.fall_spikes_list:
        fall_spikes.destroy()
    for stand_spikes in PlayStandSpikes.stand_spikes_list:
        stand_spikes.destroy()
    open_file.close()
    
    # Removes all placed lists
    remove_all_placed(game_state)
    
    print("Removed all sprites. Now creating lists for loaded level.")
    
    for player_pos in loaded_dict['player']:
        PlacedPlayer(player_pos, PLACED_SPRITES)
    for door_pos in loaded_dict['door']:
        PlacedDoor(door_pos, PLACED_SPRITES)
    for wall_pos in loaded_dict['wall']:
        PlacedWall(wall_pos, PLACED_SPRITES)
    for reverse_wall_pos in loaded_dict['reverse_wall']:
        PlacedReverseWall(reverse_wall_pos, PLACED_SPRITES)
    for flyer_pos in loaded_dict['flyer']:
        PlacedFlyer(flyer_pos, PLACED_SPRITES)
    for smily_robot_pos in loaded_dict['smily_robot']:
        PlacedSmilyRobot(smily_robot_pos, PLACED_SPRITES)
    for spring_pos in loaded_dict['spring']:
        PlacedSpring(spring_pos, PLACED_SPRITES)
    for diamond_pos in loaded_dict['diamonds']:
        PlacedDiamonds(diamond_pos, PLACED_SPRITES)
    for sticky_block_pos in loaded_dict['sticky_block']:
        PlacedStickyBlock(sticky_block_pos, PLACED_SPRITES)
    for fall_spikes_pos in loaded_dict['fall_spikes']:
        PlacedFallSpikes(fall_spikes_pos, PLACED_SPRITES)
    for stand_spikes_pos in loaded_dict['stand_spikes']:
        PlacedStandSpikes(stand_spikes_pos, PLACED_SPRITES)
    colorkey = loaded_dict['RGB']
    
    print("File Loaded")
    return PLACED_SPRITES, colorkey

def save_file(colorkey):
    try:
        if PlacedPlayer.player_list and PlacedDoor.door_list:
            # default extension is optional, here will add .txt if missing
            save_file_prompt = asksaveasfilename(defaultextension=".lvl")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                obj_locations = copy.deepcopy(get_dict_rect_positions())
                obj_locations['RGB'] = colorkey
                save_file_name.write(str(obj_locations))
                save_file_name.close()
                print("File Saved Successfully.")
        else:
            print("Error! Need player and door to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")

def create_grids_in_game_world(game_state, screen_width, screen_height, grid_spacing, top_ui_boundary_y_height):
    """
    Creates a grid for the level editor.

    :param game_state: The current state of the game, holding sprite groups and other stateful information.
    :param screen_width: The width of the screen or canvas.
    :param screen_height: The height of the screen or canvas.
    :param grid_spacing: The spacing between grid lines.
    :param top_ui_boundary_y_height: The Y-coordinate from where the grid should start, to avoid UI overlap.
    """
    for x in range(0, screen_width, grid_spacing):
        for y in range(top_ui_boundary_y_height, screen_height, grid_spacing):
            grid = Grid(game_state.grid_sprites, IMAGES)
            grid.rect.topleft = (x, y)

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
    def __init__(self, start_sprites, start_positions):
        self.blank_box = StartBlankBox(IMAGES)
        start_sprites.add(self.blank_box)
        self.player = StartPlayer(start_positions['player'], IMAGES)
        start_sprites.add(self.player)
        self.wall = StartWall(start_positions['wall'], IMAGES)
        start_sprites.add(self.wall)
        self.flyer = StartFlyer(start_positions['flyer'], IMAGES)
        start_sprites.add(self.flyer)
        self.reverse_wall = StartReverseWall(start_positions['reverse_wall'], IMAGES)
        start_sprites.add(self.reverse_wall)
        self.spring = StartSpring(start_positions['spring'], IMAGES)
        start_sprites.add(self.spring)
        self.smily_robot = StartSmilyRobot(start_positions['smily_robot'], IMAGES)
        start_sprites.add(self.smily_robot)
        self.door = StartDoor(start_positions['door'], IMAGES)
        start_sprites.add(self.door)
        self.diamonds = StartDiamonds(start_positions['diamonds'], IMAGES)
        start_sprites.add(self.diamonds)
        self.sticky_block = StartStickyBlock(start_positions['sticky_block'], IMAGES)
        start_sprites.add(self.sticky_block)
        self.fall_spikes = StartFallSpikes(start_positions['fall_spikes'], IMAGES)
        start_sprites.add(self.fall_spikes)
        self.stand_spikes = StartStandSpikes(start_positions['stand_spikes'], IMAGES)
        start_sprites.add(self.stand_spikes)
        
class GameState:
    EDIT_MODE, PLAY_MODE = 0, 1
    START_POSITIONS = {'player': (10, 4), 'wall': (40, 12), 'reverse_wall': (102, 12),
                'spring': (255, 12), 'flyer': (130, 12), 'smily_robot': (162, 12),
                'door': (195, 2), 'diamonds': (225, 14), 'sticky_block': (70, 12),
                'fall_spikes': (290, 12), 'stand_spikes': (320, 12)}
    RUNNING, DEBUG = 0, 1
    STATE = RUNNING
    TOP_UI_BOUNDARY_Y_HEIGHT = 96
    GRID_SPACING = 24
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.grid_sprites = pygame.sprite.Group()
        self.start_sprites = pygame.sprite.Group()
        self.play_sprites = pygame.sprite.Group()
        self.game_mode_sprites = pygame.sprite.Group()
        self.placed_sprites = pygame.sprite.Group()
        self.dragging = Dragging()
        self.start = Start(self.start_sprites, self.START_POSITIONS)
        self.game_mode = GameState.EDIT_MODE
        self.mouse_pos = (0, 0)
        self.init_ui_elements()
        
        self.placed_player = None

    def update_mouse_pos(self):
        self.mouse_pos = pygame.mouse.get_pos()
    def init_ui_elements(self):
        self.play_edit_switch_button = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), self.game_mode_sprites, IMAGES)
        self.clear_button = ClearButton((SCREEN_WIDTH-115, 10), IMAGES)
        self.start_sprites.add(self.clear_button)
        self.info_button = InfoButton((SCREEN_WIDTH-320, 10), IMAGES)
        self.start_sprites.add(self.info_button)
        self.grid_button = GridButton((SCREEN_WIDTH-150, 10), IMAGES)
        self.start_sprites.add(self.grid_button)
        self.restart_button = RestartButton((SCREEN_WIDTH-175, 10), self.play_sprites, IMAGES)
        self.color_button = ColorButton((SCREEN_WIDTH-195, 10), IMAGES)
        self.start_sprites.add(self.color_button)
        self.save_file_button = SaveFileButton((SCREEN_WIDTH-230, 10), IMAGES)
        self.start_sprites.add(self.save_file_button)
        self.load_file_button = LoadFileButton((SCREEN_WIDTH-265, 10), IMAGES)
        self.start_sprites.add(self.load_file_button)
        self.rotate_button = RotateButton((SCREEN_WIDTH-590, 7), IMAGES)
        self.start_sprites.add(self.rotate_button)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    debug_message = True
                    GameState.STATE = GameState.DEBUG
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                    
            #################
            # LEFT CLICK (PRESSED DOWN) at Top of Screen
            #################
            if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and self.mouse_pos[1] < GameState.TOP_UI_BOUNDARY_Y_HEIGHT): 
                # DRAG (only for menu and inanimate buttons at top)
                if self.game_mode == GameState.EDIT_MODE:
                    # BUTTONS
                    if self.grid_button.rect.collidepoint(self.mouse_pos):
                        if self.grid_button.grid_on_var:
                            self.grid_button.grid_on_var = False
                        else:
                            self.grid_button.grid_on_var = True
                    if not MOBILE_ACCESSIBILITY_MODE:
                        if self.color_button.rect.collidepoint(self.mouse_pos):
                            COLORKEY = get_color()
                        if self.save_file_button.rect.collidepoint(self.mouse_pos):
                            save_file(COLORKEY)
                        if self.load_file_button.rect.collidepoint(self.mouse_pos):
                            self.placed_sprites, COLORKEY = load_file(self.placed_sprites, COLORKEY, self)
                    
                    # DRAG
                    # Restarts all drag objects
                    
                    if self.start.player.rect.collidepoint(self.mouse_pos):
                        # Checks for if there is already a player placed on level
                        if self.placed_player is None:
                            self.dragging.dragging_all_false()
                            self.start = restart_start_objects(self.start, self.START_POSITIONS)
                            self.dragging.player = True
                            self.start.blank_box.flip_start_sprite(self.dragging, self.start.player.rect.topleft, IMAGES)
                        else:
                            print("Error: Too many players")
                    elif self.start.door.rect.collidepoint(self.mouse_pos):
                        if not PlacedDoor.door_list:
                            self.dragging.dragging_all_false()
                            self.start = restart_start_objects(self.start, self.START_POSITIONS)
                            self.dragging.door = True
                            self.start.blank_box.flip_start_sprite(self.dragging, self.start.door.rect.topleft, IMAGES)
                        else:
                            print("Error: Only one exit allowed")
                    elif self.start.wall.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.wall = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.wall.rect.topleft, IMAGES)
                    elif self.start.flyer.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.flyer = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.flyer.rect.topleft, IMAGES)
                    elif self.start.reverse_wall.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.reverse_wall = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.reverse_wall.rect.topleft, IMAGES)
                    elif self.start.spring.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.spring = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.spring.rect.topleft, IMAGES)
                    elif self.start.smily_robot.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.smily_robot = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.smily_robot.rect.topleft, IMAGES)
                    elif self.start.diamonds.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.diamonds = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.diamonds.rect.topleft, IMAGES)
                    elif self.start.sticky_block.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.sticky_block = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.sticky_block.rect.topleft, IMAGES)
                    elif self.start.fall_spikes.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.fall_spikes = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.fall_spikes.rect.topleft, IMAGES)
                    elif self.start.stand_spikes.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.dragging.stand_spikes = True
                        self.start.blank_box.flip_start_sprite(self.dragging, self.start.stand_spikes.rect.topleft, IMAGES)
                        
            #################
            # LEFT CLICK (PRESSED DOWN)
            #################
            elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                # Place object on location of mouse release
                if self.dragging.player:
                    self.placed_player = PlacedPlayer(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.door:
                    PlacedDoor(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.wall:
                    PlacedWall(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.flyer:
                    PlacedFlyer(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.reverse_wall:
                    PlacedReverseWall(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.smily_robot:
                    PlacedSmilyRobot(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.spring:
                    PlacedSpring(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.diamonds:
                    PlacedDiamonds(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.sticky_block:
                    PlacedStickyBlock(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.fall_spikes:
                    PlacedFallSpikes(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                elif self.dragging.stand_spikes:
                    PlacedStandSpikes(snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT), self.placed_sprites, IMAGES)
                    
            #################
            # CLICK (RELEASE)
            #################           
            if self.game_mode == self.EDIT_MODE:
            # Right click on obj, destroy
                if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                    self.dragging.dragging_all_false()
                    self.start = restart_start_objects(self.start, self.START_POSITIONS)
                    remove_placed_object(self.placed_sprites, self.mouse_pos, self)
            if event.type == MOUSEBUTTONUP:            
                #################
                # PLAY BUTTON
                #################
                if(self.play_edit_switch_button.rect.collidepoint(self.mouse_pos) and self.game_mode == self.EDIT_MODE):
                    # Makes sure there is at least one player to play game
                    if self.placed_player:
                        # Makes clicking play again unclickable
                        self.game_mode = self.PLAY_MODE
                        self.play_edit_switch_button.image = self.play_edit_switch_button.game_mode_button(self.game_mode)
                        print("Play Mode Activated")
                        #MUSIC_PLAYER = [MusicPlayer()]
                        self.play_player = PlayPlayer(self.placed_player.rect.topleft, self.play_sprites, IMAGES, SOUNDS)
                        for placed_door in PlacedDoor.door_list:
                            PlayDoor(placed_door.rect.topleft, self.play_sprites, IMAGES)
                        for placed_wall in PlacedWall.wall_list:
                            PlayWall(placed_wall.rect.topleft, self.play_sprites, IMAGES)
                        for placed_flyer in PlacedFlyer.flyer_list:
                            PlayFlyer(placed_flyer.rect.topleft, self.play_sprites, IMAGES)
                        for placed_reverse_wall in PlacedReverseWall.reverse_wall_list:
                            PlayReverseWall(placed_reverse_wall.rect.topleft, self.play_sprites, IMAGES)
                        for placed_smily_robot in PlacedSmilyRobot.smily_robot_list:
                            PlaySmilyRobot(placed_smily_robot.rect.topleft, self.play_sprites, IMAGES)
                        for placed_spring_list in PlacedSpring.spring_list:
                            PlaySpring(placed_spring_list.rect.topleft, self.play_sprites, IMAGES)
                        for placed_diamonds_list in PlacedDiamonds.diamonds_list:
                            PlayDiamonds(placed_diamonds_list.rect.topleft, self.play_sprites, IMAGES)
                        for placed_sticky_block_list in PlacedStickyBlock.sticky_block_list:
                            PlayStickyBlock(placed_sticky_block_list.rect.topleft, self.play_sprites, IMAGES)
                        for placed_fall_spikes_list in PlacedFallSpikes.fall_spikes_list:
                            PlayFallSpikes(placed_fall_spikes_list.rect.topleft, self.play_sprites, IMAGES)
                        for placed_stand_spikes_list in PlacedStandSpikes.stand_spikes_list:
                            PlayStandSpikes(placed_stand_spikes_list.rect.topleft, self.play_sprites, IMAGES)
                    else:
                        print("You need a character!")
                #################
                # LEFT CLICK (RELEASE) STOP BUTTON
                #################
                elif(self.play_edit_switch_button.rect.collidepoint(self.mouse_pos) and self.game_mode == self.PLAY_MODE):
                    # Makes sure you are not in editing mode to enter editing mode
                    if self.game_mode == self.PLAY_MODE:
                        print("Editing Mode Activated")
                        self.play_player.death_count = 0
                        self.game_mode = self.EDIT_MODE
                        self.play_edit_switch_button.image = self.play_edit_switch_button.game_mode_button(self.game_mode)
                        remove_all_play(self)
                        #MUSIC_PLAYER = []
                        #MUSIC_PLAYER = [MusicPlayer()]
                if self.restart_button.rect.collidepoint(self.mouse_pos):
                    if self.game_mode == self.PLAY_MODE:
                        restart_level(self)
                if self.info_button.rect.collidepoint(self.mouse_pos):
                    MENUON = 2
                if self.clear_button.rect.collidepoint(self.mouse_pos):
                    if self.game_mode == self.EDIT_MODE: #Editing mode
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        # REMOVE ALL SPRITES
                        remove_all_placed(self)
                if self.rotate_button.rect.collidepoint(self.mouse_pos):
                    self.start.stand_spikes.rotate -= 90
                    
            #################
            # KEYBOARD EVENTS (PLAYER)
            #################
            if self.game_mode == self.PLAY_MODE:
                if event.type == pygame.KEYUP:
                    if event.key == K_LEFT and self.play_player.speed_x < 0:
                        self.play_player.stop()
                    if event.key == pygame.K_RIGHT and self.play_player.speed_x > 0:
                        self.play_player.stop()
                if event.type == KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.play_player.jumps_left > 0:
                            self.play_player.jump()
    def edit_mode_function(self):
        if self.dragging.player and self.placed_player is None:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['player'] # Replaces in Menu
            self.start.player.rect.topleft = (self.mouse_pos[0]-(self.start.player.image.get_width()/2),
                                         self.mouse_pos[1]-(self.start.player.image.get_height()/3))
        else:
            self.dragging.player = False
            self.start.player.rect.topleft = self.START_POSITIONS['player']
        if self.dragging.wall:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['wall'] # Replaces in Menu
            self.start.wall.rect.topleft = (self.mouse_pos[0]-(self.start.wall.image.get_width()/2),
                                       self.mouse_pos[1]-(self.start.wall.image.get_height()/2))
        else:
            self.start.wall.rect.topleft = self.START_POSITIONS['wall']
        if self.dragging.reverse_wall:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['reverse_wall'] # Replaces in Menu
            self.start.reverse_wall.rect.topleft = (self.mouse_pos[0]-(self.start.reverse_wall.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.reverse_wall.image.get_height()/2))
        else:
            self.start.reverse_wall.rect.topleft = self.START_POSITIONS['reverse_wall']
        if self.dragging.diamonds:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['diamonds'] # Replaces in Menu
            self.start.diamonds.rect.topleft = (self.mouse_pos[0]-(self.start.diamonds.image.get_width()/2),
                                           self.mouse_pos[1]-(self.start.diamonds.image.get_height()/2))
        else:
            self.start.diamonds.rect.topleft = self.START_POSITIONS['diamonds']
        if self.dragging.door and not PlacedDoor.door_list:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['door'] # Replaces in Menu
            self.start.door.rect.topleft = (self.mouse_pos[0]-(self.start.door.image.get_width()/2),
                                       self.mouse_pos[1]-(self.start.door.image.get_height()/4))
            self.start.door.image = IMAGES["spr_door_closed"]
        else:
            self.start.door.rect.topleft = self.START_POSITIONS['door']
            self.start.door.image = pygame.transform.smoothscale(IMAGES["spr_door_closed"], (24, 40))
        if self.dragging.flyer:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['flyer'] # Replaces in Menu
            self.start.flyer.rect.topleft = (self.mouse_pos[0]-(self.start.flyer.image.get_width()/2),
                                        self.mouse_pos[1]-(self.start.flyer.image.get_height()/2))
        else:
            self.start.flyer.rect.topleft = self.START_POSITIONS['flyer']
        if self.dragging.smily_robot:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['smily_robot'] # Replaces in Menu
            self.start.smily_robot.rect.topleft = (self.mouse_pos[0]-(self.start.smily_robot.image.get_width()/2),
                                              self.mouse_pos[1]-(self.start.smily_robot.image.get_height()/2))
        else:
            self.start.smily_robot.rect.topleft = self.START_POSITIONS['smily_robot']
        if self.dragging.spring:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['spring'] # Replaces in Menu
            self.start.spring.rect.topleft = (self.mouse_pos[0]-(self.start.spring.image.get_width()/2),
                                         self.mouse_pos[1]-(self.start.spring.image.get_height()/2))
        else:
            self.start.spring.rect.topleft = self.START_POSITIONS['spring']
        if self.dragging.sticky_block:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['sticky_block'] # Replaces in Menu
            self.start.sticky_block.rect.topleft = (self.mouse_pos[0]-(self.start.sticky_block.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.sticky_block.image.get_height()/2))
        else:
            self.start.sticky_block.rect.topleft = self.START_POSITIONS['sticky_block']
        if self.dragging.fall_spikes:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['fall_spikes'] # Replaces in Menu
            self.start.fall_spikes.rect.topleft = (self.mouse_pos[0]-(self.start.fall_spikes.image.get_width()/2),
                                              self.mouse_pos[1]-(self.start.fall_spikes.image.get_height()/2))
        else:
            self.start.fall_spikes.rect.topleft = self.START_POSITIONS['fall_spikes']
        if self.start.stand_spikes.rotate == 0:
            self.start.stand_spikes.image = IMAGES["spr_stand_spikes"]
        else:
            self.start.stand_spikes.image = pygame.transform.rotate(IMAGES["spr_stand_spikes"], self.start.stand_spikes.rotate)
        if self.dragging.stand_spikes:
            self.start.blank_box.rect.topleft = self.START_POSITIONS['stand_spikes'] # Replaces in Menu
            self.start.stand_spikes.rect.topleft = (self.mouse_pos[0]-(self.start.stand_spikes.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.stand_spikes.image.get_height()/2))
        else:
            self.start.stand_spikes.rect.topleft = self.START_POSITIONS['stand_spikes']       
    def play_mode_function(self):
        # Avoid player going off screen
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_LEFT]:
            self.play_player.last_pressed_r = 0
            if self.play_player.rect.left > 0:
                self.play_player.go_left()
            else:
                self.play_player.stop()
        if keys_pressed[K_RIGHT]:
            self.play_player.last_pressed_r = 1
            if self.play_player.rect.right < SCREEN_WIDTH:
                self.play_player.go_right()
            else:
                self.play_player.stop()
        # Dead
        if self.play_player.rect.top > SCREEN_HEIGHT and self.play_player.speed_y >= 0:
            restart_level(self)
        # Spikes fall when player goes underneath
        if PlayFallSpikes.fall_spikes_list:
            for fall_spike in PlayFallSpikes.fall_spikes_list:
                if(self.play_player.rect.right > fall_spike.rect.left and
                   self.play_player.rect.left < fall_spike.rect.right and
                   self.play_player.rect.top > fall_spike.rect.bottom):
                    fall_spike.fall_var = 1
                if fall_spike.fall_var == 1:
                    fall_spike.rect.top = fall_spike.rect.top + 5
        # Player wins when he captures all jewels and enters door
        if PlayDoor.door_list:
            PlayDoor.door_list[0].image = PlayDoor.door_list[0].open_or_close(self.play_player.score, PlayDiamonds.diamonds_list)
            if pygame.sprite.collide_mask(self.play_player, PlayDoor.door_list[0]):
                if self.play_player.score == len(PlayDiamonds.diamonds_list):
                    print("You Win!")
                    self.play_player.death_count = 0
                    self.game_mode = self.EDIT_MODE
                    self.play_edit_switch_button.image = self.play_edit_switch_button.game_mode_button(self.game_mode)
                    #music_player = [MusicPlayer()]
                    self.play_player.rect.topleft = self.placed_player.rect.topleft
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
            if self.play_player.rect.colliderect(play_smily_robot.rect):
                if(self.play_player.rect.bottom <= play_smily_robot.rect.top + 10 and self.play_player.speed_y >= 0):
                    play_smily_robot.rect.topleft = PlaySmilyRobot.OUT_OF_PLAY_TOPLEFT
                    self.play_player.propeller = 0
                    self.play_player.speed_y = -4
                    self.play_player.jumps_left = 1 #Allows propeller in air
                elif(self.play_player.rect.right-play_smily_robot.rect.left <= 10 and
                     self.play_player.rect.bottom > play_smily_robot.rect.top + 10):
                    restart_level(self)
                elif(self.play_player.rect.left-play_smily_robot.rect.right <= 10 and
                     self.play_player.rect.bottom > play_smily_robot.rect.top + 10):
                    restart_level(self)
        for play_flyer in PlayFlyer.flyer_list:
            if self.play_player.rect.colliderect(play_flyer.rect):
                restart_level(self)
        for play_fall_spikes in PlayFallSpikes.fall_spikes_list:
            if self.play_player.rect.colliderect(play_fall_spikes.rect):
                restart_level(self)
        for play_stand_spikes in PlayStandSpikes.stand_spikes_list:
            if self.play_player.rect.colliderect(play_stand_spikes.rect):
                restart_level(self)
        for play_diamonds in PlayDiamonds.diamonds_list:
            if pygame.sprite.collide_mask(self.play_player, play_diamonds):
                self.play_player.score += 1
                play_diamonds.image = IMAGES["spr_blank_box"]
        for spring in PlaySpring.spring_list:
            if pygame.sprite.collide_mask(self.play_player, spring):
                if self.play_player.rect.bottom <= spring.rect.top+20 and self.play_player.speed_y >= 10: #big jumps
                    SOUNDS["snd_spring"].play()
                    self.play_player.propeller = 0 
                    self.play_player.rect.bottom = spring.rect.top
                    self.play_player.speed_y = -10
                    self.play_player.jumps_left = 1 #Allows propeller in air
                elif self.play_player.rect.bottom <= spring.rect.top+10 and self.play_player.speed_y >= 0:
                    SOUNDS["snd_spring"].play()
                    self.play_player.propeller = 0 #Fixes propeller bug
                    self.play_player.rect.bottom = spring.rect.top
                    self.play_player.speed_y = -10
                    self.play_player.jumps_left = 1 #Allows propeller in air
                elif self.play_player.speed_x > 0:
                    self.play_player.rect.right = spring.rect.left
                elif self.play_player.speed_x < 0:
                    self.play_player.rect.left = spring.rect.right
                elif self.play_player.speed_y < 0:
                    self.play_player.speed_y = 0
                    self.play_player.propeller = 0
                    self.play_player.rect.top = spring.rect.bottom #Below the wall
    def initiate_room(self):
        self.start.player.rect.topleft = self.START_POSITIONS['player']
        self.start.wall.rect.topleft = self.START_POSITIONS['wall']
        self.start.flyer.rect.topleft = self.START_POSITIONS['flyer']
        self.start.reverse_wall.rect.topleft = self.START_POSITIONS['reverse_wall']
        self.start.spring.rect.topleft = self.START_POSITIONS['spring']
        self.start.smily_robot.rect.topleft = self.START_POSITIONS['smily_robot']
        self.start.door.rect.topleft = self.START_POSITIONS['door']
        self.start.diamonds.rect.topleft = self.START_POSITIONS['diamonds']
        self.start.sticky_block.rect.topleft = self.START_POSITIONS['sticky_block']
        self.start.fall_spikes.rect.topleft = self.START_POSITIONS['fall_spikes']
        self.start.stand_spikes.rect.topleft = self.START_POSITIONS['stand_spikes']

# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions(game_state):
    # Handle player separately
    player_position = []
    if game_state.placed_player is not None:
        player_position = [game_state.placed_player.rect.topleft]

    # Dictionary for all other objects except player
    total_placed_list = {
        'door': PlacedDoor.door_list,
        'wall': PlacedWall.wall_list,
        'flyer': PlacedFlyer.flyer_list,
        'reverse_wall': PlacedReverseWall.reverse_wall_list,
        'spring': PlacedSpring.spring_list,
        'smily_robot': PlacedSmilyRobot.smily_robot_list,
        'diamonds': PlacedDiamonds.diamonds_list,
        'sticky_block': PlacedStickyBlock.sticky_block_list,
        'fall_spikes': PlacedFallSpikes.fall_spikes_list,
        'stand_spikes': PlacedStandSpikes.stand_spikes_list
    }

    # Initialize the dictionary for storing object positions
    get_rect_for_all_obj = {'player': player_position}

    # Loop through all lists of placed objects (except player)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = [item.rect.topleft for item in item_list]
        get_rect_for_all_obj[item_key] = item_list_in_name

    return get_rect_for_all_obj

def remove_all_placed(game_state):
    for spr_list in [PlacedWall.wall_list, PlacedFlyer.flyer_list,
                     PlacedReverseWall.reverse_wall_list, PlacedSpring.spring_list, PlacedSmilyRobot.smily_robot_list,
                     PlacedDoor.door_list, PlacedDiamonds.diamonds_list, PlacedStickyBlock.sticky_block_list,
                     PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    game_state.placed_player.kill()
    game_state.placed_player = None
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

def remove_all_play(game_state):
    for spr_list in [PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    game_state.play_player.kill()
    game_state.play_player = None
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

def restart_level(game_state):
    for spr_list in [PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.restart()
    game_state.play_player.restart()

def main():
    # Tk box for color
    if not MOBILE_ACCESSIBILITY_MODE:
        ROOT = tk.Tk()
        ROOT.withdraw()

    MENUON = 1
    load_all_assets()
    
    game_state = GameState()

    COLORKEY = [160, 160, 160]
    
    debug_message = False
    
    #Fonts
    FONT_ARIAL = pygame.font.SysFont('Arial', 24)

    
    #Backgrounds
    START_MENU = pygame.image.load("sprites/start_menu.png").convert()
    START_MENU = pygame.transform.scale(START_MENU, (SCREEN_WIDTH, SCREEN_HEIGHT))
    INFO_SCREEN = pygame.image.load("sprites/info_screen.bmp").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    #MUSIC_PLAYER = [MusicPlayer()]
    
    # Creating grid on main area
    create_grids_in_game_world(game_state, 
                               SCREEN_WIDTH, 
                               SCREEN_HEIGHT, 
                               GameState.GRID_SPACING, 
                               GameState.TOP_UI_BOUNDARY_Y_HEIGHT)
    
    while GameState.STATE == GameState.RUNNING:
        clock.tick(FPS)
        game_state.update_mouse_pos()
        
        if GameState.STATE == GameState.RUNNING and MENUON == 1: # Initiate room
            game_state.initiate_room()
            game_state.handle_events()

            ##################
            # ALL EDIT ACTIONS
            ##################
            if game_state.game_mode == game_state.EDIT_MODE:
                game_state.edit_mode_function()
                    
            ##################
            # IN-GAME ACTIONS
            ##################
            if game_state.game_mode == game_state.PLAY_MODE:
                game_state.play_mode_function()
                

            #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
            
            SCREEN.fill(COLORKEY)

            #Update all sprites
            game_state.start_sprites.update()
            game_state.placed_sprites.update()
            game_state.play_sprites.update()
            game_state.game_mode_sprites.draw(SCREEN)
            if game_state.game_mode == game_state.EDIT_MODE: #Only draw placed sprites in editing mode
                if game_state.grid_button.grid_on_var:
                    game_state.grid_sprites.draw(SCREEN)
                game_state.start_sprites.draw(SCREEN)
                game_state.placed_sprites.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("", 1, (0, 0, 0))
            elif game_state.game_mode == game_state.PLAY_MODE: #Only draw play sprites in play mode
                game_state.play_sprites.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("Deaths: " + str(game_state.play_player.death_count), 1, (0, 0, 0))
            SCREEN.blit(DEATH_COUNT_TEXT, ((SCREEN_WIDTH/2-50), 5))

            pygame.display.update()
        elif MENUON == 2: # Info SCREEN in a WHILE loop
            InfoScreen(INFO_SCREEN, SCREEN)
            MENUON = 1
        elif GameState.STATE == GameState.DEBUG:
            if debug_message == True:
                print("Entering debug mode")
                # USE BREAKPOINT HERE
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = False
                        state = GameState.STATE
        
if __name__ == "__main__":
    main()